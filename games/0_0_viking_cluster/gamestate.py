from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Core function handling simulation results."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            # reset_book resets the multiplier grid, so in the base game it is fresh each spin.
            self.reset_book()
            self.draw_board()

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            # A winning connection raises the grid multipliers for the NEXT connections.
            self.update_grid_mults()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_grid_mults()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()  # global multiplier starts at 0 (bumped to 1 on spin 1)
        # Ragnarok (5 scatters) starts each free spin's grid pre-filled at x4.
        grid_start = (
            self.config.ragnarok_grid_start if getattr(self, "bonus_type", None) == "ragnarok" else 0
        )
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            # Top global multiplier grows every free spin (x1, x2, x3, ...).
            self.update_global_mult()
            # Fresh grid each free spin; Ragnarok gives a x4 head start on all tiles.
            self.reset_grid_mults(grid_start)
            if grid_start > 0:
                self.emit_grid()

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            self.update_grid_mults()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
                self.update_grid_mults()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
