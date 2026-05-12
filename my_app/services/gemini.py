import google.generativeai as genai
import json, re
from PIL import Image
import io
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

PROMPT = """
Sen qishloq xo'jaligi mutaxassisisan.
Berilgan o'simlik rasmini tahlil qil va FAQAT quyidagi JSON formatda javob qaytar:

{
  "kasallik_nomi": "kasallik nomi yoki 'Sog'lom o'simlik'",
  "ishonch_darajasi": "yuqori yoki orta yoki past",
  "sababi": "kasallik sababi",
  "belgilari": ["belgi 1", "belgi 2"],
  "davolash": ["davo 1", "davo 2"],
  "oldini_olish": ["usul 1", "usul 2"],
  "shoshilinchlik": "yuqori yoki orta yoki past"
}

Boshqa hech narsa yozma, faqat JSON.
"""

def analyze_image(image_file):
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes))

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([PROMPT, image])

    text = response.text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("Gemini dan noto'g'ri javob keldi")

    return json.loads(json_match.group())