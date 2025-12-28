from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_superuser, sender=self)


def create_superuser(sender, **kwargs):
    User = get_user_model()

    if not User.objects.filter(email="admin@gmail.com").exists():
        User.objects.create_superuser(
            email="admin@gmail.com",
            password="Admin@123"
        )