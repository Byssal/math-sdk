from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from game_events import tile_multipliers_event
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def get_clusters_update_wins(self):
        """Find clusters on board, draw random tile multipliers, and update win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {
            "totalWin": 0,
            "wins": [],
        }
        self.board, self.win_data = self.evaluate_clusters_with_random_mult(
            config=self.config,
            board=self.board,
            clusters=clusters,
            mult_values=self.config.mult_values[self.gametype],
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )

        Cluster.record_cluster_wins(self)
        tile_multipliers_event(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
