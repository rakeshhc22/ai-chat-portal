"""
App configuration for Conversations application
"""

from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    """Configuration class for conversations app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conversations'
    verbose_name = 'Conversations Management'
    
    def ready(self):
        """
        Import signal handlers when app is ready
        Uncomment when you add signal handlers
        """
        # import conversations.signals
        pass
