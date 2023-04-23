import requests

def get_match_history(api_key, steam_id):
    url = f"https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1?key={api_key}&account_id={steam_id}"
    
    response = requests.get(url)
    return response.json()

def get_user_stats(api_key, steam_id, game_key):
    url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={game_key}&key={api_key}&steamid={steam_id}"
    
    response = requests.get(url)
    return response.json()