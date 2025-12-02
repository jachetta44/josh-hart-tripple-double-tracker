import requests
from datetime import datetime
import pytz
import os
import tweepy

# -----------------------------
# Constants
# -----------------------------
API_KEY = os.getenv("BALLDONTLIE_KEY")
JOSH_HART_ID = 322  # balldontlie player ID

HEADERS = {"Authorization": API_KEY}


# -----------------------------
# API CALLS
# -----------------------------
def fetch_stats_for_today():
    """Return Josh Hart's stats for today's date."""
    est = pytz.timezone("America/New_York")
    today = datetime.now(est).strftime("%Y-%m-%d")

    url = "https://api.balldontlie.io/v1/stats"
    params = {
        "player_ids[]": JOSH_HART_ID,
        "dates[]": today
    }

    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data["data"][0] if data["data"] else None


# -----------------------------
# LOGIC
# -----------------------------
def is_triple_double(stats):
    pts = stats["pts"]
    reb = stats["reb"]
    ast = stats["ast"]
    stl = stats["stl"]
    blk = stats["blk"]
    return sum(v >= 10 for v in [pts, reb, ast, stl, blk]) >= 3


def format_tweet(stats, triple):
    def mark(v):
        return f"✅ {v}" if v >= 10 else f"❌ {v}"

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
        "😔 Josh Hart did NOT record a triple-double tonight.\n\n"
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
    stats = fetch_stats_for_today()
    if not stats:
        print("No Josh Hart stats today — Knicks didn't play.")
        return

    # Extract game information from stat block
    game = stats["game"]
    if game["status"] != "Final":
        print(f"Game not final yet: status = {game['status']}")
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)
    tweet(tweet_text)
    print("Tweet sent!")


if __name__ == "__main__":
    main()
