import os
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from google import genai
from PIL import Image

from django.shortcuts import render

# Glavniy sahifaga kirganda index.html ni chiqaradigan funksiya
def home_page_view(request):
    return render(request, 'index.html')

class LeafDiseaseAnalyzeView(APIView):
    # Rasm formatidagi fayllarni qabul qilish uchun parserlar
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # 1. Request ichidan rasm faylini ajratib olamiz
        image_file = request.FILES.get('image')

        if not image_file:
            return Response(
                {"error": "Rasm yuklanmadi. Iltimos, 'image' kaliti bilan rasm yuboring."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. .env fayldan API kalitni o'qiymiz va Gemini mijozini yaratamiz
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return Response(
                    {"error": "Serverda API kalit topilmadi. .env faylni tekshiring."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            client = genai.Client(api_key=api_key)

            # 3. Kelgan rasmni PIL (Pillow) kutubxonasi yordamida ochamiz
            img = Image.open(image_file)

            # 4. Menga (Gemini'ga) beriladigan aniq ko'rsatma (Prompt)
            prompt = """
            Zararlangan o'simlik bargining rasmini tahlil qil va faqat quyidagi formatda toza JSON qaytar:
            {
                "status": "success",
                "detected_disease": "Kasallik nomi (Inglizcha va O'zbekcha)",
                "confidence": "Aniqlik foizi (masalan, 95%)",
                "plant_name": "O'simlik nomi",
                "part_affected": "Zararlangan qismi",
                "disease_type": "Kasallik turi (bakteriyalik, zamburug'li va h.k.)",
                "cure": "Kasallikni davolash va oldini olish choralari (O'zbek tilida batafsil)"
            }
            Diqqat: Javobingda faqat toza JSON matni bo'lsin, hech qanday ```json markdown belgilari yoki ortiqcha so'zlar qo'shma!
            """

            # 5. Rasmni va promptni eng so'nggi 'gemini-2.5-flash' modeliga uzatamiz
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[img, prompt]
            )

            # 6. Mendan qaytgan matnni JSON formatiga o'giramiz (pars qilamiz)
            # Agar model string qaytargan bo'lsa, uni Python lug'atiga (dict) aylantiramiz
            try:
                result_json = json.loads(response.text.strip())
                return Response(result_json, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                # Agar model kutilmaganda toza JSON formatda qaytarmasa, matnning o'zini yuboramiz
                return Response({"status": "success", "raw_data": response.text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Tizimda xatolik yuz berdi: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )