from api.filters import IngredientSearchFilter, RecipeFilter
from api.mixins import ListRetrieveCreateViewSet
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    CreateUserSerializer,
    FavouriteAndShoppingCartSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)

from app.models import (
    Favourite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet for the tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet for the ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(ListRetrieveCreateViewSet):
    """ViewSet for the user."""

    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Method for demonstrating user subscriptions."""

        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(data=serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        """Method of interaction with subscription."""

        user = request.user
        following = get_object_or_404(User, pk=pk)
        subscription = Follow.objects.filter(user=user, following=following)
        if request.method == 'POST':
            if user == following:
                return Response(
                    data={
                        'errors': 'subscribing to yourself is not possible',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if subscription.exists():
                return Response(
                    data={
                        'errors': 'the user is already in the subscriptions',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(
                following,
                context={'request': request},
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
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
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def addition_and_removal(self, request, pk, query, msg):
        """
        Universal method for adding and removing
        objects from favorites and shopping lists.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = query.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    data={
                        'errors': 'the recipe has already '
                                  f'been added to {msg}',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            query.objects.create(user=user, recipe=recipe)
            serializer = FavouriteAndShoppingCartSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                data={'errors': f'the recipe is not in {msg}'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Method of interaction with favorite recipes."""

        return self.addition_and_removal(request, pk, Favourite, 'favorites')

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """Method of interaction with shopping cart."""

        return self.addition_and_removal(
            request,
            pk,
            ShoppingCart,
            'shopping cart',
        )

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Method for downloading ingredients from the shopping cart."""

        user = request.user
        if not user.shopping_carts.exists():
            return Response(
                data={'errors': 'the shopping cart is empty'},
                status=status.HTTP_404_NOT_FOUND,
            )
        ingredients = Ingredient.objects.filter(
            ingredient_in_recipes__recipe__shopping_carts__user=user,
        ).values(
            'name',
            'measurement_unit',
        ).annotate(
            amount=Sum('ingredient_in_recipes__amount'),
        )
        shopping_cart = [''.join(
            f'{ingredient["name"]} '
            f'({ingredient["measurement_unit"]}) - '
            f'{ingredient["amount"]}\n'
        ) for ingredient in ingredients]
        return HttpResponse(shopping_cart, content_type='text/plain')
