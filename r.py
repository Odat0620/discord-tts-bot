import redis
import os

redis_url = os.environ['REDIS_URL']

def connect():
    return redis.from_url(
        url=redis_url,
        decode_responses=True,
  )

def get_user_name(id: str):
    con = connect()
    return con.get(id)