from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DbHandlerConfig(AppConfig):
    name = 'pydrive.dbhandler'
    verbose_name = _('DB Handler')