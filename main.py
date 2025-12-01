import requests
from datetime import datetime
import os
import tweepy
import pytz  # for Eastern Time conversion

# -----------------------------
# Constants
# -----------------------------
JOSH_HART_ID = 322     # balldontlie player ID
KNICKS_ID = 20         # Knicks team ID

# -----------------------------
# API CALLS
# -----------------------------

BALLEDONTLIE_API_KEY = os.getenv("BALLEDONTLIE_API_KEY")

def get_knicks_game():
    """Return today's Knicks game if it exists."""
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).date().isoformat()
    url = f"https://www.balldontlie.io/api/v1/games?team_ids[]={KNICKS_ID}&dates[]={today}"
    headers = {"Authorization": BALLEDONTLIE_API_KEY} if BALLEDONTLIE_API_KEY else {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching game:", e)
        return None
    except ValueError as e:
        print("Error decoding game JSON:", e)
        print("Raw response:", response.text)
        return None

    return data.get("data")[0] if data.get("data") else None


def get_josh_hart_stats(game_id):
    """Return Josh Hart's stats for this game."""
    url = f"https://www.balldontlie.io/api/v1/stats?game_ids[]={game_id}&player_ids[]={JOSH_HART_ID}"
    headers = {"Authorization": BALLEDONTLIE_API_KEY} if BALLEDONTLIE_API_KEY else {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching stats:", e)
        return None
    except ValueError as e:
        print("Error decoding stats JSON:", e)
        print("Raw response:", response.text)
        return None

    return data.get("data")[0] if data.get("data") else None

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
    """Create tweet text for triple-double or non-triple-double nights."""

    # helper: checkmark if >=10 else X
    def mark(value):
        return f"✅ {value}" if value >= 10 else f"❌ {value}"

    pts = stats["pts"]
    reb = stats["reb"]
    ast = stats["ast"]
    stl = stats["stl"]
    blk = stats["blk"]

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
    # Optional TEST MODE: force a tweet without needing a real game
    if os.getenv("TEST_MODE") == "1":
        print("TEST MODE: sending test tweet")
        tweet("🚨 Test tweet from Josh Hart bot — credentials working! 🚨")
        return

    game = get_knicks_game()
    if not game:
        print("No Knicks game found today or data not yet available.")
        return

    if not is_game_final(game):
        print("Game not final yet. Exiting.")
        return

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        print("Stats not available yet. Exiting.")
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)
    print("Sending tweet:")
    print(tweet_text)
    tweet(tweet_text)


if __name__ == "__main__":
    main()
