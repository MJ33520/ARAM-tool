import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API key missing!")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Available Gemini Flash Models:")
    found = False
    for m in genai.list_models():
        if "gemini" in m.name and "flash" in m.name:
            print(f"- {m.name}")
            found = True
    if not found:
        print("No flash models found.")
except Exception as e:
    print(f"Error fetching models: {e}")
