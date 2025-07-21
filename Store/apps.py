from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = 'Store'


    def ready(self):
        import Store.signals


