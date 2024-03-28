import os

import redis
import re

password = os.environ.get('REDIS_PWD', '')
host = os.environ.get('REDIS_HOST', 'localhost')
port = os.environ.get('REDIS_PORT', '6379')
db = 0
# Create a Redis connection
redis_client = redis.StrictRedis(
    host=host,
    port=port,
    password=password,
    db=db,
    decode_responses=True,  # Decode responses from bytes to strings
)

# Test the connection
try:
    response = redis_client.ping()
    if response:
        print("Redis server is reachable.")
    else:
        print("Redis server did not respond to ping.")


except redis.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
