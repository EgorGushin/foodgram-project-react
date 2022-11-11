from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from ingredients.views import IngredientViewSet
from recipes.views import RecipeViewSet
from tags.views import TagViewSet
from users.views import CustomUserViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth', include('djoser.urls.authtoken'))
]

urlpatterns += router.urls
