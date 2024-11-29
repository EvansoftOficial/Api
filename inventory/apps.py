from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        # Importa el archivo de señales al inicio para que se registren
        import inventory.signals  # Cambia 'inventory' por el nombre de tu aplicación si es necesario
