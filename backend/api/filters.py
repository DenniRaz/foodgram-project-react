from app.models import Recipe, Tag

import django_filters

from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Ingredient search filter by name."""

    search_param = "name"


class RecipeFilter(django_filters.FilterSet):
    """
    Recipe filter allows you to filter by
    favorites, shopping cart, tag and author.
    """

    is_favorited = django_filters.filters.NumberFilter(
        method='favorite_filter')
    is_in_shopping_cart = django_filters.filters.NumberFilter(
        method='shoppingcart_cart_filter')
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    def favorite_filter(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(favourites__user=user.id)
        return queryset

    def shoppingcart_cart_filter(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(shopping_carts__user=user.id)
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
