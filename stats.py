import json

class PlayerStats:
    def __init__(self):
        self.steamID = None
        self.gameName = None
        
        self.all_stats = {}
        self.last_match_stats = {}
        self.other_stats = {}

    def from_json(self, json_str):
        try:
            data = json.loads(json_str)
        except TypeError:
            data = json_str

        playerstats = data["playerstats"]
        self.steamID = playerstats["steamID"]
        self.gameName = playerstats["gameName"]

        for stat in data["playerstats"]["stats"]:
            stat_name = stat["name"]
            stat_value = stat["value"]

            self.all_stats[stat_name] = stat_value

            if stat_name.startswith("last_match_"):
                self.last_match_stats[stat_name] = stat_value
            else:
                self.other_stats[stat_name] = stat_value
        return self
    
    def __str__(self):
        attributes = [f"{attr}: {getattr(self, attr)}" for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        return "\n".join(attributes)
    
    def get_most_wins_map(self):
        map_wins = {attr: getattr(self, attr) for attr in dir(self) if attr.startswith("total_wins_map")}
        if map_wins:
            return max(map_wins, key=map_wins.get)
        return None
    
    # def get_most_kills_with_weapon(self):
    #     total_kills = {attr: getattr(self, attr) for attr in dir(self) if attr.startswith("total_kills_map")}
    #     if total_kills:
    #         return max(total_kills, key=total_kills.get)
    #     return None
    
    # def get_most_hits_with_weapon(self):
    #     most_hits = {attr: getattr(self, attr) for attr in dir(self) if attr.startswith("total_hits")}
    #     if most_hits:
    #         return max(most_hits, key=most_hits.get)
    #     return None