import os
from datetime import datetime
from balldontlie import BalldontlieAPI

TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

# Get API key from GitHub Actions env
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
if not BALLDONTLIE_API_KEY:
    raise ValueError("Missing BALLDONTLIE_API_KEY environment variable.")

api = BalldontlieAPI(api_key=BALLDONTLIE_API_KEY)


# ---------------------------
# Hardcoded test for 11/30/24
# ---------------------------
def get_knicks_game_1130():
    print("=== TEST MODE: Pulling Knicks Game for 11/30 ===")
    games = api.nba.games.get(
        team_ids=[20],        # Knicks
        dates=["2024-11-30"]  # Hardcoded test date
    )
    
    print("Returned:", games.data)
    return games.data[0] if len(games.data) > 0 else None


# ---------------------------
# YOUR ORIGINAL TWEET FORMATTING
# ---------------------------
def format_tweet(stats, triple):
    def mark(v): 
        return f"✅ {v}" if v >= 10 else f"❌ {v}"

    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)
    stl = stats.get("stl", 0)
    blk = stats.get("blk", 0)

    if triple:
        return (
            "🚨🚨 JOSH HART TRIPLE-DOUBLE ALERT 🚨🚨\n\n"
            f"{mark(pts)} Points\n"
            f"{mark(reb)} Rebounds\n"
            f"{mark(ast)} Assists\n"
            f"Steals: {stl}\n"
            f"Blocks: {blk}\n\n"
            "🟠🔵 #Knicks 🟠🔵"
        )
    else:
        return (
            "😭😭 Josh Hart did not record a triple-double tonight 😭😭\n\n"
            f"{mark(pts)} Points\n"
            f"{mark(reb)} Rebounds\n"
            f"{mark(ast)} Assists\n"
            f"Steals: {stl}\n"
            f"Blocks: {blk}\n\n"
            "🟠🔵 #Knicks 🟠🔵"
        )


# ---------------------------
# Main Logic
# ---------------------------
def main():
    if TEST_MODE:
        print("=== TEST MODE ENABLED ===")
        game = get_knicks_game_1130()
    else:
        print("LIVE MODE NOT CONFIGURED HERE YET")
        return

    if not game:
        print("No game found.")
        return

    # Pull stats for Josh Hart (player_id = 354717)
    stats_response = api.nba.stats.get(
        game_ids=[game.id],
        player_ids=[354717]
    )

    stats_list = stats_response.data
    if not stats_list:
        print("No Josh Hart stats found.")
        return

    stats = stats_list[0]

    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)

    triple = pts >= 10 and reb >= 10 and ast >= 10

    tweet_text = format_tweet(stats, triple)

    print("Tweet:\n", tweet_text)

    if not TEST_MODE:
        tweet_now(tweet_text)


# Mock tweet (prevents tweeting in test mode)
def tweet_now(text):
    print("[TWEET SENT]", text)


if __name__ == "__main__":
    main()
