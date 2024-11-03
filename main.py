from fastapi import FastAPI, HTTPException
from randomWord import getRandomWord, getMeaning
import json
import redis
import os

# Get Redis connection details and cache TTL from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def set_cache(key, value, ttl=CACHE_TTL):
    """Set a JSON-serializable cache entry with a TTL."""
    client.setex(key, ttl, json.dumps(value))

def get_cache(key):
    """Get a cache entry, returning it as a dictionary if found."""
    cached_value = client.get(key)
    return json.loads(cached_value) if cached_value else None

app = FastAPI()

@app.get('/random')
def random():
    # Generate a random word and try to get its cached meaning
    word = json.loads(getRandomWord())['word'][0]
    meaning = get_cache(word)

    if meaning is None:
        meaning = json.loads(getMeaning(word))
        if not meaning:
            raise HTTPException(status_code=404, detail="Meaning not found.")
        meaning['source'] = 'api-ninjas'
        set_cache(word, meaning)  # Cache the meaning
    else:
        meaning['source'] = 'redis'

    return meaning

@app.get('/dictionary')
def dictionary(word: str):
    # Try to get cached meaning
    meaning = get_cache(word)

    # If not cached, fetch and cache the meaning
    if meaning is None:
        meaning_data = json.loads(getMeaning(word))
        if not meaning_data:
            raise HTTPException(status_code=404, detail="Meaning not found.")
        
        meaning = {"word": word, "definition": meaning_data['definition'], "source": "api-ninjas"}
        set_cache(word, meaning)  # Cache the meaning
    else:
        meaning['source'] = 'redis'
    return meaning
