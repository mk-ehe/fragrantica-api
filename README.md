# 🧴 Fragrantica API

A high-performance, serverless API built to scrape and cache perfume data from Fragrantica. Designed for seamless deployment on **Vercel** with a **MongoDB Atlas** backend.

---

## 🚀 Key Features

* **Intelligent Scraping**: Extracts notes, accords, ratings, and brand info using `cloudscraper` to bypass basic bot protections.
* **Smart Caching**: Stores results in MongoDB to prevent redundant scraping and ensure lightning-fast responses for popular scents.
* **Data Integrity**: Includes validation logic to prevent junk data from entering the database.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **Framework** | FastAPI |
| **Database** | MongoDB Atlas |
| **Deployment** | Vercel |

---

## 📡 API Endpoints

### 1. Search & Scrape
`GET /search?url={full_url}`
Fetches perfume data. If cached, it increments the `search_count` and returns the data immediately.

### 2. Health Check
`GET /ping`
Keeps the serverless function "warm" to prevent cold starts.

### 3. Documentation
`GET /docs`
Interactive Swagger UI to test the API directly in your browser.

---

## 📖 Usage Examples

Below are examples of requests and responses for each endpoint.

### 1. Home / Menu
**Request:** `GET /`

**Response:**
```json
{
  "routes": [
    "/docs",
    "/search?url={full_url}",
    "/ping"
  ],
  "author": "mk-ehe",
  "github": "https://github.com/mk-ehe/fragrantica-api"
}
```
---

### 2: Searching
**Request:** `GET /search?url=https://www.fragrantica.com/perfume/Dior/Sauvage-31861.html`

**Response:**
```json
{
  "fragrance": {
    "name": "Sauvage Dior",
    "image": "https://fimgs.net/mdimg/perfume-thumbs/375x500.31861.jpg"
  },
  "gender": "for men",
  "rating": "3.86",
  "amount_of_rates": "31,551",
  "accords": [
    {
      "name": "fresh spicy",
      "color": "#83C928"
    },
    {
      "name": "amber",
      "color": "#bc4d10"
    },
    {
      "name": "citrus",
      "color": "#F9FF52"
    },
    {
      "name": "aromatic",
      "color": "#37a089"
    },
    {
      "name": "musky",
      "color": "#E7D8EA"
    },
    {
      "name": "woody",
      "color": "#774414"
    },
    {
      "name": "lavender",
      "color": "#9B7DB8"
    },
    {
      "name": "herbal",
      "color": "#6CA47F"
    },
    {
      "name": "warm spicy",
      "color": "#CC3300"
    }
  ],
  "notes": {
    "top": [
      {
        "name": "Calabrian bergamot",
        "image": "https://fimgs.net/mdimg/sastojci/t.75.jpg"
      },
      {
        "name": "Pepper",
        "image": "https://fimgs.net/mdimg/sastojci/t.158.jpg"
      }
    ],
    "heart": [
      {
        "name": "Sichuan Pepper",
        "image": "https://fimgs.net/mdimg/sastojci/t.213.jpg"
      },
      {
        "name": "Lavender",
        "image": "https://fimgs.net/mdimg/sastojci/t.1.jpg"
      },
      {
        "name": "Pink Pepper",
        "image": "https://fimgs.net/mdimg/sastojci/t.91.jpg"
      },
      {
        "name": "Vetiver",
        "image": "https://fimgs.net/mdimg/sastojci/t.2.jpg"
      },
      {
        "name": "Patchouli",
        "image": "https://fimgs.net/mdimg/sastojci/t.34.jpg"
      },
      {
        "name": "Geranium",
        "image": "https://fimgs.net/mdimg/sastojci/t.21.jpg"
      },
      {
        "name": "elemi",
        "image": "https://fimgs.net/mdimg/sastojci/t.390.jpg"
      }
    ],
    "base": [
      {
        "name": "Ambroxan",
        "image": "https://fimgs.net/mdimg/sastojci/t.563.jpg"
      },
      {
        "name": "Cedar",
        "image": "https://fimgs.net/mdimg/sastojci/t.41.jpg"
      },
      {
        "name": "Labdanum",
        "image": "https://fimgs.net/mdimg/sastojci/t.15.jpg"
      }
    ]
  },
  "url": "https://www.fragrantica.com/perfume/Dior/Sauvage-31861.html"
}
```

---

### 3. Health Check
`GET /ping`

**Response:**
```json
{"status":"ok"}
```

---


## ⚙️ Setup & Environment

To run this project, you need to add your **MongoDB connection string** to Vercel's **Environment Variables**:

* **Key**: `MONGO_URL`
* **Value**: `mongodb+srv://user:password@cluster.mongodb.net/...`

---

## 💻 Local Setup

1. Clone the repo: `git clone https://github.com/mk-ehe/fragrantica-api`
2. Install dependecies: `pip install -r requirements.txt`
3. Create a `.env` file with your `MONGO_URL`.
4. Start the dev server: `fastapi dev main.py`
