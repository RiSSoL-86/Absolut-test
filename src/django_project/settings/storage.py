from typing import TYPE_CHECKING

from django_project.settings import env

if TYPE_CHECKING:
    from pathlib import Path

STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")

MEDIA_ROOT = env("MEDIA_ROOT")
STATIC_ROOT = env("STATIC_ROOT")

# there should be listed all paths which used in project
FILE_FOLDERS: dict[str, Path] = {
    # "avatars": Path("users/avatars"),
}
