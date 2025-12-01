import requests
from datetime import date
import os
import tweepy

JOSH_HART_ID = 322
KNICKS_ID = 20

def get_knicks_game():
    today = date.today().isoformat()
    url = f"https://www.balldontlie.io/api/v1/games?team_ids[]={KNICKS_ID}&dates[]={today}"
    r = requests.get(url).json()
    return r["data"][0] if r["data"] else None

def get_josh_hart_stats(game_id):
    url = f"https://www.balldontlie.io/api/v1/stats?game_ids[]={game_id}&player_ids[]={JOSH_HART_ID}"
    r = requests.get(url).json()
    return r["data"][0] if r["data"] else None

def is_triple_double(stats):
    c = stats
    cats = [c["pts"], c["reb"], c["ast"], c["stl"], c["blk"]]
    return sum(1 for v in cats if v >= 10) >= 3

def format_tweet(stats, triple):
    if not triple:
        return "Josh Hart did **not** record a triple-double tonight."

    return (
        f"Josh Hart Triple-Double Alert! 🔵🟠\n\n"
        f"Points: {stats['pts']}\n"
        f"Rebounds: {stats['reb']}\n"
        f"Assists: {stats['ast']}\n"
        f"Steals: {stats['stl']}\n"
        f"Blocks: {stats['blk']}\n\n"
        f"#Knicks"
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
    game = get_knicks_game()
    if not game:
        return

    stats = get_josh_hart_stats(game["id"])
    if not stats:
        return

    triple = is_triple_double(stats)
    tweet_text = format_tweet(stats, triple)
    tweet(tweet_text)

if __name__ == "__main__":
    main()

