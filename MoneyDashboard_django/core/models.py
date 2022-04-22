from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


class Category(models.Model):

    title = models.CharField(verbose_name='Category', max_length=255)
    user = models.ForeignKey(User, verbose_name='User',
                                   on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.title}'


class Action(models.Model):

    INCREASE = 'increase'
    SPENDING = 'spending'

    TYPE_CHOICES = (
        (INCREASE, 'Increase'),
        (SPENDING, 'Spending')
    )

    user = models.ForeignKey(User, verbose_name='User',
                                   on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='Category',
                                           on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Name')
    money = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')
    date = models.DateField(verbose_name='Date', default=timezone.now)
    action_type = models.CharField(verbose_name='Action type', choices=TYPE_CHOICES, max_length=8)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Created at')

    def __str__(self) -> str:
        return f'{self.title} ({self.category}) {self.money} [{self.user.username}]'