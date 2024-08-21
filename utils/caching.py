import hashlib
import redis
import streamlit as st

redis_client = redis.StrictRedis(
    host=st.secrets["redis_host"],
    port=12019,
    password=st.secrets["redis_password"],
    db=0,
    decode_responses=True
)

def create_cache_key(query: str, schema: str):
    return hashlib.sha256((query + schema).encode()).hexdigest()
    
def cache_results(key: str, results=None):
    if results:
        redis_client.set(key, str(results))
        return results
    cached_results = redis_client.get(key)
    if cached_results:
        return eval(cached_results)
    return None
