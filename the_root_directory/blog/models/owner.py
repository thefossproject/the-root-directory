from django.contrib.auth.models import User
from django.db import models


class Owner(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owner'
    )
    biography = models.TextField()

    def __str__(self):
        return self.user.username
