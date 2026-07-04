AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Sessions are stored in the cache backend (Redis), so the admin login used
# to manage users does not touch the database on every request.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
