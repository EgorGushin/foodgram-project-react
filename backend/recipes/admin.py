from django.contrib import admin

from recipes.models import Recipe

from recipes.models import Favorite

from recipes.models import Purchase, AmountIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorited')

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
