from redis import Redis

from ..config import RedisConfig

class Session:
    def __init__(self, database_config: RedisConfig):
        self.database = Redis(**database_config.__dict__)
        
