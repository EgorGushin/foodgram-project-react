from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Purchase, Recipe
from recipes.serializers import (CreateUpdateRecipeSerializer,
                                 FavoritesSerializer, ListRecipeSerializer,
                                 PurchaseSerializer, IngredientInRecipe)
from utils.filters import RecipeFilter
from utils.paginators import CustomPagination
from utils.permissions import IsOwnerOrAdminOrReadOnly

from ingredients.models import Ingredient


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated, ),
    )
    def set_favorite(self, request, pk=id):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoritesSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorite, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated, ),
    )
    def set_shopping_cart(self, request, pk=None):
        user = self.request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            in_shopping_cart = Purchase.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = PurchaseSerializer(in_shopping_cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        in_shopping_cart = get_object_or_404(
            Purchase,
            user=user,
            recipe__id=pk
        )
        in_shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        queryset = self.get_queryset()
        cart_objects = Purchase.objects.filter(user=request.user)
        recipes = queryset.filter(purchases__in=cart_objects)
        ingredients = IngredientInRecipe.objects.filter(recipes__in=recipes)
        ing_types = Ingredient.objects.filter(
            ingredients_amount__in=ingredients
        ).annotate(total=Sum('ingredients_amount__amount'))

        lines = [f'{ing_type.name}, {ing_type.total}'
                 f' {ing_type.measurement_unit}' for ing_type in ing_types]
        filename = 'shopping_ingredients.txt'
        response_content = '\n'.join(lines)
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
