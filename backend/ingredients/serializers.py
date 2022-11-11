from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import AmountIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.SerializerMethodField(read_only=True)
    measurement_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_ingredient(self, ingredient_id):
        return get_object_or_404(Ingredient, id=ingredient_id)

    def get_name(self, amount):
        return self.get_ingredient(amount.ingredient.id).name

    def get_measurement_unit(self, amount):
        return self.get_ingredient(amount.ingredient.id).measurement_unit
