from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.calculations.statistics import get_random_outcome
from src.config.config import Config


class GameCalculations(Executables):
    """
    Overrides evaluate_clusters() to draw a random multiplier (rune-stone) for
    each tile that takes part in a winning cluster, instead of a static grid.
    """

    def evaluate_clusters_with_random_mult(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        mult_values: dict,
        global_multiplier: int = 1,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> type:
        """
        Determine payout amount from cluster, drawing a random multiplier value
        for each winning tile (cached per-position so a tile shared by more than
        one cluster keeps a single drawn value within this evaluation pass).
        """
        exploding_symbols = []
        tile_multipliers = {}
        total_win = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) in config.paytable:
                    board_mult = 0
                    for positions in cluster:
                        if positions not in tile_multipliers:
                            tile_multipliers[positions] = get_random_outcome(mult_values)
                        board_mult += tile_multipliers[positions]
                    board_mult = max(board_mult, 1)
                    sym_win = config.paytable[(syms_in_cluster, sym)]
                    symwin_mult = sym_win * board_mult * global_multiplier
                    total_win += symwin_mult
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]

                    central_pos = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"] += [
                        {
                            "symbol": sym,
                            "clusterSize": syms_in_cluster,
                            "win": symwin_mult,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": board_mult,
                                "winWithoutMult": sym_win,
                                "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                            },
                        }
                    ]

                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True
                        if {
                            "reel": positions[0],
                            "row": positions[1],
                        } not in exploding_symbols:
                            exploding_symbols.append({"reel": positions[0], "row": positions[1]})

        return_data["totalWin"] += total_win
        return_data["tileMultipliers"] = [
            {"reel": pos[0], "row": pos[1], "value": value}
            for pos, value in tile_multipliers.items()
            if value > 1
        ]

        return board, return_data
