from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        pass