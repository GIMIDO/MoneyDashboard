from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from colorfield.fields import ColorField


User = get_user_model()


class Currency(models.Model):
    '''
    Currency model in database
    '''

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE)

    title = models.CharField(
        verbose_name='Currency', max_length=3)

    def __str__(self) -> str:
        return f'{self.title}'


class Wallet(models.Model):
    '''
    Wallet model in database
    '''

    user = models.ForeignKey(
        User,verbose_name='User', on_delete=models.CASCADE)

    currency = models.ForeignKey(
        Currency, verbose_name='Currency', on_delete=models.CASCADE)

    title = models.CharField(
        verbose_name='Wallet', max_length=255)

    start_amount = models.DecimalField(
        verbose_name='Start amount', max_digits=9, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.title} {self.currency} {self.start_amount}'


class Category(models.Model):
    '''
    Category model in database
    '''

    title = models.CharField(
        verbose_name='Category', max_length=25)

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE)

    wallet = models.ForeignKey(
        Wallet, verbose_name='Wallet',
        on_delete=models.CASCADE)

    color = ColorField(
        verbose_name='Color')

    def __str__(self) -> str:
        return f'{self.title}'
        

class Action(models.Model):
    '''
    Action model in database
    '''

    INCREASE = 'increase'
    SPENDING = 'spending'

    TYPE_CHOICES = (
        (INCREASE, 'Increase'),
        (SPENDING, 'Spending')
    )

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE)

    category = models.ForeignKey(
        Category, verbose_name='Category', on_delete=models.CASCADE)

    wallet = models.ForeignKey(
        Wallet, verbose_name='Wallet', on_delete=models.CASCADE)

    title = models.CharField(
        max_length=150, verbose_name='Name')

    money = models.DecimalField(
        verbose_name='Price', max_digits=9, decimal_places=2)

    date = models.DateField(
        verbose_name='Date', default=timezone.now)

    action_type = models.CharField(
        verbose_name='Action type', choices=TYPE_CHOICES, max_length=8)  

    created_at = models.DateTimeField(
        auto_now=True, verbose_name='Created at')

    def __str__(self) -> str:
        return f'{self.title} ({self.category}) {self.money} [{self.user.username}]'


class FamilyAccess(models.Model):
    '''
    Family Access model in database
    '''

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )


class Profile(models.Model):
    '''
    Profile model in database
    '''

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE)

    first_name = models.CharField(
        verbose_name='name', blank=True, max_length=255)

    last_name = models.CharField(
        verbose_name='surname', blank=True, max_length=255)

    avatar = models.ImageField(
        verbose_name='Avatar', default=None, blank=True)

    bio = models.TextField(
        verbose_name='BIO', blank=True)

    email = models.EmailField(
        verbose_name='Email', max_length=255)


class Objective(models.Model):
    '''
    Objective model in database
    '''

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE)

    currency = models.ForeignKey(
        Currency,verbose_name='Currency',on_delete=models.CASCADE)

    title = models.CharField(
        verbose_name='title', max_length=255)

    target_amount = models.DecimalField(
        verbose_name='target', max_digits=9, decimal_places=2)

    now_amount = models.DecimalField(
        verbose_name='now', default=0, max_digits=9, decimal_places=2)
    
    def __str__(self) -> str:
        return f'[{self.user.username}] {self.title} {self.now_amount}\
            /{self.target_amount} {self.currency.title}'


class LogTable(models.Model):
    '''
    Model for logs in database
    '''

    DELETE = 'delete'
    UPDATE = 'update'
    CREATE = 'create'

    TYPE_CHOICES = (
        (DELETE, 'Delete'),
        (UPDATE, 'Update'),
        (CREATE, 'Create')
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    message = models.TextField(
        verbose_name='Message', blank=True
    )

    created_at = models.DateTimeField(
        auto_now=True, verbose_name='Created at'
    )

    a_type = models.CharField(
        verbose_name="Type", choices=TYPE_CHOICES, max_length=255
    )

    def __str__(self) -> str:
        return f'{self.user} | {self.created_at} | {self.message}'


class WalletMessage(models.Model):
    '''
    Wallet notes in database
    '''

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE
    )

    message = models.CharField(
        verbose_name='Message', max_length=150
    )

    def __str__(self) -> str:
        return f'{self.wallet} | {self.message}'