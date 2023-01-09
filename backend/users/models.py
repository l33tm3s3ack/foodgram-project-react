from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='first_name',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='last_name',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True
    )
    password = models.CharField(
        verbose_name='password',
        max_length=128
    )


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        verbose_name='author',
        on_delete=models.CASCADE
    )
    subscriber = models.ForeignKey(
        User,
        related_name='subscribe',
        verbose_name='subscriber',
        on_delete=models.CASCADE
    )
