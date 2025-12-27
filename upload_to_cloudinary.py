import os
import cloudinary
import cloudinary.uploader
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")
django.setup()

from django.conf import settings

media_path = Path(settings.MEDIA_ROOT) / "product_images"

for filename in os.listdir(media_path):
    file_path = media_path / filename
    if file_path.is_file():
        cloudinary.uploader.upload(str(file_path), folder="product_images")
        print(f"Uploaded {filename} to Cloudinary")