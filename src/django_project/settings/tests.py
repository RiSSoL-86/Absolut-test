import sys

# `manage.py test` puts "test" in argv; pytest does not, so it is detected
# via its imported module (present once the test session has started).
RUNNING_TESTS = "test" in sys.argv or "pytest" in sys.modules

if RUNNING_TESTS:
    # Use a local-memory cache so the test suite does not require a running
    # Redis instance (the session backend is cache-based as well).
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
