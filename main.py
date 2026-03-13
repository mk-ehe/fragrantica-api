from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from scraper import FragranticaScraper
import re
from urllib.parse import urlparse

load_dotenv()

app = FastAPI()
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
    if existing_data:
        collection.update_one({"url": url}, {"$inc": {"search_count": 1}})
        existing_data.pop("_id", None)
        existing_data.pop("search_count", None)
        return existing_data

    try:
        data = scraper.get_data(url)
        if not data.get("fragrance").get("name"):
            raise HTTPException(status_code=404, detail="Page not found.")

        data["search_count"] = 1
        collection.insert_one(data.copy())
        data.pop("_id", None)
        data.pop("search_count", None)
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.get("/ping")
def ping():
    return {"status": "ok"}
