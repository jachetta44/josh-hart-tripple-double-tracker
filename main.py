import os
import requests
from datetime import datetime
import tweepy
import pytz

# Constants
JOSH_HART_ID = 322
KNICKS_ID = 20
API_KEY = os.getenv("BALLEDONTLIE_API_KEY")

BASE_URL = "https://api.balldontlie.io/v1"

def fetch_json(path, params=None):
    headers = {"Authorization": API_KEY} if API_KEY else {}
    resp = requests.get(f"{BASE_URL}/{path}", params=params or {}, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_todays_knicks_game():
    est = pytz.timezone("US/Eastern")
    today = datetime.now(est).date().isoformat()
    # Try games endpoint
    data = fetch_json("games", {"team_ids[]": KNICKS_ID, "dates[]": today})
    games = data.get("data", [])
    if games:
        return games[0]
    # Fallback: check live box scores
    data = fetch_json("box_scores/live")
    for g in data.get("data", []):
        if g.get("home_team", {}).get("id") == KNICKS_ID or g.get("visitor_team", {}).get("id") == KNICKS_ID:
            return g
    return None

def get_player_stats(game_id):
    data = fetch_json("stats", {"game_ids[]": game_id, "player_ids[]": JOSH_HART_ID})
    stats = data.get("data", [])
    return stats[0] if stats else None

def is_triple(stats):
    cats = [stats.get("pts", 0), stats.get("reb", 0), stats.get("ast", 0), stats.get("stl", 0), stats.get("blk", 0)]
    return sum(1 for v in cats if v >= 10) >= 3

def format_tweet(stats, triple):
    def mark(v): return f"✅ {v}" if v >= 10 else f"❌ {v}"
    pts, reb, ast = stats.get("pts", 0), stats.get("reb", 0), stats.get("ast", 0)
    stl, blk = stats.get("stl", 0), stats.get("blk", 0)
    if triple:
        return (
            "🚨🚨 JOSH HART TRIPLE-DOUBLE ALERT 🚨🚨\n\n"
            f"{mark(pts)} Points\n{mark(reb)} Rebounds\n{mark(ast)} Assists\n"
            f"Steals: {stl}\nBlocks: {blk}\n\n🟠🔵 #Knicks 🟠🔵"
        )
    else:
        return (
            "😭😭 Josh Hart did not record a triple-double tonight 😭😭\n\n"
            f"{mark(pts)} Points\n{mark(reb)} Rebounds\n{mark(ast)} Assists\n"
            f"Steals: {stl}\nBlocks: {blk}\n\n🟠🔵 #Knicks 🟠🔵"
        )

def tweet(text):
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )
    client.create_tweet(text=text)

def main():
    if os.getenv("TEST_MODE") == "1":
        tweet("🚨 Test tweet — Bot is working. 🚨")
        return
    game = get_todays_knicks_game()
    if not game:
        print("No game found or data not available yet.")
        return
    # Attempt to find stats
    stats = get_player_stats(game.get("id"))
    if not stats:
        print("No stats yet. Exiting.")
        return
    triple = is_triple(stats)
    t = format_tweet(stats, triple)
    tweet(t)

if __name__ == "__main__":
    main()
