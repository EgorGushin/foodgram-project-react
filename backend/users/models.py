from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, ManyToManyField


class CustomUser(AbstractUser):
    username = CharField(
        verbose_name='Уникальный username',
        max_lenght=150,
        unique=True,
        help_text='Укажите username не более 150 символов'
    )
    password = CharField(
        verbose_name='Пароль',
        max_lenght=150,
        help_text='Пароль для входа'
    )
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_lenght=254,
        unique=True,
        help_text='Введите адрес электронной почты'
    )
    first_name = CharField(
        verbose_name='Ваше имя',
        max_lenght=150,
        help_text='Введите ваше имя'
    )
    last_name = CharField(
        verbose_name='Ваша фамилия',
        max_lenght=150,
        help_text='Введите вашу фамилию'
    )
    subscribe = ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribes',
        to='self',
        symmetrical=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}: {self.email}'
