from dataclasses import fields
from django import forms
from django.contrib.auth.models import User

from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class LoginForm(forms.Form):

    class Meta:
        model = User
        fields = ['username', 'password']

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Пользователь {username} не найден')
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Логин {username} уже занят')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data


class ActionForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'maxlength':'150', 'type':'text'}))
    money = forms.CharField(widget=forms.TextInput(
        attrs={'min':'0.01','max': '9999999','type': 'number', 'step':'0.01'}))

    class Meta:
        model = Action
        fields = ['title','category','money','date','action_type']
        widgets = {
            'date': DateInput()
        }

    def __init__(self, wallet_pk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['category'].queryset = Category.objects.filter(wallet=wallet_pk)


class CategoryForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'maxlength':'25', 'type':'text'}))

    class Meta:
        model = Action
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'


class WalletForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'maxlength':'255', 'type':'text'}))
    start_amount = forms.CharField(widget=forms.TextInput(
        attrs={'min':'-9999999','max': '9999999','type': 'number', 'step':'0.01'}))

    class Meta:
        model = Wallet
        fields = ['title','currency','start_amount']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['currency'].queryset = Currency.objects.filter(user=user)


class CurrencyForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'maxlength':'3', 'type':'text'}))

    class Meta:
        model = Currency
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'


class FamilyAccessForm(forms.ModelForm):

    user1 = forms.CharField(widget=forms.TextInput(
        attrs={'type': 'text'}))

    class Meta:
        model = FamilyAccess
        fields = ['user1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user1'].label = 'Username'

    def clean(self):
        test_user = self.cleaned_data['user1']
        print(test_user)
        if not User.objects.filter(username=test_user).exists():
            raise forms.ValidationError(f'Логин {test_user} не найден!')
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)
    bio = forms.CharField(widget=forms.TextInput(
        attrs={'type':'text'}))
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'maxlength':'255', 'type':'text'}))

    class Meta:
        model = Objective
        fields = ['title', 'currency', 'target_amount', 'now_amount']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(user=user)


class MoneyTransferForm(forms.Form):

    wallets = forms.ModelChoiceField(queryset=Wallet.objects.all())
    money = forms.CharField(widget=forms.TextInput(
        attrs={'min':'0.01','max': '9999999','type': 'number', 'step':'0.01'}))

    def __init__(self, pk, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallets'].queryset = Wallet.objects.exclude(pk=pk).filter(user=user)


class ObjectiveTransferForm(forms.Form):

    wallets = forms.ModelChoiceField(queryset=Wallet.objects.all())
    money = forms.CharField(widget=forms.TextInput(
        attrs={'min':'0.01','max': '9999999','type': 'number', 'step':'0.01'}))

    def __init__(self, currency, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallets'].queryset = Wallet.objects.filter(user=user, currency=currency)
        self.fields['wallets'].label = 'From wallet'
