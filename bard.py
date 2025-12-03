from google import genai  # note import path
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

client = genai.Client(api_key=api_key)

MODEL = "models/gemini-2.5-flash"

def generate_itinerary(source, destination, start_date, end_date, no_of_day):
    prompt = f"""
Generate a detailed and practical day-by-day itinerary.
From: {source} to {destination}, dates: {start_date} to {end_date}, total days: {no_of_day}.

Include:
  - Transportation
  - Sightseeing spots
  - Food recommendations
  - Budget (INR)
  - Travel tips
  - Weather considerations

Format in markdown.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text or "Unable to generate itinerary at the moment."
    except Exception as e:
        print("❌ Gemini Error:", e)
        return "Unable to generate itinerary at the moment."
