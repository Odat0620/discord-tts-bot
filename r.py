import redis
import os

redis_url = os.environ['REDIS_URL']

if not redis_url:
    redis_url = "redis://db:6379"

def connect():
    return redis.from_url(
        url=redis_url,
        decode_responses=True,
    )

def get_user_name(id: str):
    con = connect()
    return con.get(id)
