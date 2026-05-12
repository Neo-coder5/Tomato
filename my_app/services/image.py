from rest_framework.exceptions import ValidationError

ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_SIZE_MB = 10

def validate_image(image_file):
    if image_file.content_type not in ALLOWED_TYPES:
        raise ValidationError("Faqat JPEG, PNG, WEBP formatlar qabul qilinadi.")

    if image_file.size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Rasm {MAX_SIZE_MB}MB dan kichik bo'lishi kerak.")

    return image_file