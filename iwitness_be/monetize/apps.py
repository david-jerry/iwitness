from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MonetizeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iwitness_be.monetize"
    verbose_name = _("Modetized")
