from django_filters import rest_framework as filters

from receipts.models import Receipt


class RecipeFilterSet(filters.FilterSet):
    """Custom filter for recipes"""
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self.user = request.user
        super().__init__(data, queryset, request=request, prefix=prefix)

    tags = filters.CharFilter(field_name='tags__slug', method='filter_tags')
    is_favorited = filters.NumberFilter(method='filter_favorite')
    is_in_shopping_cart = filters.NumberFilter(method='filter_shopping_cart')

    class Meta:
        model = Receipt
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__slug=value)

    def filter_favorite(self, queryset, name, value):
        if value == 1:
            return queryset.filter(as_favorite__user=self.user)
        elif value == 0:
            return queryset.exclude(as_favorite__user=self.user)

    def filter_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(in_shopping_cart__user=self.user)
        elif value == 0:
            return queryset.exclude(as_favorite__user=self.user)
