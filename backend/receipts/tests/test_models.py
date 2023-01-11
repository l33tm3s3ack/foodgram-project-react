from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Ingredient, Receipt, Tag

User = get_user_model()


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = Tag.objects.create(
            name='test_tag',
            color='#AAAAAA',
            slug='test_tag'
        )
        cls.ingredient = Ingredient.objects.create(
            name='test_ingredient',
            measurement_unit='test'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.recipe = Receipt(
            author=cls.user,
            name='test_recipe',
            text='text',
            cooking_time=10
        )
        cls.recipe.ingredients.add(
            cls.ingredient,
            through_defaults={'amount': 10}
        )
        cls.recipe.tags.add(cls.tag)
        cls.recipe.save()
