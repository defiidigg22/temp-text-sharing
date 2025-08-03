# main.py

# 1. All imports at the top
import os
import redis
import secrets
from datetime import timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv() # Loads variables from your .env file for local development

# 2. Initialize the FastAPI app first
app = FastAPI(title="Temporary Text Bin API")

# 3. Add middleware right after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Connect to Redis (using environment variable)
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    # This will only happen if the .env file is missing or the variable isn't set
    raise ConnectionError("REDIS_URL environment variable not set.")
redis_client = redis.from_url(redis_url, decode_responses=True)


# --- Pydantic Models ---
class SnippetIn(BaseModel):
    content: str
    expiresIn: str

class SnippetOut(BaseModel):
    id: str
    url: str

# --- Helper Function ---
def duration_to_seconds(duration: str) -> int:
    unit = duration[-1]
    if not duration[:-1].isdigit():
        raise ValueError("Invalid duration value.")
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
    try:
        expiration_seconds = duration_to_seconds(snippet.expiresIn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    snippet_id = secrets.token_urlsafe(6)
    redis_client.set(snippet_id, snippet.content, ex=expiration_seconds)
    return SnippetOut(id=snippet_id, url=f"/{snippet_id}")

@app.get("/{snippet_id}")
def get_snippet(snippet_id: str):
    content = redis_client.get(snippet_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Snippet not found or has expired.")
    return {"content": content}

# --- Static File Serving (at the end) ---
# This serves all files from the 'frontend' directory (like css, js)
app.mount("/frontend", StaticFiles(directory="frontend"), name="static")

# This serves the index.html file for the root URL
@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')