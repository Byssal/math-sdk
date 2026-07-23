TILE_MULTIPLIERS = "tileMultipliers"


def tile_multipliers_event(gamestate):
    """Announce which board positions got a random rune multiplier this win."""
    tile_multipliers = gamestate.win_data.get("tileMultipliers", [])
    if tile_multipliers:
        event = {
            "index": len(gamestate.book.events),
            "type": TILE_MULTIPLIERS,
            "tileMultipliers": tile_multipliers,
        }
        gamestate.book.add_event(event)
