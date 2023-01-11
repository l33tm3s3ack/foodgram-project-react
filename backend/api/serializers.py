from django.core.paginator import Paginator
from receipts.models import (AttachedIngredient, AttachedTag, Favorites,
                             Ingredient, Receipt, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from users.models import Subscribe, User

from .fields import Base64ImageField


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


class UserManageSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email',
                  'id',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        """Метод, определяющий,
        является ли текущий пользователь подписанным или нет."""
        user = self.context['request'].user
        return not user.is_anonymous and Subscribe.objects.filter(
            author=obj, subscriber=user).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.StringRelatedField(
        source='ingredient.name', read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = AttachedIngredient
        fields = ('id', 'measurement_unit', 'name', 'amount')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.ingredient.id
        return representation


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        source='attached_ingredients'
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    author = UserManageSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Receipt
        fields = ('id',
                  'author',
                  'name',
                  'image',
                  'text',
                  'ingredients',
                  'tags',
                  'cooking_time',
                  'is_in_shopping_cart',
                  'is_favorited',)

    def to_internal_value(self, data):
        tags_id = data.get('tags')
        internal_data = super().to_internal_value(data)
        try:
            tags = Tag.objects.filter(id__in=tags_id)
        except Tag.DoesNotExist:
            raise ValidationError(
                {'tags': ['invalid tags id']},
                code='invalid'
            )
        internal_data['tags'] = tags
        return internal_data

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and ShoppingCart.objects.filter(
            receipt=obj, user=user).exists()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and Favorites.objects.filter(
            receipt=obj, user=user).exists()

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('attached_ingredients')
        user = self.context['request'].user
        recipe = Receipt(author=user, **validated_data)
        recipe.save()
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            AttachedIngredient.objects.create(
                receipt=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('attached_ingredients')
        user = self.context['request'].user
        recipe = instance
        if recipe.author != user:
            raise ValidationError(
                {"author": "You are not author of this recipe"},
                code='invalid'
            )
        for attr, value in validated_data.items():
            setattr(recipe, attr, value)
        AttachedTag.objects.filter(receipt=recipe).delete()
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        AttachedIngredient.objects.filter(receipt=recipe).delete()
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            AttachedIngredient.objects.create(
                receipt=recipe,
                ingredient=ingredient,
                amount=amount
            )
        recipe.save()
        return recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Receipt
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email',
                  'id',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )

    def get_recipes_count(self, obj):
        return Receipt.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        page_size = (self.context['request'].query_params.get('recipes_limit')
                     or 10)
        paginator = Paginator(obj.receipts.all(), page_size)
        recipes = paginator.page(1)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscribe.objects.filter(
            author=obj, subscriber=user).exists()
