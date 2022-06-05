from django import forms
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import password_validation


class DateInput(forms.DateInput):
    '''DateInput Form'''

    input_type = 'date'


class LoginForm(forms.Form):
    '''Login Form'''

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','password']

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'User {username} not found!')
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password!')
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    '''Registration Form'''

    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','password','confirm_password']

    # validate username
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Username "{username}" already exists!')
        return username

    # validate password and send form data
    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        password_validation.validate_password(password)
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')
        return self.cleaned_data


class ActionForm(forms.ModelForm):
    '''Action form'''

    title = forms.CharField(widget=forms.TextInput(attrs={
                'maxlength':'150',
                'type':'text'}))

    money = forms.CharField(widget=forms.TextInput(attrs={
                'min':'0.01',
                'max': '9999999',
                'type': 'number',
                'step':'0.01'}))

    class Meta:
        model = Action
        fields = ['title','category','money','date','action_type']
        widgets = {'date': DateInput()}

    def __init__(self, wallet_pk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['category'].queryset = Category.objects.filter(wallet=wallet_pk)


class CategoryForm(forms.ModelForm):
    '''Category Form'''

    title = forms.CharField(widget=forms.TextInput(attrs={
                'maxlength':'25',
                'type':'text'}))
    color = forms.CharField(label='Color',max_length=7,widget=forms.TextInput(attrs={
                'type': 'color',
                'id':'color-picker'}))

    class Meta:
        model = Action
        fields = ['title', 'color']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'


class WalletForm(forms.ModelForm):
    '''Wallet Form'''

    title = forms.CharField(widget=forms.TextInput(attrs={
                'maxlength':'255',
                'type':'text'}))
    start_amount = forms.CharField(widget=forms.TextInput(attrs={
                'min':'-9999999',
                'max': '9999999',
                'type': 'number',
                'step':'0.01'}))

    class Meta:
        model = Wallet
        fields = ['title','currency','start_amount']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['currency'].queryset = Currency.objects.filter(user=user)


class CurrencyForm(forms.ModelForm):
    '''Currency Form'''

    title = forms.CharField(widget=forms.TextInput(attrs={
                'maxlength':'3',
                'type':'text'}))

    class Meta:
        model = Currency
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'


class FamilyAccessForm(forms.ModelForm):
    '''Family Access Form'''

    user1 = forms.CharField(widget=forms.TextInput(attrs={
                'type': 'text'}))

    class Meta:
        model = FamilyAccess
        fields = ['user1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user1'].label = 'Username'

    # validate user and send form data
    def clean(self):
        test_user = self.cleaned_data['user1']
        if not User.objects.filter(username=test_user).exists():
            raise forms.ValidationError(f'Username {test_user} not found!')
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    '''Profile Form'''
    
    avatar = forms.ImageField(required=False,widget=forms.FileInput)
    bio = forms.CharField(required=False,widget=forms.TextInput(attrs={
                'type':'text'}))
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['first_name','last_name','avatar','bio','email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveForm(forms.ModelForm):
    '''Objective Form'''

    title = forms.CharField(widget=forms.TextInput(attrs={
                'maxlength':'255',
                'type':'text'}))

    class Meta:
        model = Objective
        fields = ['title','currency','target_amount','now_amount']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.filter(user=user)


class MoneyTransferForm(forms.Form):
    '''Money Transfering Form'''

    wallets = forms.ModelChoiceField(queryset=Wallet.objects.all())
    money = forms.CharField(widget=forms.TextInput(attrs={
                'min':'0.01',
                'max': '9999999',
                'type': 'number',
                'step':'0.01'}))

    def __init__(self, pk, user, currency, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallets'].queryset = Wallet.objects.exclude(pk=pk).filter(user=user, currency=currency)


class ObjectiveTransferForm(forms.Form):
    '''Objective Trnsfer Form'''

    wallets = forms.ModelChoiceField(queryset=Wallet.objects.all())
    money = forms.CharField(widget=forms.TextInput(attrs={
                'min':'0.01',
                'max': '9999999',
                'type': 'number',
                'step':'0.01'}))

    def __init__(self, currency, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallets'].queryset = Wallet.objects.filter(user=user,currency=currency)
        self.fields['wallets'].label = 'From wallet'


class WalletMessageForm(forms.ModelForm):
    '''Wallet Message Form (Notes)'''

    message = forms.CharField(required=True,widget=forms.TextInput(attrs={
                'type':'text'}))

    class Meta:
        model = WalletMessage
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
