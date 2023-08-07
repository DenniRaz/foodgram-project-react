from app.validators import validate_HEX_format

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(
        max_length=200,
        verbose_name=_('name of the tag'),
    )
    color = models.CharField(
        max_length=7,
        verbose_name=_('color'),
        validators=(validate_HEX_format,),
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name=_('unique identifier'),
        validators=(
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message=_('slug can contain only Latin letters '
                          'from "a" to "z" in any case and numbers'),
            ),
        ),
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tag',
            ),
        )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=200,
        verbose_name=_('name of the ingredient'),
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name=_('measurement_unit'),
    )

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('author of the recipe'),
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('name of the recipe'),
    )
    image = models.ImageField(
        upload_to='images/',
        verbose_name=_('image'),
    )
    text = models.TextField(verbose_name=_('recipe description'))
    ingredients = models.ManyToManyField(
        to=Ingredient,
        related_name='recipes',
        through='IngredientInRecipe',
        verbose_name=_('ingredients'),
    )
    tags = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        through='TagForRecipe',
        verbose_name=_('tags'),
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('cooking time'),
        validators=(
            MinValueValidator(
                limit_value=1,
                message=_('minimum cooking time is 1 minute'),
            ),
        ),
    )

    class Meta:
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')
        ordering = ('name',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Ingredient in recipe model."""

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes',
        verbose_name=_('recipe'),
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes',
        verbose_name=_('ingredient'),
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_('amount of ingredient in the recipe'),
        validators=(
            MinValueValidator(
                limit_value=1,
                message=_('minimum amount is 1'),
            ),
        ),
    )

    class Meta:
        verbose_name = _('ingredient in recipe')
        verbose_name_plural = _('ingredients in recipe')
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe',
            ),
        )

    def __str__(self):
        return f'{self.recipe} contains {self.ingredient}'


class TagForRecipe(models.Model):
    """Tag for recipe model."""

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='tag_in_recipes',
        verbose_name=_('recipe'),
    )
    tag = models.ForeignKey(
        to=Tag,
        on_delete=models.CASCADE,
        related_name='tag_in_recipes',
        verbose_name=_('tag'),
    )

    class Meta:
        verbose_name = _('tag in recipe')
        verbose_name_plural = _('tags in recipe')
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_tag_in_recipe',
            ),
        )

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class Follow(models.Model):
    """Follow model."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('user'),
    )
    following = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('user subscription'),
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow',
            ),
        )

    def __str__(self):
        return f'{self.user} subscriber of the {self.following}'


class Favourite(models.Model):
    """Favourite model."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name=_('user'),
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name=_('recipe'),
    )

    class Meta:
        verbose_name = _('favourite')
        verbose_name_plural = _('favourites')
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite',
            ),
        )

    def __str__(self):
        return f'{self.user} favorite {self.recipe}'


class ShoppingCart(models.Model):
    """Shopping cart model."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name=_('user'),
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name=_('recipe'),
    )

    class Meta:
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping carts')
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            ),
        )

    def __str__(self):
        return f'{self.user} added {self.recipe} to the cart'
