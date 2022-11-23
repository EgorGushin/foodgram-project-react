from django.contrib import admin

from recipes.models import (AmountIngredient, Favorite, Purchase, Recipe,
                            IngredientInRecipe)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorited')
    search_fields = ('name', 'author', 'tags')
    inlines = (IngredientInRecipeInline,)
    exclude = ('ingredients',)

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(AmountIngredient)
