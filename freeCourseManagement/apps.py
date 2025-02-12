from django.apps import AppConfig


class freeCourseManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'freeCourseManagement'
    verbose_name = 'courseManagement_Free'

    def ready(self):
        # Import signals here
        import freeCourseManagement.signals
