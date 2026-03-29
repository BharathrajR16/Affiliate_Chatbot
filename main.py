import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from gemini import extract_intent
from search import search_amazon, get_fallback_products
from cache import get_cache, set_cache

load_dotenv()

app = FastAPI(title="ShopBot API")

# CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="public"), name="static")

# Rate limiting - simple in-memory
rate_tracker = {}
RATE_LIMIT = 10       # max requests
RATE_WINDOW = 60      # per 60 seconds


def check_rate_limit(ip: str) -> bool:
    import time
    now = time.time()
    requests = rate_tracker.get(ip, [])
    recent = [t for t in requests if now - t < RATE_WINDOW]
    if len(recent) >= RATE_LIMIT:
        return False
    recent.append(now)
    rate_tracker[ip] = recent
    return True


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def serve_frontend():
    return FileResponse("public/index.html")


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    message = req.message.strip()
    print(f"\n📥 Message: {message}")

    if not message:
        return JSONResponse({"error": "Message required"}, status_code=400)

    # Rate limit check
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        print(f"⚠️ Rate limit hit for {client_ip}")
        return JSONResponse({
            "products": get_fallback_products(message),
            "note": "⏰ Too many requests. Showing cached recommendations.",
            "source": "fallback"
        })

    # Check cache first
    cache_key = message.lower().strip()
    cached = get_cache(cache_key)
    if cached:
        return JSONResponse({
            "products": cached,
            "note": "⚡ Instant results",
            "source": "cache"
        })

    try:
        # Step 1: Gemini extracts intent
        intent = await extract_intent(message)
        search_query = intent.get("search_query", message)

        # Step 2: SerpAPI searches Amazon
        products = await search_amazon(search_query)

        # Step 3: Fallback if no results
        if not products:
            print("⚠️ No SerpAPI results, using fallback")
            products = get_fallback_products(search_query)
            note = "✨ Showing curated recommendations"
            source = "fallback"
        else:
            note = "🛍️ Live results from Amazon"
            source = "live"

        # Cache successful results
        set_cache(cache_key, products)

        return JSONResponse({
            "products": products,
            "note": note,
            "source": source,
            "intent": intent  # useful for debugging
        })

    except Exception as e:
        print(f"❌ Server error: {e}")
        return JSONResponse({
            "products": get_fallback_products(message),
            "note": "✨ Showing curated recommendations",
            "source": "fallback"
        })


@app.get("/health")
async def health():
    return {"status": "ok", "message": "ShopBot is running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Starting ShopBot on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)