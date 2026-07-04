import factory
from factory.django import DjangoModelFactory

from apps.users.choices import Role
from apps.users.models import User

DEFAULT_PASSWORD = "testpass123"


class UserFactory(DjangoModelFactory):
    """A plain, active reader user with a usable (hashed) password."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = Role.READER
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or DEFAULT_PASSWORD)
        if create:
            obj.save()


class StaffUserFactory(UserFactory):
    """A staff user; its JWT carries ``is_staff`` so ``IsAdminUser`` passes."""

    is_staff = True


class SuperUserFactory(StaffUserFactory):
    """A full superuser (staff + superuser)."""

    is_superuser = True
