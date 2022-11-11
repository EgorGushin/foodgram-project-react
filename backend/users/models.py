from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, EmailField, ManyToManyField,
                              ForeignKey, Model, CASCADE, DateTimeField,
                              UniqueConstraint)


class CustomUser(AbstractUser):
    username = CharField(
        verbose_name='Nickname',
        max_length=150,
        unique=True,
        help_text='Укажите username от 3 до 150 букв',
    )
    email = EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
        help_text='Введите адрес электронной почты'
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    password = CharField(
        verbose_name='password',
        max_length=150
    )
    subscribe = ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}: {self.email}'


class Follow(Model):
    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='follower'
    )
    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='following'
    )
    subscription_date = DateTimeField(
        auto_now=True,
        verbose_name='Дата подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='follow_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
