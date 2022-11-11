from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'
