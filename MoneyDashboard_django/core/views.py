from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.core import serializers
from .models import *
from .forms import *
from .utils import *
from .mixins import *

# home
class HomePage(AuthUserMixin, View):

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user)
        currencies = Currency.objects.filter(user=request.user)
        f_wallets = FamilyAccess.objects.filter(user=request.user)
        context = {'wallets': wallets, 'currencies': currencies, 'f_wallets': f_wallets}
        return render(request, 'home.html', context)

# auth
class LoginView(View):

    def get(self, request):
        form = LoginForm(request.POST or None)
        context = {'form': form, 'auth_check': 1,
                   'page_title':'Sign In', 'button_title':'Sign Up'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'auth_check': 1,
                   'page_title':'Sign In', 'button_title':'Sign Up'}
        return render(request, 'page_manager.html', context)

class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm(request.POST or None)
        context = {'form': form, 'auth_check': 2,
                   'page_title':'Sign Up', 'button_title':'Sign In'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():

            created_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'])
            created_user.save()

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])

            Profile.objects.create(user=created_user)

            login(request, user)
            
            messages.add_message(request, messages.SUCCESS, "Registation completed!")
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'auth_check': 2,
                   'page_title':'Sign Up', 'button_title':'Sign In'}
        return render(request, 'page_manager.html', context)

class LogoutView(View):
    
    def get(self, request):
        logout(request)
        return redirect('login')

