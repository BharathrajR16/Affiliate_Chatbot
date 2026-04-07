import time

# Simple in-memory cache
# Key = search query, Value = (timestamp, results)
_cache = {}
CACHE_EXPIRY = 1800  # 30 minutes


def get_cache(key: str):
    if key in _cache:
        timestamp, data = _cache[key]
        if time.time() - timestamp < CACHE_EXPIRY:
            print(f"Cache hit: {key}")
            return data
        else:
            del _cache[key]
    return None


def set_cache(key: str, data):
    _cache[key] = (time.time(), data)
    print(f"Cached: {key}")


def clear_cache():
    _cache.clear()
    print("Cache cleared")