from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from ingredients.serializers import IngredientSerializer
from recipes.models import Recipe, Favorite, Purchase, \
    AmountIngredient
from tags.models import Tag
from tags.serializers import TagSerializer, TagListField


class ListRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        read_only=True,
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'tags')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Purchase.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    tags = TagListField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def create(self, validate_data):
        tags = validate_data.pop('tags')
        image = validate_data.pop('image')
        ingredients = validate_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validate_data)
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_amount, status = (
                AmountIngredient.objects.get_or_create(**ingredient)
            )
            ingredients_list.append(ingredient_amount)
        recipe.ingredients.set(ingredients_list)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_amount, status = (
                AmountIngredient.objects.get_or_create(**ingredient)
            )
            ingredients_list.append(ingredient_amount)
        instance.ingredients.set(ingredients_list)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return ListRecipeSerializer(instance, context=self.context).data


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoritesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ReadOnlyField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'image', 'cooking_time', 'user', 'recipe')
        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}}

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'],
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return data


class PurchaseSerializer(FavoritesSerializer):
    class Meta:
        model = Purchase

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        purchase_exists = Purchase.objects.filter(
            user=request.user,
            recipe_id=recipe_id
        ).exists()

        if purchase_exists:
            raise serializers.ValidationError(
                'В списке покупок уже есть такой рецепт.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowRecipeSerializer(instance.recipe,
                                      context=context).data