# search
class SearchResultsView(AuthUserMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            q_from = self.request.GET.get("from")
            q_to = self.request.GET.get("to")
            q_category = self.request.GET.get("category")
            actions = search_actions(kwargs.get('wallet_pk'), q_from, q_to, q_category)

            if q_category:
                category_out = Category.objects.get(id=q_category)
            else:
                category_out = None

            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'q_from': q_from, 'q_to': q_to, 'q_category': q_category, 'category_out': category_out,
                'button_url': 'wallet-page', 'b_u2': kwargs.get('wallet_pk'), 'button_title': 'Back',
                'wallet': wallet, 'total_amount': calc_amount(actions), 'page_obj': page_obj}
            return render(request, 'search_actions.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

# download
class DownloadJSON(AuthUserMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            q_wallet = kwargs.get('wallet_pk')
            q_from = request.GET.get('from')
            q_to = request.GET.get('to')
            q_category = request.GET.get("category")
            actions = search_actions(q_wallet, q_from, q_to, q_category)
            json_str = serializers.serialize('json', actions,
                fields=('title', 'user', 'category', 'wallet', 'money', 'action_type', 'date'))
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=actions.json'
            return response
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

# action
class CreateAction(AuthUserMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            form = ActionForm(kwargs.get('wallet_pk'), request.POST or None)
            context = {'form': form, 'go_next': get_next_link(request),
                       'page_title':'Create action', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))


    def post(self, request, **kwargs):
        form = ActionForm(kwargs.get('wallet_pk'), request.POST or None)
        if form.is_valid():
            action = Action.objects.create(
                user=request.user,
                category=form.cleaned_data['category'],
                wallet=Wallet.objects.get(pk=kwargs.get('wallet_pk')),
                title=form.cleaned_data['title'],
                money=form.cleaned_data['money'],
                date=form.cleaned_data['date'],
                action_type=form.cleaned_data['action_type'])
            action.save()
            calc_amount_wallet('create',action, kwargs.get('wallet_pk'))
            messages.add_message(request, messages.SUCCESS, "Added action: {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create action', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateAction(AuthUserMixin, View):

    def get(self, request, **kwargs):
        if (Action.objects.get(pk=kwargs.get('pk')).user == request.user) or (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            action = Action.objects.get(pk=(kwargs.get('pk')))
            form = ActionForm(kwargs.get('wallet_pk'), request.POST or None, instance=action)
            context = {'form': form,'go_next': get_next_link(request),
                       'page_title':'Update action', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        action = Action.objects.get(pk=kwargs.get('pk'))
        old_action = Action.objects.get(pk=kwargs.get('pk'))
        form = ActionForm(kwargs.get('wallet_pk'), request.POST, instance=action)
        if form.is_valid():
            form.save()
            calc_amount_wallet_update(action, kwargs.get('wallet_pk'), old_action)
            messages.add_message(request, messages.SUCCESS, "Updated action: {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = ActionForm(instance=action)
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Update action', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

# category
class CreateCategory(AuthUserMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            form = CategoryForm(request.POST or None)
            context = {'form': form, 'go_next': get_next_link(request), 'page_title':'Create category', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))


    def post(self, request, **kwargs):


        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            Category.objects.create(title=form.cleaned_data['title'], wallet=wallet,  user=request.user)
            messages.add_message(request, messages.SUCCESS, "Added category: {}!".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create category',  'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateCategory(AuthUserMixin, View):

    def get(self, request, **kwargs):
        if (Category.objects.get(pk=kwargs.get('pk')).user == request.user) or (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            category = Category.objects.get(pk=kwargs.get('pk'))
            form = CategoryForm(request.POST or None, instance=category)
            context = {'form': form, 'go_next': get_next_link(request),
                       'page_title':'Update category', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


    def post(self, request, **kwargs):
        category = Category.objects.get(pk=kwargs.get('pk'))
        form = CategoryForm(request.POST or None, instance=category)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Updated category: {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CategoryForm(instance=category)

        context = {'form': form,'go_next': get_next_link(request),
                   'page_title':'Update category','button_title':'Back'}
        return render(request, 'page_manager.html', context)

class CategoryManager(AuthUserMixin, View):
    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            categories = Category.objects.filter(wallet=(kwargs.get('wallet_pk')))

            paginator = Paginator(categories, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {'wallet': wallet, 'page_obj': page_obj, 'count': categories.count}
            return render(request, 'category_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))
    pass

# wallet
class CreateWallet(AuthUserMixin, View):

    def get(self, request):
        form = WalletForm(request.user,
                          request.POST or None)
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create wallet', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = WalletForm(request.user, request.POST or None)
        if form.is_valid():
            Wallet.objects.create(user=request.user,
                                  title=form.cleaned_data['title'],
                                  currency=form.cleaned_data['currency'],
                                  start_amount=form.cleaned_data['start_amount'])
            messages.add_message(request, messages.SUCCESS, "Added wallet: {}!".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create wallet', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateWallet(AuthUserMixin, View):

    def get(self, request, **kwargs):
        if (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            wallet = Wallet.objects.get(user=request.user, pk=(kwargs.get('wallet_pk')))
            form = WalletForm(request.user, request.POST or None, instance=wallet)
            context = {'form': form, 'go_next': get_next_link(request),
                       'page_title':'Update wallet', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet = Wallet.objects.get(user=request.user, pk=(kwargs.get('wallet_pk')))
        form = WalletForm(request.user, request.POST or None, instance=wallet)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,"Updated wallet: {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CategoryForm(instance=wallet)
        context = {'form': form,'go_next': get_next_link(request),
                   'page_title':'Update wallet', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class WalletView(AuthUserMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) or wallet.user == request.user:
            actions = Action.objects.filter(wallet=(kwargs.get('wallet_pk'))).order_by('-date', '-created_at')
            categories = Category.objects.filter(wallet=(kwargs.get('wallet_pk')))

            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {'wallet': wallet, 'total_amount': wallet.start_amount, 'page_obj': page_obj, 'count': actions.count, 'categories': categories}
            return render(request, 'wallet.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

# currency
class CreateCurrency(AuthUserMixin, View):

    def get(self, request):
        form = CurrencyForm(request.POST or None)
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create currency','button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = CurrencyForm(request.POST or None)
        if form.is_valid():
            Currency.objects.create(user=request.user, title=form.cleaned_data['title'],coef=form.cleaned_data['coef'])
            messages.add_message(request, messages.SUCCESS, "Added currency: {} [{}]!".format(form.cleaned_data['title'],
                                                                                              form.cleaned_data['coef']))
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Create currency', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateCurrency(AuthUserMixin, View):
    
    def get(self, request, **kwargs):
        if (Currency.objects.get(pk=kwargs.get('pk')).user == request.user):
            currency = Currency.objects.get(user=request.user, pk=(kwargs.get('pk')))
            form = CurrencyForm(request.POST or None,  instance=currency)
            context = {'form': form, 'go_next': get_next_link(request),
                       'page_title':'Update currency', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        currency = Currency.objects.get(user=request.user, pk=(kwargs.get('pk')))
        form = CurrencyForm(request.POST or None, instance=currency)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Updated currency: {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CurrencyForm(instance=currency)
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Update currency', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

# delete
class DeleteModelView(AuthUserMixin, View):

    MODEL_CHOISE = {
        'wallet': Wallet,
        'currency': Currency,
        'familyAccess': FamilyAccess
    }

    def get(self, request, **kwargs):
        self.MODEL_CHOISE[kwargs['model']].objects.get(pk=(kwargs.get('pk')), user=request.user).delete()
        messages.add_message(request, messages.WARNING,"Deleted {}".format(kwargs.get('model')))
        return HttpResponseRedirect(get_next_link(request))

class DeleteActionView(AuthUserMixin, View):
    def get(self, request, **kwargs):
        if (Action.objects.get(pk=kwargs.get('pk')).user == request.user) or (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            action = Action.objects.get(pk=kwargs.get('pk'))
            calc_amount_wallet('delete', action, action.wallet.pk)
            messages.add_message(request, messages.SUCCESS, "Deleted action {}".format(action.title))
            action.delete()
            return HttpResponseRedirect(get_next_link(request))
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

class DeleteCategoryView(AuthUserMixin, View):
    def get(self, request, **kwargs):
        if (Category.objects.get(pk=kwargs.get('pk')).user == request.user) or (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            category = Category.objects.get(pk=(kwargs.get('pk')))
            actions = Action.objects.filter(category=kwargs.get('pk'))
            for action in actions:
                calc_amount_wallet('delete', action, action.wallet.pk)
            messages.add_message(request,messages.SUCCESS,"Deleted category {}".format(category.title))
            category.delete()
            return HttpResponseRedirect(get_next_link(request))
        else:
            messages.add_message(request,messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

# family access
class FamilyAccessView(AuthUserMixin, OwnerAccessMixin, View):

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(user=request.user, pk=kwargs.get('wallet_pk'))
        t_wallet = FamilyAccess.objects.filter(wallet=wallet)
        context = { 'wallet_pk': wallet.pk,'t_wallet': t_wallet, 'go_next': get_next_link(request)}
        return render(request, 'wallet_access.html', context)

class DeleteAccessView(AuthUserMixin, OwnerAccessMixin, View):

    def get(self, request, **kwargs):
        instance = FamilyAccess.objects.get(
            wallet=Wallet.objects.get(user=request.user, pk=kwargs.get('wallet_pk')),
            user=User.objects.get(username=kwargs.get('user')))
        messages.add_message(request, messages.WARNING, "Deleted user: {}!".format(instance.user.username))
        instance.delete()
        return redirect(get_next_link(request))

class AddAccessView(AuthUserMixin, OwnerAccessMixin, View):

    def get(self, request, **kwargs):
        form = FamilyAccessForm(request.POST or None)
        context = {'form': form, 'go_next': get_next_link(request), 
                   'page_title': 'Add user', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        form = FamilyAccessForm(request.POST or None)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['user1'])
            FamilyAccess.objects.create(user=user,wallet=Wallet.objects.get(user=request.user, pk=kwargs.get('wallet_pk')))
            messages.add_message(request, messages.SUCCESS, "Added user: {}".format(form.cleaned_data['user1']))
            return HttpResponseRedirect(get_next_link(request))
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Add user', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)

# profile
class ProfileView(AuthUserMixin, View):

    def get(self, request, **kwargs):
        user_profile = User.objects.get(username=kwargs.get('username'))
        profile = Profile.objects.get(user=user_profile)
        # messages.add_message(request, messages.SUCCESS, "User profile: {}".format(kwargs.get('username')))

        context = {'go_next': get_next_link(request), 'profile': profile,
                   'button_title':'Back'}
        return render(request, 'profile.html', context)

class ProfileUpdate(AuthUserMixin, View):

    def get(self, request, **kwargs):
        profile = Profile.objects.get(user=User.objects.get(username=kwargs.get('username')))
        if profile.user == request.user:
            form = ProfileForm(request.POST or None, instance=profile)
            context = {'form':form ,'go_next': get_next_link(request),
                       'page_title':'Profile update', 'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        profile = Profile.objects.get(user=User.objects.get(username=kwargs.get('username')))
        form = ProfileForm(request.POST or None, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = ProfileForm(instance=profile)
        context = {'form': form, 'go_next': get_next_link(request),
                   'page_title':'Update profile', 'button_title':'Back'}
        return render(request, 'page_manager.html', context)