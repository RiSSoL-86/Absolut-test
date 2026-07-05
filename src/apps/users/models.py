from typing import final

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.users.choices import Role
from apps.users.managers import UserManager


@final
class User(AbstractUser):
    username = None  # type: ignore[assignment]

    email = models.EmailField(_("email"), unique=True)
    first_name = models.CharField(_("first name"), max_length=80)
    last_name = models.CharField(_("lastname"), max_length=80)
    role = models.PositiveSmallIntegerField(
        _("role"), choices=Role.choices, default=Role.READER
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()  # type: ignore[misc]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"), name="unique_lowered_email"
            )
        ]
