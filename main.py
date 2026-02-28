from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from scraper import FragranticaScraper


load_dotenv()

app = FastAPI()
scraper = FragranticaScraper()

client = MongoClient(os.getenv("MONGO_URL"))
db = client["fragrantica_db"]
collection = db["perfumes"]


@app.get("/")
def home():
    return {"routes": ["/docs", "/search?url={full_url}", "/ping" ], "author": "mk-ehe", "github": "https://github.com/mk-ehe/fragrantica-api"}

@app.get("/search")
def get_fragrance(url: str):
    existing_data = collection.find_one({"url": url})
    
    if existing_data:
        collection.update_one({"url": url}, {"$inc": {"search_count": 1}})
        existing_data.pop("_id", None)
        existing_data.pop("search_count", None)
        return existing_data
    
    try:
        data = scraper.get_data(url)
        if not data.get("fragrance"):
            raise HTTPException(status_code=404, detail="Page not found.")

        data["search_count"] = 1
        collection.insert_one(data.copy())
        data.pop("_id", None)
        data.pop("search_count", None)
        return data
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@app.get("/ping")
def ping():
    return {"status": "ok"}
