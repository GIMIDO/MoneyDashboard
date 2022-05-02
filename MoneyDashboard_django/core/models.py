from operator import mod
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


class Currency(models.Model):

    user = models.ForeignKey(User,verbose_name='User',on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Currency',max_length=255)
    coef = models.FloatField(verbose_name='Coefficient')

    def __str__(self) -> str:
        return f'{self.title} [{self.coef}]'

class Wallet(models.Model):

    user = models.ForeignKey(User,verbose_name='User',on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency,verbose_name='Currency',on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Wallet',max_length=255)
    start_amount = models.FloatField(verbose_name='Start amount')

    def __str__(self) -> str:
        return f'{self.title} {self.currency}'


class Category(models.Model):

    title = models.CharField(verbose_name='Category',max_length=255)
    user = models.ForeignKey(User,verbose_name='User',on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet,verbose_name='Wallet',on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.title}'
        

class Action(models.Model):

    INCREASE = 'increase'
    SPENDING = 'spending'

    TYPE_CHOICES = (
        (INCREASE, 'Increase'),
        (SPENDING, 'Spending')
    )

    user = models.ForeignKey(User,verbose_name='User',on_delete=models.CASCADE)
    category = models.ForeignKey(Category,verbose_name='Category',on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet,verbose_name='Wallet',on_delete=models.CASCADE)
    title = models.CharField(max_length=255,verbose_name='Name')
    money = models.FloatField(verbose_name='Price')
    date = models.DateField(verbose_name='Date',default=timezone.now)
    action_type = models.CharField(verbose_name='Action type',choices=TYPE_CHOICES,max_length=8)                         
    created_at = models.DateTimeField(auto_now=True,verbose_name='Created at')

    def __str__(self) -> str:
        return f'{self.title} ({self.category}) {self.money} [{self.user.username}]'


class FamilyAccess(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    first_name = models.CharField(verbose_name='name', null=True, max_length=255)
    last_name = models.CharField(verbose_name='surname', null=True, max_length=255)
    avatar = models.ImageField(verbose_name='Avatar', default=None, null=True)
    bio = models.TextField(verbose_name='BIO', null=True)
