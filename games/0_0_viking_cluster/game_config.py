"""Viking cluster game configuration file/setup"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton Viking cluster game configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_viking_cluster"
        self.provider_number = 0
        self.working_name = "Viking Cluster Raid"
        self.wincap = 5000.0
        self.win_type = "cluster"
        self.rtp = 0.9670
        self.construct_paths()

        # Game Dimensions: 5 reels (columns) x 6 rows = 30 cells
        self.num_reels = 5
        self.num_rows = [6] * self.num_reels

        # Board and Symbol Properties.
        # H1-H4: Mjolnir (Thor's hammer), horned helmet, battle axe, rune shield.
        # L1-L4: four rune-stone colors. W: Viking longship (wild). S: Valknut (scatter).
        # Top tier max (30) matches num_reels*num_rows so a full-board cluster never pays zero.
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 14), (15, 30)
        pay_group = {
            (t1, "H1"): 6.0,
            (t2, "H1"): 15.0,
            (t3, "H1"): 30.0,
            (t4, "H1"): 75.0,
            (t1, "H2"): 2.5,
            (t2, "H2"): 6.0,
            (t3, "H2"): 12.0,
            (t4, "H2"): 45.0,
            (t1, "H3"): 1.6,
            (t2, "H3"): 4.0,
            (t3, "H3"): 8.0,
            (t4, "H3"): 32.0,
            (t1, "H4"): 1.2,
            (t2, "H4"): 3.0,
            (t3, "H4"): 6.5,
            (t4, "H4"): 22.0,
            (t1, "L1"): 0.7,
            (t2, "L1"): 1.8,
            (t3, "L1"): 4.5,
            (t4, "L1"): 12.0,
            (t1, "L2"): 0.5,
            (t2, "L2"): 1.4,
            (t3, "L2"): 3.8,
            (t4, "L2"): 9.0,
            (t1, "L3"): 0.3,
            (t2, "L3"): 1.0,
            (t3, "L3"): 3.0,
            (t4, "L3"): 6.0,
            (t1, "L4"): 0.2,
            (t2, "L4"): 0.6,
            (t3, "L4"): 2.0,
            (t4, "L4"): 4.5,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"]}

        # 3-tier scatter bonus: 3 = Raid (common), 4 = Expedition (better odds),
        # 5 = Ragnarok (ultra rare, huge bonus). Keys double as free-spin counts.
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 10, 5: 15},
            self.freegame_type: {3: 5, 4: 8, 5: 12},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        self.bonus_tier_names = {3: "raid", 4: "expedition", 5: "ragnarok"}

        # Multiplier grid: a winning cluster raises the multiplier on each of its
        # tiles (0->1 on first win there, then +1 on every further win at that tile).
        # A cluster's win is multiplied by the sum of the grid values on its tiles.
        # In the base game the grid resets each spin; during free spins it PERSISTS
        # across all spins, so multipliers stack up over the bonus.
        self.maximum_board_mult = 512

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        mode_maxwins = {"base": 5000, "bonus": 5000}

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["base"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 10, 4: 4, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=200,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["bonus"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 10, 4: 4, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
