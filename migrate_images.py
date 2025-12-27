import os
import django

# 1️⃣ Django settings load କର
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_project.settings")
django.setup()

from accounts.models import Product
from cloudinary.uploader import upload

for product in Product.objects.filter(image__isnull=False):
    # 2️⃣ Puruna Cloudinary URLs skip କରିବା
    if str(product.image).startswith("http"):
        continue

    # 3️⃣ Full local path build କର
    from django.conf import settings
    local_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

    # 4️⃣ Cloudinary re upload କର
    cloud_resp = upload(local_path, folder="product_images")

    # 5️⃣ Model update କର
    product.image = cloud_resp['secure_url']
    product.save()
    print(f"Uploaded {product.name} to Cloudinary")