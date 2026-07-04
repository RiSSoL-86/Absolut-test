from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.IntegerChoices):
    READER = 0, _("reader")
    AUTHOR = 1, _("author")
