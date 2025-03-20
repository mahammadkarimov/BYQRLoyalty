from django.apps import AppConfig
from firebase_admin import credentials
import firebase_admin

class BaseUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_user'

    def ready(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("base_user/firebase/serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        
        import base_user.signals