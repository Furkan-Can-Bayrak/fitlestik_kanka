import google.generativeai as genai
from app.config import settings

print(f"Listing available models...")

genai.configure(api_key=settings.GOOGLE_API_KEY)

try:
    models = genai.list_models()
    print("\nAvailable models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

