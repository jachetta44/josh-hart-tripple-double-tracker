import os
from datetime import datetime
from pyball import PyBall

TEST_MODE = True

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
if not BALLDONTLIE_API_KEY:
    raise ValueError("BALLDONTLIE_API_KEY is missing from environment variables!")

api = PyBall(api_key=BALLDONTLIE_API_KEY)

# ---------------------------
# Fetch Knicks game for 11/30 (test mode only)
# ---------------------------
def get_knicks_game_1130():
    """Specifically fetch the Knicks game on 11/30 from BallDontLie."""
    games = api.games.get(
        team_ids=[20],     # Knicks ID
        dates=["2024-11-30"]
    )

    # IMPORTANT: PaginatedListResponse uses `.data`, NOT dict access.
    if games.data and len(games.data) > 0:
        return games.data[0]
    return None


# ---------------------------
# Extract Josh Hart stats
# ---------------------------
def get_josh_hart_stats(game_id: int):
    """Return Josh Hart’s stat line for a single game."""
    stats = api.stats.get(
        player_ids=[362],  # Josh Hart ID
        game_ids=[game_id]
    )

    if not stats.data:
        return None

    return stats.data[0]


# ---------------------------
# Format message
# ---------------------------
def format_stat_message(stats):
    """Format a human-readable single-line update."""
    pts = stats.points
    reb = stats.rebounds
    ast = stats.assists

    td = (pts >= 10 and reb >= 10 and ast >= 10)

    if td:
        return f"Josh Hart recorded a triple-double tonight! ({pts} PTS, {reb} REB, {ast} AST)"
    else:
        return f"Josh Hart did NOT record a triple-double. ({pts} PTS, {reb} RBS, {ast} AST)"


# ---------------------------
# MAIN SCRIPT
# ---------------------------
def main():
    print("=== TEST MODE: 11/30 JOSH HART GAME ===" if TEST_MODE else "=== LIVE MODE ===")

    if TEST_MODE:
        game = get_knicks_game_1130()
    else:
        # In real mode you'd calculate "today" and fetch today's game
        raise NotImplementedError("Not coded yet for real-time mode.")

    if not game:
        print("No Knicks game found.")
        return

    game_id = game.id
    stats = get_josh_hart_stats(game_id)

    if not stats:
        print("No Josh Hart stats found for this game.")
        return

    message = format_stat_message(stats)
    print(message)


if __name__ == "__main__":
    main()
