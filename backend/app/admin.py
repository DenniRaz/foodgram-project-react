from app.models import (
    Favourite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)

from django.contrib import admin


class IngredientInRecipeInline(admin.TabularInline):
    """
    Provides the ability to edit the ingredient in recipe model
    on the same page as the parent model.
    """

    model = IngredientInRecipe
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin panel for tag model."""

    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin panel for ingredient model."""

    list_display = ('id', 'name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin panel for recipe model."""

    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    inlines = (IngredientInRecipeInline,)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Admin panel for ingredient in recipe model."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')


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
