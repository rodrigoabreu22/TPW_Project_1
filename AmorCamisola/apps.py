from django.apps import AppConfig


class AmorcamisolaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AmorCamisola'

    def ready(self):
        import AmorCamisola.signals