import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from receipts.models import (AttachedIngredient, Favorites, Ingredient,
                             Receipt, ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import RecipeFilterSet
from .mixins import ListCreateRetrieveViewSet
from .permissions import Subscribepermission, UserPermission
from .serializers import (IngredientSerializer, PasswordChangeSerializer,
                          RecipeSerializer, SignupSerializer,
                          SubscribeUserSerializer, TagSerializer,
                          UserManageSerializer)

logger = logging.getLogger(__name__)


class UserViewSet(ListCreateRetrieveViewSet):
    queryset = User.objects.all()
    serializer_class = UserManageSerializer
    permission_classes = (UserPermission, )

    def get_serializer_class(self):
        if self.action == 'create':
            return SignupSerializer
        return UserManageSerializer

    @action(detail=False,
            methods=['GET', ],
            permission_classes=[IsAuthenticated, ])
    def me(self, request):
        """Возвращает профиль текущего пользователя."""
        user = User.objects.get(id=request.user.id)
        serializer = UserManageSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['POST', ])
    def set_password(self, request):
        """Смена пароля."""
        user = User.objects.get(id=request.user.id)
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('field error', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET', ],
            permission_classes=(Subscribepermission, ))
    def subscriptions(self, request):
        """Возвращает подписки текущего пользователя."""
        user = User.objects.get(id=request.user.id)
        subscriptions = Subscribe.objects.filter(subscriber=user)
        list_of_id = []
        for sub in subscriptions:
            list_of_id.append(sub.author.id)
        queryset = User.objects.filter(id__in=list_of_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeUserSerializer(
                page,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeUserSerializer(
            queryset,
            many=True,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(Subscribepermission, ))
    def subscribe(self, request, pk=None):
        """Позволяет подписаться или отписаться от пользователя."""
        logger.info('trying to subscribe')
        author = self.get_object()
        logger.info(f'got an author, {author}')
        user = User.objects.get(id=request.user.id)
        logger.info(f'got a user {user}')
        if request.method == 'POST':
            if (
                Subscribe.objects.filter(
                    author=author,
                    subscriber=user
                ).exists()
                or author == user
            ):
                return Response('Can\'t subscribe',
                                status=status.HTTP_400_BAD_REQUEST)
            logger.info('trying to create subscribe object')
            Subscribe.objects.create(author=author, subscriber=user)
            logger.info('sub object created, serializin author')
            serializer = SubscribeUserSerializer(
                author, context={'request': request})
            logger.info('author serialized')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.info('trying to get subscribe object')
            try:
                subscribe = Subscribe.objects.get(
                    author=author, subscriber=user
                )
            except (ObjectDoesNotExist):
                return Response(
                    'Object does not exist', status=status.HTTP_400_BAD_REQUEST
                )
            logger.info('trying to delete object')
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilterSet
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        """Позволяет добавить или удалить рецепт из избранного."""
        recipe = self.get_object()
        user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            if Favorites.objects.filter(receipt=recipe, user=user).exists():
                return Response('Already exists',
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                Favorites.objects.create(receipt=recipe, user=user)
                serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        else:
            try:
                favorite = Favorites.objects.get(receipt=recipe, user=user)
            except (ObjectDoesNotExist):
                return Response(
                    'Object does not exist', status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk=None):
        """Позволяет добавить или удалить рецепт из корзины."""
        recipe = self.get_object()
        user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(receipt=recipe, user=user).exists():
                return Response('Already exists',
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                ShoppingCart.objects.create(receipt=recipe, user=user)
                serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        else:
            try:
                favorite = ShoppingCart.objects.get(receipt=recipe, user=user)
            except (ObjectDoesNotExist):
                return Response(
                    'Object does not exist', status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['GET', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        """Позволяет скачать лист покупок."""
        user = User.objects.get(id=request.user.id)
        queryset = ShoppingCart.objects.filter(user=user)
        shopping_list = {}
        for query in queryset:
            recipe = query.receipt
            for ingredient in recipe.ingredients.all():
                name = ingredient.name
                ingredient_amount = AttachedIngredient.objects.get(
                    receipt=recipe, ingredient=ingredient)
                amount = ingredient_amount.amount
                if name in shopping_list:
                    shopping_list[name] += amount
                else:
                    shopping_list[name] = amount
        content = str()
        for key in shopping_list:
            content += key + ': ' + str(shopping_list[key]) + ', '
        filename = 'shopping_list.txt'
        response = HttpResponse(content=content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = ()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = ()
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )
