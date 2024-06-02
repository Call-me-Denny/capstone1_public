from django.apps import AppConfig
import threading

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    # def ready(self):
    #     from .views import process_audio_data
    #     audio_thread = threading.Thread(target=process_audio_data, daemon=True)
    #     audio_thread.start()
