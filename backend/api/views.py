from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.mixins import ListRetrieveCreateViewSet
from api.pagination import LimitPageNumberPagination
from api.serializers import TagSerializer, IngredientSerializer, UserSerializer, RecipeSerializer, \
    FavouriteAndShoppingCartSerializer
from app.models import Tag, Ingredient, Recipe, Favourite, ShoppingCart, Follow

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet for the tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet for the ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(ListRetrieveCreateViewSet):
    """ViewSet for the user."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        """Method of interaction with subscription."""

        user = request.user
        following = get_object_or_404(User, id=pk)
        subscription = Follow.objects.filter(user=user, following=following)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    data={
                        'errors': 'the user is already in the subscriptions',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(user=user, following=following)
            serializer =
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                data={"errors": "the user is not in subscriptions"},
                status=status.HTTP_404_NOT_FOUND,
            )


class RecipeViewSet(ModelViewSet):
    """ViewSet for the recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Method of interaction with favorite recipes."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = Favourite.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if favorites.exists():
                return Response(
                    data={
                        'errors': 'the recipe has already '
                                  'been added to favorites',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favourite.objects.create(user=user, recipe=recipe)
            serializer = FavouriteAndShoppingCartSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            if favorites.exists():
                favorites.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                data={'errors': 'the recipe is not in favorites'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """Method of interaction with shopping cart."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if shopping_cart.exists():
                return Response(
                    data={
                        'errors': 'the recipe has already '
                                  'been added to shopping cart',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = FavouriteAndShoppingCartSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                data={'errors': 'the recipe is not in shopping cart'},
                status=status.HTTP_404_NOT_FOUND,
            )

    # @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    # def download_shopping_cart(self, request):
    #     pass
