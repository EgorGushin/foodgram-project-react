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


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListRecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
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
        permission_classes=(IsAuthenticated,),
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

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__purchases__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        text = 'C?????????? ??????????????: \n'
        for ingredients in shopping_cart:
            name, measurement_unit, amount = ingredients
            text += f'{name}: {amount} {measurement_unit}\n'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response
