import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import tweepy

# -----------------------------
# CONSTANTS
# -----------------------------
API_KEY = "c31a6eec-7d5b-43cf-be21-735f14902a97"
JOSH_HART_ID = 322
KNICKS_ID = 20
BASE_URL = "https://api.balldontlie.io/v1"

# -----------------------------
# AUTH GET
# -----------------------------
def api_get(endpoint, params=None):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=headers)

    print(f"[DEBUG] GET {resp.url} -> {resp.status_code}")

    resp.raise_for_status()
    return resp.json()

# -----------------------------
# DATE (NY TIME)
# -----------------------------
def get_today_ny():
    forced = os.getenv("FORCE_DATE")
    if forced:
        print(f"[DEBUG] Using FORCE_DATE override: {forced}")
        return forced

    # today = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    today = "2024-11-30"
    print(f"[DEBUG] NY Today = {today}")
    return today

# -----------------------------
# GAME LOOKUP
# -----------------------------
def get_todays_knicks_game():
    today = get_today_ny()

    data = api_get(
        "games",
        {
            "team_ids[]": KNICKS_ID,
            "dates[]": today,
        },
    )

    print(f"[DEBUG] Games returned: {len(data['data'])}")

    return data["data"][0] if data["data"] else None

# -----------------------------
# PLAYER STATS
# -----------------------------
def get_josh_hart_stats(game_id):
    data = api_get(
        "stats",
        {
            "game_ids[]": game_id,
            "player_ids[]": JOSH_HART_ID,
        },
    )

    print(f"[DEBUG] Stats returned: {len(data['data'])}")

    return data["data"][0] if data["data"] else None

# -----------------------------
# CHECKS
# -----------------------------
def is_game_final(game):
    status = game.get("status")
    print(f"[DEBUG] Game status = {status}")
    return status == "Final"

def is_triple_double(stats):
    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)
    stl = stats.get("stl", 0)
    blk = stats.get("blk", 0)

    categories = [pts, reb, ast, stl, blk]
    achieved = sum(v >= 10 for v in categories)

    print(f"[DEBUG] Category counts >=10: {achieved}")

    return achieved >= 3

# -----------------------------
# TWEET FORMAT (YOUR EXACT FORMAT)
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
# SEND TWEET
# -----------------------------
def send_tweet(text):
    print("[DEBUG] Attempting to tweet...")

    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )
    resp = client.create_tweet(text=text)

    print(f"[DEBUG] Tweet response: {resp}")

# -----------------------------
# MAIN
# -----------------------------
def main():
    print("=== Josh Hart Triple Double Bot Started ===")

    game = get_todays_knicks_game()
    if not game:
        print("[DEBUG] No game found today.")
        return

    if not is_game_final(game):
        print("[DEBUG] Game not final yet.")
        return

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        print("[DEBUG] No stats yet.")
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)

    print("[DEBUG] Final tweet text:")
    print(tweet_text)

    send_tweet(tweet_text)


if __name__ == "__main__":
    main()
