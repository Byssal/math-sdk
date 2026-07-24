from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


class GameCalculations(Executables):
    """
    Overrides evaluate_clusters() to account for the accumulating multiplier grid:
    a cluster's win is multiplied by the sum of the grid multipliers on its tiles.
    """

    def evaluate_clusters_with_grid(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        pos_mult_grid: list,
        global_multiplier: int = 1,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> type:
        """Determine payout, multiplying each cluster by the summed grid multiplier
        on its winning tiles (min 1) and the global multiplier."""
        exploding_symbols = []
        total_win = 0
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) in config.paytable:
                    board_mult = 0
                    for positions in cluster:
                        board_mult += pos_mult_grid[positions[0]][positions[1]]
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
                        if {"reel": positions[0], "row": positions[1]} not in exploding_symbols:
                            exploding_symbols.append({"reel": positions[0], "row": positions[1]})

        return_data["totalWin"] += total_win
        return board, return_data
