from django.db import models
from django.core.validators import MinValueValidator

from users.models import User
from .validators import validate_hex


class Tag(models.Model):
    name = models.CharField(
        verbose_name='name of the tag',
        unique=True,
        max_length=150
    )
    color = models.CharField(
        verbose_name='color code of the tag',
        unique=True,
        max_length=7,
        validators=[validate_hex]
    )
    slug = models.SlugField(
        verbose_name='slug',
        unique=True
    )

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='name of the ingredient',
        max_length=256
    )
    measurement_unit = models.CharField(
        verbose_name='unit of measure',
        max_length=32
    )

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return self.name


class Receipt(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='author of the receipt',
        on_delete=models.CASCADE,
        related_name='receipts',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        verbose_name='дата публикации'
    )
    name = models.CharField(
        max_length=256,
        verbose_name='title of the receipt',
    )
    image = models.ImageField(
        verbose_name='image of the receipt',
        upload_to='receipts/'
    )
    text = models.TextField(
        verbose_name='text description',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AttachedIngredient',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        through='AttachedTag',
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name='cooking time',
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class AttachedIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='attached_to_receipts',
        on_delete=models.PROTECT
    )
    receipt = models.ForeignKey(
        Receipt,
        related_name='attached_ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount of ingredient in receipt',
        validators=(MinValueValidator(1),)
    )

    def __str__(self):
        return '{} ({})'.format(self.ingredient.name, self.receipt.name)


class AttachedTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        related_name='marked_receipts',
        on_delete=models.CASCADE,
    )
    receipt = models.ForeignKey(
        Receipt,
        related_name='attached_tags',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} ({})'.format(self.tag.name, self.receipt.name)


class Favorites(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='as_favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class ShoppingCart(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
