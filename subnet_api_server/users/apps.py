import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "subnet_api_server.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import subnet_api_server.users.signals  # noqa: F401
