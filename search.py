import os
import requests
from dotenv import load_dotenv
from affiliate import build_link, format_price, format_rating, format_reviews, generate_reason

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_URL = "https://serpapi.com/search"


async def search_amazon(search_query: str) -> list:
    try:
        print(f"🔍 SerpAPI searching: {search_query}")

        params = {
            "engine": "amazon",
            "k": search_query,
            "amazon_domain": "amazon.in",
            "api_key": SERPAPI_KEY,
            "num": 8
        }

        response = requests.get(SERPAPI_URL, params=params, timeout=10)
        data = response.json()

        if "error" in data:
            print(f"❌ SerpAPI error: {data['error']}")
            return []

        organic = data.get("organic_results", [])
        print(f"✅ SerpAPI returned {len(organic)} results")

        products = []
        for item in organic[:5]:
            asin = item.get("asin")
            name = item.get("title", "Unknown Product")

            product = {
                "name": name,
                "price": format_price(item.get("price")),
                "rating": format_rating(item.get("rating")),
                "reviews": format_reviews(item.get("reviews")),
                "reason": generate_reason(item),
                "asin": asin,
                "link": build_link(asin=asin, product_name=name)
            }
            products.append(product)

        return products

    except requests.Timeout:
        print("❌ SerpAPI timeout")
        return []

    except Exception as e:
        print(f"❌ SerpAPI exception: {e}")
        return []


def get_fallback_products(query: str) -> list:
    """Return hardcoded fallback when SerpAPI fails"""
    q = query.lower()

    fallback_db = {
        "earbuds": [
            {"name": "boAt Airdopes 141", "price": "₹1,299", "rating": "4.1/5", "reviews": "85K+ reviews", "reason": "👍 Well rated • 🔥 Popular choice", "asin": "B09X4KXQJM"},
            {"name": "OnePlus Nord Buds 2", "price": "₹1,499", "rating": "4.3/5", "reviews": "42K+ reviews", "reason": "⭐ Highly rated", "asin": "B0BYQ3FKQP"},
            {"name": "Noise Air Buds Mini", "price": "₹1,199", "rating": "4.2/5", "reviews": "31K+ reviews", "reason": "👍 Well rated", "asin": "B0C1XKZMPL"},
        ],
        "headphones": [
            {"name": "boAt Rockerz 255 Pro", "price": "₹1,299", "rating": "4.2/5", "reviews": "1,00,000+ reviews", "reason": "🔥 Popular choice", "asin": "B07WQZXNPF"},
            {"name": "OnePlus Bullets Wireless Z2", "price": "₹1,999", "rating": "4.4/5", "reviews": "1,50,000+ reviews", "reason": "⭐ Highly rated", "asin": "B09WQZXNPF"},
            {"name": "Realme Buds 2 Neo", "price": "₹1,499", "rating": "4.3/5", "reviews": "80K+ reviews", "reason": "👍 Well rated", "asin": "B08WQZXNPF"},
        ],
        "phone": [
            {"name": "Redmi Note 12 5G", "price": "₹14,999", "rating": "4.3/5", "reviews": "50K+ reviews", "reason": "⭐ Highly rated • 🔥 Popular choice", "asin": "B0BT5SLN5D"},
            {"name": "Samsung Galaxy M34 5G", "price": "₹14,999", "rating": "4.2/5", "reviews": "15K+ reviews", "reason": "👍 Well rated", "asin": "B0C7FDHXZN"},
            {"name": "Realme Narzo 60x 5G", "price": "₹13,999", "rating": "4.4/5", "reviews": "10K+ reviews", "reason": "⭐ Highly rated", "asin": "B0CFXZN123"},
        ],
        "laptop": [
            {"name": "HP 15s Intel Core i3", "price": "₹39,990", "rating": "4.1/5", "reviews": "30K+ reviews", "reason": "👍 Well rated • 🔥 Popular choice", "asin": "B09LAPTOP01"},
            {"name": "Lenovo IdeaPad Slim 3", "price": "₹38,990", "rating": "4.2/5", "reviews": "25K+ reviews", "reason": "⭐ Highly rated", "asin": "B09LAPTOP02"},
        ],
        "watch": [
            {"name": "Noise ColorFit Pulse", "price": "₹999", "rating": "4.0/5", "reviews": "2,00,000+ reviews", "reason": "🔥 Popular choice", "asin": "B09WATCH001"},
            {"name": "boAt Wave Call 2", "price": "₹1,299", "rating": "4.1/5", "reviews": "1,00,000+ reviews", "reason": "👍 Well rated", "asin": "B09WATCH002"},
        ],
    }

    # Match category
    matched = None
    for key in fallback_db:
        if key in q:
            matched = fallback_db[key]
            break

    if not matched:
        matched = fallback_db["earbuds"]

    # Add affiliate links to fallback products
    for p in matched:
        p["link"] = build_link(asin=p.get("asin"), product_name=p["name"])

    return matched