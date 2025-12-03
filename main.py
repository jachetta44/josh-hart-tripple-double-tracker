import requests
from datetime import datetime
import os
import tweepy

API_KEY = "c31a6eec-7d5b-43cf-be21-735f14902a97"
JOSH_HART_ID = 322
KNICKS_ID = 20

BASE_URL = "https://api.balldontlie.io/v1"

# -----------------------------
# Helper – authenticated GET
# -----------------------------
def api_get(endpoint, params=None):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()


# -----------------------------
# GET TODAY'S GAME
# -----------------------------
def get_todays_knicks_game():
    today = datetime.today().strftime("%Y-%m-%d")

    data = api_get(
        "games",
        {
            "team_ids[]": KNICKS_ID,
            "dates[]": today,
        },
    )

    return data["data"][0] if data["data"] else None


# -----------------------------
# GET JOSH HART'S STATS
# -----------------------------
def get_josh_hart_stats(game_id):
    data = api_get(
        "stats",
        {
            "game_ids[]": game_id,
            "player_ids[]": JOSH_HART_ID,
        },
    )

    return data["data"][0] if data["data"] else None


# -----------------------------
# CHECKS
# -----------------------------
def is_game_final(game):
    return game.get("status") == "Final"


def is_triple_double(stats):
    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)
    stl = stats.get("stl", 0)
    blk = stats.get("blk", 0)

    categories = [pts, reb, ast, stl, blk]
    return sum(v >= 10 for v in categories) >= 3


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
# TWEET SENDER
# -----------------------------
def send_tweet(text):
    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )

    print("DEBUG KEYS:")
    print("X_API_KEY:", bool(os.getenv("X_API_KEY")))
    print("X_API_SECRET:", bool(os.getenv("X_API_SECRET")))
    print("X_ACCESS_TOKEN:", bool(os.getenv("X_ACCESS_TOKEN")))
    print("X_ACCESS_SECRET:", bool(os.getenv("X_ACCESS_SECRET")))

    try:
        response = client.create_tweet(text=text)
        print("Tweet response:", response)
    except Exception as e:
        print("Tweet failed:", e)


# -----------------------------
# MAIN
# -----------------------------
def main():
    game = get_todays_knicks_game()
    if not game:
        return

    if not is_game_final(game):
        return

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)
    send_tweet(tweet_text)


if __name__ == "__main__":
    main()
