import os
import json
import logging
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import PredictionHistory

# 🌟 TARJIMON KUTUBXONASINI ULAYMIZ
from deep_translator import GoogleTranslator

# =========================================
# 🔧 RESURSLARNING YO'LLARI (PATHS)
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_PATH = os.path.join(BASE_DIR, 'resources')

MODEL_PATH = os.path.join(RESOURCE_PATH, "Plaintify_diseases_classifier_model.keras")
DIS_JSON_PATH = os.path.join(RESOURCE_PATH, "dis.json")
DATA_INFO_JSON_PATH = os.path.join(RESOURCE_PATH, "datainfo.json")

# Server yonganda fayllarni xotiraga bir marta yuklab olamiz
MODEL = tf.keras.models.load_model(MODEL_PATH)

with open(DIS_JSON_PATH, "r", encoding="utf-8") as f:
    DIS_JSON = json.load(f)

with open(DATA_INFO_JSON_PATH, "r", encoding="utf-8") as f:
    DATA_INFO_DF = pd.DataFrame(json.load(f)["data"])

CLASS_LABELS = [
    'Apple Apple scab', 'Apple Black rot', 'Apple Cedar apple rust', 'Apple healthy',
    'Bacterial leaf blight in rice leaf', 'Blight in corn Leaf', 'Blueberry healthy',
    'Brown spot in rice leaf', 'Cercospora leaf spot', 'Cherry (including sour) Powdery mildew',
    'Cherry (including_sour) healthy', 'Common Rust in corn Leaf', 'Corn (maize) healthy', 'Garlic',
    'Grape Black rot', 'Grape Esca Black Measles', 'Grape Leaf blight Isariopsis Leaf Spot',
    'Grape healthy', 'Gray Leaf Spot in corn Leaf', 'Leaf smut in rice leaf',
    'Nitrogen deficiency in plant', 'Orange Haunglongbing Citrus greening', 'Peach healthy',
    'Pepper bell Bacterial spot', 'Pepper bell healthy', 'Potato Early blight',
    'Potato Late blight', 'Potato healthy', 'Raspberry healthy', 'Sogatella rice',
    'Soybean healthy', 'Strawberry Leaf scorch', 'Strawberry healthy', 'Tomato Bacterial spot',
    'Tomato Early blight', 'Tomato Late blight', 'Tomato Leaf Mold', 'Tomato Septoria leaf spot',
    'Tomato Spider mites Two spotted spider mite', 'Tomato Target Spot',
    'Tomato Tomato mosaic virus', 'Tomato healthy', 'Waterlogging in plant', 'algal leaf in tea',
    'anthracnose in tea', 'bird eye spot in tea', 'brown blight in tea', 'cabbage looper',
    'corn crop', 'ginger', 'healthy tea leaf', 'lemon canker', 'onion',
    'potassium deficiency in plant', 'potato crop', 'potato hollow heart',
    'red leaf spot in tea', 'tomato canker'
]

logging.basicConfig(filename='predictions.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# =========================================
# 🚀 DJANGO API VIEW (KLASS)
# =========================================
class PlantDiseasePredictView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "Rasm fayli yuklanmadi!"}, status=400)

        try:
            # 1. Rasmni AI model o'qiydigan formatga keltirish
            img = Image.open(image_file).convert("RGB")
            img = img.resize((224, 224), Image.Resampling.LANCZOS)
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # 2. Model orqali kasallikni aniqlash
            predictions = MODEL.predict(img_array, verbose=0)
            idx = np.argmax(predictions)
            confidence = float(predictions[idx])
            predicted_class = CLASS_LABELS[idx]
            disease_key = predicted_class.lower()

            logging.info(f"Rasm: {image_file.name} | Natija: {predicted_class} | Ishonch: {confidence * 100:.2f}%")

            # 3. Natijani ma'lumotlar bazasida saqlash
            user = request.user if request.user.is_authenticated else None
            PredictionHistory.objects.create(
                user=user,
                image_name=image_file.name,
                detected_disease=predicted_class,
                confidence=f"{confidence * 100:.2f}%"
            )

            # 4. datainfo.json faylidan ma'lumotlarni qidirish
            matched = DATA_INFO_DF[DATA_INFO_DF["name"].str.contains(disease_key, case=False, na=False)]
            plant_info = {}
            if not matched.empty:
                info = matched.iloc[0]
                plant_info = {
                    "plant_name": str(info['plantName']),
                    "part_affected": str(info['plantPart']),
                    "disease_type": str(info['diseaseType']),
                    "cure": str(info['cure'])
                }

            # 5. dis.json faylidan qo'shimcha davolash choralarini qidirish
            additional_cure = DIS_JSON.get(disease_key, None)
            if not additional_cure:
                for key in DIS_JSON.keys():
                    if disease_key in key.lower():
                        additional_cure = DIS_JSON[key]
                        break

            # 6. 🌟 INGLIZCHADAN O'ZBEK TILIGA AVTOMATIK TARJIMA QILISH
            # Tarjimon ob'ektini yaratamiz (en -> uz)
            translator = GoogleTranslator(source='en', target='uz')

            # Kasallik nomi va davolash choralarini tarjima qilamiz
            uz_detected_disease = translator.translate(predicted_class)

            uz_plant_info = {}
            if plant_info:
                uz_plant_info = {
                    "plant_name": translator.translate(plant_info["plant_name"]),
                    "part_affected": translator.translate(plant_info["part_affected"]),
                    "disease_type": translator.translate(plant_info["disease_type"]),
                    "cure": translator.translate(plant_info["cure"])
                }

            uz_additional_cure = "Qo'shimcha davolash chorasi yo'q."
            if additional_cure:
                uz_additional_cure = translator.translate(additional_cure)

            # 7. Yakuniy javobni O'ZBEK tilida qaytarish
            return Response({
                "status": "success",
                "prediction": {
                    "detected_disease_en": predicted_class,
                    "detected_disease_uz": uz_detected_disease,  # ◄ O'zbekcha nomi
                    "confidence": f"{confidence * 100:.2f}%"
                },
                "details_uz": uz_plant_info if uz_plant_info else "Batafsil ma'lumot topilmadi.",
                "additional_cure_uz": uz_additional_cure
            })

        except Exception as e:
            return Response({"error": f"Tahlil jarayonida ichki xatolik: {str(e)}"}, status=500)
