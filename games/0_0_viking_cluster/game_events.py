UPDATE_GRID = "updateGrid"


def tile_multipliers_event(gamestate):
    """Announce random rune multipliers landed this win, as a full reel x row
    grid (matches the web-sdk cluster app's existing MultiplierGrid component)."""
    tile_multipliers = gamestate.win_data.get("tileMultipliers", [])
    if tile_multipliers:
        grid = [[0 for _ in range(gamestate.config.num_rows[reel])] for reel in range(gamestate.config.num_reels)]
        for tile in tile_multipliers:
            grid[tile["reel"]][tile["row"]] = tile["value"]

        event = {
            "index": len(gamestate.book.events),
            "type": UPDATE_GRID,
            "gridMultipliers": grid,
        }
        gamestate.book.add_event(event)
