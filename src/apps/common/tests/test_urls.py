import importlib
from typing import TYPE_CHECKING

import pytest
from django.test import override_settings
from django.urls import clear_url_caches

import django_project.urls as project_urls

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


@pytest.fixture
def reload_urlconf() -> Iterator[Callable[[], None]]:
    """Reload the root urlconf, restoring it afterwards for other tests."""

    def _reload() -> None:
        clear_url_caches()
        importlib.reload(project_urls)

    yield _reload
    _reload()


def test_media_route_is_added_only_in_debug(
    reload_urlconf: Callable[[], None],
) -> None:
    with override_settings(DEBUG=False):
        reload_urlconf()
        without_debug = len(project_urls.urlpatterns)

    with override_settings(DEBUG=True):
        reload_urlconf()
        with_debug = len(project_urls.urlpatterns)

    # DEBUG adds exactly the extra media-serving route.
    assert with_debug == without_debug + 1
