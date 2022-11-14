from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ingredients.models import Ingredient
from recipes.models import AmountIngredient, Favorite, Purchase, Recipe
from recipes.serializers import (CreateUpdateRecipeSerializer,
                                 ListRecipeSerializer)
from utils.filters import RecipeFilter
from utils.paginators import CustomPagination
from utils.permissions import IsOwnerOrAdminOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return CreateUpdateRecipeSerializer
        return ListRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def _recipe_post_method(self, request, AnySerializer, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = AnySerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _recipe_delete_method(self, request, AnyModel, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            AnyModel, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.recipe_post_method(
                request, FavoritesSerializer, pk
            )

    @favorite.mapping.delete
    def delete_favorite(self, requests, pk=None):
        return self.recipe_delete_method(
            requests, Favorite, pk
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.recipe_post_method(
                request, PurchaseSerializer, pk
            )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.recipe_delete_method(
            request, Purchase, pk
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=[IsAuthenticated]
    )
    def get_ingredients_for_download(self, request):
        queryset = self.get_queryset()
        cart_objects = Purchase.objects.filter(user=request.user)
        recipes = queryset.filter(purchases__in=cart_objects)
        ingredients = AmountIngredient.objects.filter(recipes__in=recipes)
        ing_types = Ingredient.objects.filter(
            ingredients_amount__in=ingredients
        ).annotate(total=Sum('ingredients_amount__amount'))
        return ing_types

    def dowload_shopping_cart(self, ing_types):
        lines = [f'{ing_type.name}, {ing_type.total}'
                 f'{ing_type.measurement_unit}' for ing_type in ing_types]
        filename = 'shopping_ingredients.txt'
        response_content = '\n'.join(lines)
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
