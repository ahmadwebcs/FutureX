from django.apps import AppConfig


class InvestmentsConfig(AppConfig):
    name = 'apps.investments'

    def ready(self):
        # import signals to connect them
        from . import signals  # noqa: F401
