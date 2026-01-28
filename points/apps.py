from django.apps import AppConfig

class PointsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'points'

class AppSchedulerConfig(AppConfig):
    name = 'app'

    def ready(self):
        from .cron import start
        start()