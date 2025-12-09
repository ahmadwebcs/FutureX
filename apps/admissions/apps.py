from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    name = 'apps.admissions'

    def ready(self):
        # import signals to connect them if needed
        pass
