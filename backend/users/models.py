from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """User model."""

    USER = 'user'
    ADMIN = 'admin'
    USER_ROLES = [
        (USER, 'Authorized user'),
        (ADMIN, 'Administrator'),
    ]
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    password = models.CharField(_('password'), max_length=150)
    role = models.CharField(
        _('role'),
        choices=USER_ROLES,
        default=USER,
        max_length=5,
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username
