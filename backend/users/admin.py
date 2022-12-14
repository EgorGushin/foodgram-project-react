from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('id', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')


admin.site.unregister(Group)
