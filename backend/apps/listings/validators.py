from PIL import Image
from rest_framework import serializers

MAX_IMAGE_SIZE = 8 * 1024 * 1024
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
MAX_IMAGES_PER_LISTING = 10


def validate_listing_image(upload):
    if upload.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError('A imagem não pode exceder 8 MB.')
    try:
        upload.seek(0)
        image = Image.open(upload)
        image.verify()
        upload.seek(0)
        image = Image.open(upload)
        if image.format not in ALLOWED_FORMATS:
            raise serializers.ValidationError('Formato não suportado. Use JPEG, PNG ou WEBP.')
        if image.width < 300 or image.height < 300:
            raise serializers.ValidationError('A imagem deve ter pelo menos 300x300 pixels.')
    except serializers.ValidationError:
        raise
    except Exception as exc:
        raise serializers.ValidationError('Ficheiro de imagem inválido.') from exc
