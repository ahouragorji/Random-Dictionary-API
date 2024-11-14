from fastapi import FastAPI, HTTPException, Request
from randomWord import getRandomWord, getMeaning
import json
import redis
import os
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

# Get Redis connection details and cache TTL from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "HTTP request latency", ["method", "endpoint"])
REQUEST_FAILURES = Counter("http_request_failures_total", "Failed HTTP requests", ["method", "endpoint"])

def set_cache(key, value, ttl=CACHE_TTL):
    """Set a JSON-serializable cache entry with a TTL."""
    client.setex(key, ttl, json.dumps(value))

def get_cache(key):
    """Get a cache entry, returning it as a dictionary if found."""
    cached_value = client.get(key)
    return json.loads(cached_value) if cached_value else None

app = FastAPI()

# Middleware for metrics collection
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path

        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            try:
                response = await call_next(request)
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=response.status_code).inc()
                if response.status_code >= 400:
                    REQUEST_FAILURES.labels(method=method, endpoint=endpoint).inc()
                return response
            except Exception as e:
                REQUEST_FAILURES.labels(method=method, endpoint=endpoint).inc()
                raise e

app.add_middleware(PrometheusMiddleware)

@app.get('/metrics')
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
    #return {"hi":"boo"}

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
