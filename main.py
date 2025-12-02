from datetime import datetime
import tweepy
from balldontlie import BalldontlieAPI

# -----------------------------
# CONSTANTS
# -----------------------------
API_KEY = "c31a6eec-7d5b-43cf-be21-735f14902a97"
JOSH_HART_ID = 322
KNICKS_ID = 20

api = BalldontlieAPI(api_key=API_KEY)

# -----------------------------
# FETCH GAME + STATS
# -----------------------------

def get_todays_knicks_game():
    """Returns today's Knicks game object, or None."""
    today = datetime.today().strftime("%Y-%m-%d")

    games = api.nba.games.list(
        dates=[today],
        team_ids=[KNICKS_ID]
    )

    return games.data[0] if games.data else None


def get_josh_hart_stats(game_id):
    """Return stats object for Josh Hart for this game, or None."""
    stats = api.nba.stats.list(
        game_ids=[game_id],
        player_ids=[JOSH_HART_ID]
    )
    return stats.data[0] if stats.data else None

# -----------------------------
# CHECKS
# -----------------------------

def is_game_final(game):
    """balldontlie uses 'Final' when game is finished."""
    return game.get("status") == "Final"


def is_triple_double(stats):
    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)
    stl = stats.get("stl", 0)
    blk = stats.get("blk", 0)

    categories = [pts, reb, ast, stl, blk]
    return sum(1 for v in categories if v >= 10) >= 3

# -----------------------------
# TWEET FORMATTING
# -----------------------------

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

# -----------------------------
# TWEET
# -----------------------------

def send_tweet(text):
    """Send tweet using OAuth1 Tweepy (API v1.1)."""
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )
    client.create_tweet(text=text)

# -----------------------------
# MAIN LOGIC
# -----------------------------

def main():
    game = get_todays_knicks_game()
    if not game:
        return  # No Knicks game today

    if not is_game_final(game):
        return  # Game still in progress

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        return  # Stats not available yet

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)

    send_tweet(tweet_text)


if __name__ == "__main__":
    main()
