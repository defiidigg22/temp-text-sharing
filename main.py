# main.py
import os
import redis
import secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import timedelta

# --- Configuration ---
# Connect to your local Redis instance.
# decode_responses=True makes the client return strings instead of bytes.
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise ConnectionError("REDIS_URL environment variable not set.")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

app = FastAPI(title="Temporary Text Bin API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
# This defines the structure of the incoming request body.
class SnippetIn(BaseModel):
    content: str
    expiresIn: str  # e.g., "1h", "10m", "1d"

# This defines the structure of the response after creating a snippet.
class SnippetOut(BaseModel):
    id: str
    url: str

# --- Helper Function ---
# A simple helper to parse a duration string (like "1h" or "10m") into seconds.
def duration_to_seconds(duration: str) -> int:
    unit = duration[-1]
    value = int(duration[:-1])
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    raise ValueError("Invalid duration format. Use 'm', 'h', or 'd'.")

# --- API Endpoints ---
@app.post("/create", response_model=SnippetOut)
def create_snippet(snippet: SnippetIn):
    """
    Creates a new text snippet, stores it in Redis with an expiration,
    and returns its unique ID and URL.
    """
    try:
        # Calculate expiration in seconds
        expiration_seconds = duration_to_seconds(snippet.expiresIn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate a short, URL-safe, unique ID
    snippet_id = secrets.token_urlsafe(6)

    # Store the content in Redis with the calculated expiration time (ex).
    # Redis will automatically delete this key after the time is up.
    redis_client.set(snippet_id, snippet.content, ex=expiration_seconds)

    return SnippetOut(id=snippet_id, url=f"/{snippet_id}")

@app.get("/{snippet_id}")
def get_snippet(snippet_id: str):
    """
    Retrieves a text snippet by its ID.
    Returns a 404 error if the snippet does not exist or has expired.
    """
    # Try to get the content from Redis.
    # It will return None if the key doesn't exist (or has already expired).
    content = redis_client.get(snippet_id)

    if content is None:
        raise HTTPException(status_code=404, detail="Snippet not found or has expired.")

    return {"content": content}