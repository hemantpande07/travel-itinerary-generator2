import google.generativeai as palm
from dotenv import load_dotenv
import os

load_dotenv()
palm.configure(api_key=os.environ.get("PALM_API_KEY"))

models = palm.list_models()
print("Available models supporting generateContent:")
for m in models:
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
