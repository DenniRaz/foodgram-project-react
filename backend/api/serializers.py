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

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers

User = get_user_model()


class IngredientKeyedRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A field that processes the ingredient id and its quantity in the recipe.
    """

    def get_queryset(self):
        return Ingredient.objects.all()

    def to_internal_value(self, data):
        try:
            ingredient = self.get_queryset().get(id=data['id'])
            amount = data['amount']
            return (ingredient, amount)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data['id'])
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data['id']).__name__)

    def to_representation(self, value):
        ingredient, amount = value
        return {'id': ingredient.id, 'amount': amount}


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """Serializer to represent the user."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Method indicating whether the current user
        is subscribed to another user.
        """

        request = self.context.get('request')
        user = request.user
        return Follow.objects.filter(user=user.id, following=obj).exists()


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user creation."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for the ingredient in recipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer to represent the recipe."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_in_recipes',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """
        Method indicating whether the recipe has been added to favorites.
        """

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Method indicating whether the recipe has been added to shopping cart.
        """

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe creation."""

    ingredients = IngredientKeyedRelatedField(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        for obj in value:
            ingredient, amount = obj
            if amount < 1:
                raise serializers.ValidationError('Minimum amount is 1')
            return value

    def create_ingredient(self, ingredients, recipe):
        """Ingredient creation method."""

        for obj in ingredients:
            ingredient, amount = obj
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )

    def create_tag(self, tags, recipe):
        """Tag creation method."""

        for pk in tags:
            TagForRecipe.objects.create(recipe=recipe, tag=pk)

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.create_ingredient(ingredients, recipe)
        self.create_tag(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            self.create_tag(tags, instance)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredient(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeSerializer(instance, context={'request': request})
        return serializer.data


class FavouriteAndShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for favorite and shopping cart."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for managing subscriptions."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """
        A method for serializing user recipes
        with the ability to specify an object output limit.
        """

        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit:
            recipes = Recipe.objects.filter(author=obj)[:int(recipes_limit)]
        serializer = FavouriteAndShoppingCartSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Method for counting the number of user recipes."""

        return Recipe.objects.filter(author=obj).count()
