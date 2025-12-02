import google.generativeai as palm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
palm_api_key = os.environ.get("PALM_API_KEY")

if not palm_api_key:
    raise RuntimeError("PALM_API_KEY not set. Please add it to your .env file.")

# Configure PaLM API
palm.configure(api_key=palm_api_key)

# Initialize the model
model = palm.GenerativeModel(model_name="models/gemini-flash-latest")

def generate_itinerary(source, destination, start_date, end_date, no_of_day):
    """
    Generate a personalized trip itinerary using PaLM API.
    Returns a string itinerary. Logs errors if generation fails.
    """
    prompt = (
        f"Generate a detailed day-by-day personalized trip itinerary for a {no_of_day}-day trip "
        f"from {source} to {destination} from {start_date} to {end_date}, "
        f"with an optimum budget (Currency: INR). Include sightseeing, food, local transport, "
        f"and best time to visit locations. Format output in readable text."
    )
    try:
        response = model.generate_content(prompt)
        itinerary_text = response.text.strip()
        if not itinerary_text:
            print("Warning: PaLM returned empty itinerary text.")
            return "Unable to generate itinerary at the moment."
        return itinerary_text
    except Exception as e:
        # Print full error to terminal for debugging
        print("Error generating itinerary:", e)
        return "Unable to generate itinerary at the moment."
