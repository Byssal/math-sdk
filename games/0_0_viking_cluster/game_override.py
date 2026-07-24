from game_executables import GameExecutables
from src.events.events import fs_trigger_event, enter_bonus_event


class GameStateOverride(GameExecutables):
    """
    This class is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        # Reset global values used across multiple projects
        super().reset_book()
        # Reset parameters relevant to local game only
        self.tumble_win = 0
        self.bonus_type = None
        # Base game: the multiplier grid is fresh every spin.
        self.reset_grid_mults()

    def reset_fs_spin(self):
        # Free spins: reset the grid ONCE at the start of the bonus so multipliers
        # persist (accumulate) across all free spins.
        super().reset_fs_spin()
        self.reset_grid_mults()

    def assign_special_sym_function(self):
        pass

    def check_repeat(self) -> None:
        """Checks if the spin failed a criteria constraint at any point."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not (self.triggered_freegame):
                self.repeat = True

            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True

    def _capped_scatter_tier(self, scatter_key: str = "scatter") -> int:
        """Scatter counts above the top defined tier (5 = ragnarok) still award
        the top tier rather than crashing on an undefined trigger key."""
        scatter_count = self.count_special_symbols(scatter_key)
        top_tier = max(self.config.freespin_triggers[self.gametype].keys())
        return min(scatter_count, top_tier)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial spin count, tag which Viking bonus tier was hit (raid /
        expedition / ragnarok based on scatter count), and transmit events."""
        tier = self._capped_scatter_tier(scatter_key)
        self.tot_fs = self.config.freespin_triggers[self.gametype][tier]
        self.bonus_type = self.config.bonus_tier_names.get(tier, "raid")

        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)
        enter_bonus_event(self)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Update total freespin amount on retrigger (same tier-capping as initial trigger)."""
        tier = self._capped_scatter_tier(scatter_key)
        self.tot_fs += self.config.freespin_triggers[self.gametype][tier]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
