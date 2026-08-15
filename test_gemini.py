import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create a model instance
model = genai.GenerativeModel('gemini-3.6-flash')

# Make one API call
response = model.generate_content("Say hello and confirm you are working. Keep it short.")

# Print the response
print(response.text)