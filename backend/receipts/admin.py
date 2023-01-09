from django.contrib import admin
from django.db.models import Count

from .models import (Receipt,
                     Ingredient,
                     Tag,
                     AttachedIngredient,
                     AttachedTag,
                     Favorites,
                     ShoppingCart)


class AttachedIngredientAdmin(admin.StackedInline):
    model = AttachedIngredient
    extra = 1


class AttachedTagAdmin(admin.StackedInline):
    model = AttachedTag
    extra = 1


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'favorite_count')
    list_filter = ('author', 'name', 'tags')
    inlines = [AttachedIngredientAdmin, AttachedTagAdmin]

    def favorite_count(self, obj):
        return obj.favorite_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favorite_count=Count('as_favorite', distinct=True)
        )
        return queryset


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    inlines = [AttachedIngredientAdmin, ]


class TagAdmin(admin.ModelAdmin):
    inlines = [AttachedTagAdmin]


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
