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

    money = forms.CharField(widget=forms.TextInput(
        attrs={'min':'0.01','max': '9999999','type': 'number', 'step':'0.01'}))

    class Meta:
        model = Action
        fields = ['title','category','money','date','action_type']
        widgets = {
            'date': DateInput()
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['category'].queryset = Category.objects.filter(user=user)


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'