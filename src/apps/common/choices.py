from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.IntegerChoices):
    RUSSIAN = 0, _("russian")
    ENGLISH = 1, _("english")
