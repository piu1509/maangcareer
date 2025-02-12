
import threading
from django.apps import AppConfig
from .tasks import my_background_task 


class NotificationmanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificationManagement'

    def ready(self):
        # Ensure the background task is started only once
        if not hasattr(self, 'started'):
            self.started = True
            threading.Thread(target=my_background_task, daemon=True).start()



    