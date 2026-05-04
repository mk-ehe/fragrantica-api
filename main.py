from fastapi import FastAPI, HTTPException, Request
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from scraper import FragranticaScraper
import re
from urllib.parse import urlparse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


load_dotenv()

app = FastAPI()

origins = [
    "https://scentwatch.vercel.app",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

scraper = FragranticaScraper()

client = MongoClient(os.getenv("MONGO_URL"))
db = client["fragrantica_db"]
collection = db["perfumes"]
collection_frag_data = db["fragrantica_dataset"]


@app.get("/")
def guide():
    return {
        "routes": [
            "[GET] /docs",
            "[GET] /search?url={full_url}",
            "[GET] /ping",
            "[GET] /autocomplete?q={query}"
        ],
        "author": "mk-ehe",
        "github": "https://github.com/mk-ehe/fragrantica-api"
        }


@app.get("/search")
@limiter.limit("1/second, 15/minute")
def get_fragrance(request: Request, url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        parsed_url = urlparse(url)
        domain_pattern = r"^(www\.)?fragrantica\.[a-z]{2,6}(\.[a-z]{2})?$"
        if not re.match(domain_pattern, parsed_url.netloc):
            raise HTTPException(status_code=400, detail="Invalid domain. Only official Fragrantica URLs are allowed.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        raise HTTPException(status_code=400, detail="Malformed URL provided.")
    
    existing_data = collection.find_one({"url": url})  
    expiration_date = datetime.now(timezone.utc) - timedelta(days=7)

    if existing_data and existing_data.get("time_created"):
        time_created = existing_data.get("time_created")

        if time_created.tzinfo is None:
            time_created = time_created.replace(tzinfo=timezone.utc)
            
        if time_created > expiration_date:
            collection.update_one({"url": url}, {"$inc": {"search_count": 1}})
            existing_data.pop("_id", None)
            existing_data.pop("search_count", None)
            existing_data.pop("time_created", None)
            return existing_data

    try:
        data = scraper.get_data(url)
        if not data["fragrance"].get("name") or not data.get("notes") or not data.get("accords"):
            raise HTTPException(status_code=400, detail="Invalid URL or product not found.")
        data["time_created"] = datetime.now(timezone.utc)

        if existing_data:
            data["search_count"] = existing_data.get("search_count", 0) + 1
            collection.replace_one({"url": url}, data.copy())
        else:
            data["search_count"] = 1
            collection.insert_one(data.copy())

        data.pop("_id", None)
        data.pop("search_count", None)
        data.pop("time_created", None)
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail="An error occured while fetching perfume.")


@app.get("/autocomplete")
@limiter.limit("60/minute")
def autocomplete(request: Request, q: str = ""):
    if len(q) < 2:
        return {"results": []}
    
    words = q.strip().split()
    and_conditions = []

    for word in words:
        escaped_word = re.escape(word)
        and_conditions.append({
            "$or": [
                {"Perfume": {"$regex": escaped_word, "$options": "i"}},
                {"Brand": {"$regex": escaped_word, "$options": "i"}}
            ]
        })
        
    try:
        results = list(collection_frag_data.find(
            {"$and": and_conditions},
            {"_id": 0, "url": 1, "Perfume": 1, "Brand": 1}
        ).limit(10))
        return {"results": results}
    except Exception as e:
        print(f"ERROR: /autocomplete: {e}", flush=True)
        raise HTTPException(status_code=500, detail="Error while searching.")


@app.get("/ping")
@limiter.limit("20/minute")
def ping(request: Request):
    return {"status": "ok"}
