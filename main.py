from balldontlie import BalldontlieAPI
import tweepy
import os

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "c31a6eec-7d5b-43cf-be21-735f14902a97"
JOSH_HART_ID = 322
KNICKS_ID = 20

# Hardcoded test date
TEST_DATE = "2024-11-30"

api = BalldontlieAPI(api_key=API_KEY)

# -----------------------------
# FETCH GAME FOR 11/30
# -----------------------------
def get_knicks_game_1130():
    games = api.nba.games.list(
        team_ids=[KNICKS_ID],
        dates=[TEST_DATE],
        per_page=10
    )
    return games["data"][0] if games.get("data") else None

# -----------------------------
# FETCH JOSH HART STATS
# -----------------------------
def get_josh_hart_stats(game_id):
    stats = api.nba.stats.list(
        game_ids=[game_id],
        player_ids=[JOSH_HART_ID],
        per_page=5
    )
    return stats["data"][0] if stats.get("data") else None

# -----------------------------
# TRIPLE DOUBLE LOGIC
# -----------------------------
def is_triple_double(stats):
    pts = stats.get("pts", 0)
    reb = stats.get("reb", 0)
    ast = stats.get("ast", 0)
    stl = stats.get("stl", 0)
    blk = stats.get("blk", 0)

    categories = [pts, reb, ast, stl, blk]
    return sum(v >= 10 for v in categories) >= 3

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
# MAIN
# -----------------------------
def main():
    print("=== TEST MODE: 11/30 JOSH HART GAME ===")

    game = get_knicks_game_1130()
    if not game:
        print("[ERROR] No Knicks game found for 11/30.")
        return

    print(f"[DEBUG] Found game: ID={game['id']} | Status={game['status']}")

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        print("[ERROR] No stats for Josh Hart found.")
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)

    print("\n=== GENERATED TWEET ===")
    print(tweet_text)
    print("\n(No tweet sent in test mode.)")

if __name__ == "__main__":
    main()
