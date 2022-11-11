from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import FollowRecipeSerializer
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed'

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user,
                                     author=obj.id).exists()


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD, settings.USER_ID_FIELD
                  ) + tuple(User.REQUIRED_FIELDS)
        read_only_fields = (settings.LOGIN_FIELD,)


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD,
                  settings.USER_ID_FIELD,
                  "password",
                  ) + tuple(User.REQUIRED_FIELDS)


class CustomSetPasswordSerializer(SetPasswordSerializer):
    class Meta:
        fields = ('password',)


class ShowFollowerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user,
                                     author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
