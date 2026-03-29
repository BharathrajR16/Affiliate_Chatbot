import os
from dotenv import load_dotenv

load_dotenv()

AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "bharathraj026-21")


def build_link(asin: str = None, product_name: str = None) -> str:
    """
    Build affiliate link.
    - If ASIN available: direct product page (better conversion)
    - If no ASIN: search page fallback
    """
    if asin:
        return f"https://www.amazon.in/dp/{asin}?tag={AFFILIATE_TAG}"
    elif product_name:
        query = product_name.replace(" ", "+")
        return f"https://www.amazon.in/s?k={query}&tag={AFFILIATE_TAG}"
    else:
        return f"https://www.amazon.in?tag={AFFILIATE_TAG}"


def format_price(price) -> str:
    if not price:
        return "Price not available"
    if isinstance(price, (int, float)):
        return f"₹{int(price):,}"
    return f"₹{price}"


def format_rating(rating) -> str:
    if not rating:
        return "4.0/5"
    return f"{float(rating):.1f}/5"


def format_reviews(reviews) -> str:
    if not reviews:
        return "1,000+ reviews"
    if isinstance(reviews, (int, float)):
        reviews = int(reviews)
        if reviews >= 100000:
            return f"{reviews // 1000}K+ reviews"
        if reviews >= 1000:
            return f"{reviews / 1000:.1f}K+ reviews"
        return f"{reviews}+ reviews"
    return str(reviews)


def generate_reason(item: dict) -> str:
    reasons = []
    rating = item.get("rating")
    reviews = item.get("reviews")
    badges = item.get("badges", [])

    if rating:
        rating = float(rating)
        if rating >= 4.5:
            reasons.append("⭐ Highly rated")
        elif rating >= 4.0:
            reasons.append("👍 Well rated")

    if reviews:
        reviews = int(reviews) if isinstance(reviews, (int, float)) else 0
        if reviews >= 10000:
            reasons.append("🔥 Popular choice")
        elif reviews >= 1000:
            reasons.append("📊 Many reviews")

    if "Amazon's Choice" in str(badges):
        reasons.append("🏆 Amazon's Choice")
    if "Best Seller" in str(badges):
        reasons.append("📈 Bestseller")

    return " • ".join(reasons) if reasons else "Great value product"