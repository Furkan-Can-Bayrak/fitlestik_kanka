import google.generativeai as genai
from app.config import settings

print(f"Testing Gemini API with key: {settings.GOOGLE_API_KEY[:20]}...")

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

try:
    response = model.generate_content("Say 'Hello' in JSON: {\"message\": \"Hello\"}")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

