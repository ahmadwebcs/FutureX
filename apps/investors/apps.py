from django.apps import AppConfig


class InvestorsConfig(AppConfig):
    name = 'apps.investors'

    def ready(self):
        from . import signals  # noqa: F401
