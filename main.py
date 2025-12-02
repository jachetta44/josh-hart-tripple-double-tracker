import requests
from datetime import date

API_KEY = "c31a6eec-7d5b-43cf-be21-735f14902a97"
BASE_URL = "https://api.balldontlie.io/v1"

JOSH_HART_ID = 322

def fetch_json(endpoint, params):
    params["api_key"] = API_KEY  # force key to always be included
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_games_for_date(target_date):
    return fetch_json("games", {"dates[]": target_date.isoformat()})

def get_player_stats(game_id):
    return fetch_json(
        "stats",
        {"game_ids[]": game_id, "player_ids[]": JOSH_HART_ID}
    )

def main():
    today = date.today()
    print("Checking games for:", today)

    games_data = get_games_for_date(today)
    games = games_data.get("data", [])

    if not games:
        print("No games today.")
        return

    for game in games:
        print("Found game:", game["id"])
        stats = get_player_stats(game["id"])
        print(stats)

if __name__ == "__main__":
    main()
