from django.apps import AppConfig


class MacAddressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mac_address'

    def ready(self) -> None:
        from jops import updater
        updater.my_scheduled_job()
