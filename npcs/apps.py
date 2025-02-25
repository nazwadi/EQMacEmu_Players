import logging

from django.apps import AppConfig


class NpcsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'npcs'

    def ready(self):
        # Set up app-specific logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)  # Adjust as needed
