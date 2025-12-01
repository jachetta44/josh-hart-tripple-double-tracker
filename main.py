import requests
from datetime import date
import os
import tweepy

# -----------------------------
# Constants
# -----------------------------
JOSH_HART_ID = 322     # balldontlie player ID
KNICKS_ID = 20         # Knicks team ID

# -----------------------------
# API CALLS
# -----------------------------

def get_knicks_game():
    """Return today's Knicks game if it exists."""
    today = date.today().isoformat()
    url = f"https://www.balldontlie.io/api/v1/games?team_ids[]={KNICKS_ID}&dates[]={today}"
    r = requests.get(url).json()
    return r["data"][0] if r["data"] else None


def get_josh_hart_stats(game_id):
    """Return Josh Hart's stats for this game."""
    url = f"https://www.balldontlie.io/api/v1/stats?game_ids[]={game_id}&player_ids[]={JOSH_HART_ID}"
    r = requests.get(url).json()
    return r["data"][0] if r["data"] else None


# -----------------------------
# LOGIC
# -----------------------------

def is_game_final(game):
    """Return True if the game has completed."""
    return game.get("status") == "Final"


def is_triple_double(stats):
    """Check if Josh Hart got a triple-double."""
    pts = stats["pts"]
    reb = stats["reb"]
    ast = stats["ast"]
    stl = stats["stl"]
    blk = stats["blk"]

    categories = [pts, reb, ast, stl, blk]
    return sum(1 for v in categories if v >= 10) >= 3


def format_tweet(stats, triple):
    """Create message text for the tweet."""
    if not triple:
        return (
            "Josh Hart did not record a triple-double tonight.\n\n"
            f"PTS: {stats['pts']}  REB: {stats['reb']}  AST: {stats['ast']}\n"
            f"STL: {stats['stl']}  BLK: {stats['blk']}\n"
            "#Knicks"
        )

    return (
        "🚨🚨JOSH HART TRIPLE-DOUBLE ALERT🚨🚨\n\n"
        f"✅Points:   {stats['pts']}\n"
        f"✅Rebounds: {stats['reb']}\n"
        f"✅Assists:  {stats['ast']}\n"
        f"Steals:   {stats['stl']}\n"
        f"Blocks:   {stats['blk']}\n\n"
        "🟠🔵 #Knicks 🟠🔵"
    )


# -----------------------------
# TWEET
# -----------------------------

def tweet(text):
    """Send the tweet via X API."""
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )
    client.create_tweet(text=text)


# -----------------------------
# MAIN
# -----------------------------

def main():
    game = get_knicks_game()
    if not game:
        return  # Knicks didn't play today

    if not is_game_final(game):
        return  # Game isn't final yet

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        return  # Stats not available yet

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)
    tweet(tweet_text)


if __name__ == "__main__":
    main()
