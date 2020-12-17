from typing import List
import requests
class MALConfig:
    def __init__(self, client_id, client_secret, access_token, refresh_token) -> None:
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.ACCESS_TOKEN = access_token
        self.REFRESH_TOKEN = refresh_token
        
        self.headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
        
    def regen_token(self) -> str:
        request = requests.post("https://myanimelist.net/v1/oauth2/token", data={
                  "client_id" : self.CLIENT_ID,
                  "client_secret" : self.CLIENT_SECRET,
                  "grant_type" : "refresh_token",
                  "refresh_token" : self.REFRESH_TOKEN
              })
        
        request_data = request.json()
        
        self.ACCESS_TOKEN = request_data["access_token"]
        self.REFRESH_TOKEN = request_data["refresh_token"]
        
        return self.ACCESS_TOKEN
    
    def get(self, url, params=None, **kwargs) -> requests.Response:
        if params is None:
            params = {}
        
        return requests.get(url, params=params, headers=self.headers, **kwargs)

    def post(self, url, data, **kwargs) -> requests.Response:
        return requests.post(url, data=data, headers=self.headers, **kwargs)

class Anime:
    
    def __init__(self, _id: str, config: MALConfig) -> None:
        self._id = _id
        self._config = config
        self.reload()
        
    @classmethod
    def from_name(cls, query: str, config: MALConfig):
        request = config.get("https://api.myanimelist.net/v2/anime", params={"q": query, "limit" : 1})
        anime_id = str(request.json()["data"][0]["node"]["id"])
        return cls(_id=anime_id, config=config)
    
    @classmethod
    def search(cls, query: str, config: MALConfig, limit: int = 5, basic=True):
        request = config.get("https://api.myanimelist.net/v2/anime", params={"q": query, "limit" : limit})
        
        for anime in request.json()["data"]:
            data = anime["node"]
            anime_id = data["id"]
            
            if not basic:
                yield cls(anime_id)
            else:
                yield {"name": data["title"], "cover": data["main_picture"]["large"], "anime_id": data["id"]}
    
    def reload(self):
        request = self._config.get(f"https://api.myanimelist.net/v2/anime/{self._id}", params={
            "fields":"title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,nsfw,created_at,media_type,status,genres,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,studios,statistics"
            })
        
        self._data = request.json()
        self._data: dict
    
    def __str__(self):
        return self.english_title
    
    @property
    def english_title(self) -> str:
        return self._data["title"]
     
    @property
    def japenese_title(self) -> str:
        try:
            return self._data["alternative_titles"]["ja"]
        except KeyError:
            return ""
    
    @property
    def episode_duration(self) -> int:
        return int(self._data["average_episode_duration"])
    
    @property
    def background(self) -> str:
        return self._data["background"]
    
    @property
    def broadcast(self) -> str:
        try:
            info = self._data["broadcast"]
        except KeyError:
            return "NA"
        
        return f'{info["day_of_the_week"]} {info["start_time"]}'
    
    @property
    def release_date(self) -> str:
        return self._data["created_at"].split("T")[0]
    
    @property
    def end_date(self) -> str:
        try:
            return self._data["end_date"]
        except KeyError:
            return "NA"
    
    @property
    def genres(self) -> List[str]:
        result = []
        
        for i in self._data["genres"]:
            result.append(i["name"].lower())
            
        return result
    
    @property
    def cover(self) -> str:
        return self._data["main_picture"]["large"]
    
    @property
    def pictures(self) -> List[str]:
        result = []
        
        for i in self._data["pictures"]:
            result.append(i["large"])
        
        if result == []:
            result == [self.cover]
        return result
    
    @property
    def score(self) -> float:
        return float(self._data["mean"])
    
    @property
    def number_of_episodes(self) -> int:
        return int(self._data["num_episodes"])
    
    @property
    def popularity(self) -> int:
        return int(self._data["popularity"])
                   
    @property
    def rank(self) -> int:
        return int(self._data["rank"])
        
    @property
    def age_rating(self) -> str:
        return self._data["rating"]
    
    @property
    def source(self) -> str:
        return self._data["source"]
    
    @property
    def season(self) -> str:
        info = self._data["start_season"]
        
        return f"{info['season'].capitalize()} {str(info['year'])}"
    
    @property
    def studios(self) -> List[str]:
        result = []
        
        for i in self._data["studios"]:
            result.append(i["name"])
            
        return result
    
    @property
    def status(self) -> str:
        return self._data["status"].replace("_", " ")
    
    @property
    def synopsis(self) -> str:
        return self._data["synopsis"]
    
    @property
    def nsfw(self) -> str:
        return self._data["nsfw"]
    
    @property
    def url(self) -> str:
        return f"https://myanimelist.net/anime/{self._id}/{self.english_title.replace(' ', '_')}"
