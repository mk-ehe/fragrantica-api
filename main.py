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

@app.get("/api/fragrance")
def get_fragrance(url: str):
    existing_data = collection.find_one({"url": url})
    
    if existing_data:
        collection.update_one({"url": url}, {"$inc": {"search_count": 1}})
        existing_data.pop("_id", None)
        return existing_data
    
    try:
        data = scraper.get_data(url)
        data["search_count"] = 1
        collection.insert_one(data.copy())
        data.pop("_id", None)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/ping")
def ping():
    return {"status": "ok"}