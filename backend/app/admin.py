from app.models import (
    Favourite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagForRecipe,
)

from django.contrib import admin


class IngredientInRecipeInline(admin.TabularInline):
    """
    Provides the ability to edit the ingredient in recipe model
    on the same page as the parent model.
    """

    model = IngredientInRecipe
    extra = 1


class TagForRecipeInline(admin.TabularInline):
    """
    Provides the ability to edit the tag in recipe model
    on the same page as the parent model.
    """

    model = TagForRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin panel for tag model."""

    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin panel for ingredient model."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin panel for recipe model."""

    list_display = ('author', 'name', 'get_is_favorited')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInRecipeInline, TagForRecipeInline)

    def get_is_favorited(self, obj):
        """Method counts the number of recipe additions to favorites."""

        return obj.favourites.count()

    get_is_favorited.short_description = 'number of additions to favorites'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Admin panel for ingredient in recipe model."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(TagForRecipe)
class TagForRecipeAdmin(admin.ModelAdmin):
    """Admin panel for tag in recipe model."""

    list_display = ('id', 'recipe', 'tag')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin panel for follow model."""

    list_display = ('id', 'user', 'following')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """Admin panel for favourite model."""

    list_display = ('id', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin panel for shopping cart model."""

    list_display = ('id', 'user', 'recipe')
