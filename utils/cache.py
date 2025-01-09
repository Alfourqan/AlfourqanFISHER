
from functools import lru_cache
import time

class Cache:
    _cache = {}
    _timestamps = {}
    _max_age = 300  # 5 minutes

    @classmethod
    def get(cls, key):
        if key in cls._cache:
            if time.time() - cls._timestamps[key] < cls._max_age:
                return cls._cache[key]
            else:
                del cls._cache[key]
                del cls._timestamps[key]
        return None

    @classmethod
    def set(cls, key, value):
        cls._cache[key] = value
        cls._timestamps[key] = time.time()

    @classmethod
    def clear(cls):
        cls._cache.clear()
        cls._timestamps.clear()

@lru_cache(maxsize=128)
def get_cached_data(query, params=()):
    """Cache les résultats des requêtes fréquentes"""
    pass
