import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")  # free tier model

PROMPT_TEMPLATE = """
You are a shopping assistant. Extract the product search intent from the user message.
Return ONLY valid JSON, no explanation, no markdown, no backticks.

User message: "{message}"

Return this exact format:
{{
  "product": "product name",
  "budget": 0,
  "category": "electronics or clothing or footwear or appliances or general",
  "search_query": "optimized amazon search query with budget in rupees"
}}

Rules:
- If no budget mentioned, set budget to 0
- search_query must be specific and include price if mentioned
- Always add "India" context in search_query
"""


async def extract_intent(message: str) -> dict:
    try:
        print(f"Gemini processing: {message}")
        prompt = PROMPT_TEMPLATE.format(message=message)
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean response if any backticks slipped through
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)
        print(f"Gemini extracted: {result}")
        return result

    except json.JSONDecodeError as e:
        print(f"Gemini JSON parse error: {e}")
        # Fallback - treat whole message as search query
        return {
            "product": message,
            "budget": 0,
            "category": "general",
            "search_query": f"best {message} in India"
        }

    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "product": message,
            "budget": 0,
            "category": "general",
            "search_query": f"best {message} in India"
        }