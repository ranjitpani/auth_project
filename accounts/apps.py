from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import os
        if os.environ.get('CREATE_ADMIN', 'False') == 'true':
            User = get_user_model()
            admin_email = os.environ.get('ADMIN_EMAIL')
            admin_password = os.environ.get('ADMIN_PASSWORD')
            if admin_email and admin_password:
                if not User.objects.filter(email=admin_email).exists():
                    User.objects.create_superuser(
                        email=admin_email,
                        password=admin_password
                    )