from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from scraper import FragranticaScraper
import re
from urllib.parse import urlparse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = FragranticaScraper()

client = MongoClient(os.getenv("MONGO_URL"))
db = client["fragrantica_db"]
collection = db["perfumes"]


@app.get("/")
def guide():
    return {
        "routes": [
            "[GET] /docs",
            "[GET] /search?url={full_url}",
            "[GET] /ping"
        ],
        "author": "mk-ehe",
        "github": "https://github.com/mk-ehe/fragrantica-api"
        }

@app.get("/search")
def get_fragrance(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            raise HTTPException(status_code=400, detail="Invalid protocol.")

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
        if not data.get("fragrance").get("name"):
            raise HTTPException(status_code=404, detail="Page not found.")
        
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
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.get("/ping")
def ping():
    return {"status": "ok"}
