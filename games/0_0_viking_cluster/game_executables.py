from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from game_events import update_grid_mult_event
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def reset_grid_mults(self, start_value: int = 0):
        """Initialize all grid position multipliers to start_value (0 normally,
        4 for the Ragnarok tier)."""
        self.position_multipliers = [
            [start_value for _ in range(self.config.num_rows[reel])] for reel in range(self.config.num_reels)
        ]

    def emit_grid(self):
        """Send the current grid to the frontend (used to show a pre-filled grid)."""
        update_grid_mult_event(self)

    def update_grid_mults(self):
        """A winning cluster raises the multiplier on its tiles: 0 -> 1 on the first
        win there, then +1 on every further win at that tile (capped). This boosts the
        NEXT connections on those tiles."""
        if self.win_data["totalWin"] > 0:
            for win in self.win_data["wins"]:
                for pos in win["positions"]:
                    if self.position_multipliers[pos["reel"]][pos["row"]] == 0:
                        self.position_multipliers[pos["reel"]][pos["row"]] = 1
                    else:
                        self.position_multipliers[pos["reel"]][pos["row"]] = min(
                            self.position_multipliers[pos["reel"]][pos["row"]] + 1,
                            self.config.maximum_board_mult,
                        )
            update_grid_mult_event(self)

    def get_clusters_update_wins(self):
        """Find clusters on board and update win manager (grid multiplier applied)."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {"totalWin": 0, "wins": []}
        self.board, self.win_data = self.evaluate_clusters_with_grid(
            config=self.config,
            board=self.board,
            clusters=clusters,
            pos_mult_grid=self.position_multipliers,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
