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
    return game.get("status") == "Fin
