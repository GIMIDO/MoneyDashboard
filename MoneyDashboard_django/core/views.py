from locale import currency
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.core import serializers
from .models import *
from .forms import *
from .utils import *


class HomePage(View):

    def get(self, request):
        if request.user.is_authenticated:
            wallets = Wallet.objects.filter(user=request.user)
            currencies = Currency.objects.filter(user=request.user)

            context = {
                'wallets': wallets,
                'currencies': currencies
            }
            return render(request, 'home.html', context)
        else:
            return HttpResponseRedirect('sign-in/')


class WalletView(View):

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            actions = Action.objects.filter(user=request.user,
                                            wallet=(kwargs.get('pk'))).order_by('-date', '-created_at')
            categories = Category.objects.filter(user=request.user,
                                                 wallet=(kwargs.get('pk')))
            wallet = Wallet.objects.get(user=request.user,
                                        pk=(kwargs.get('pk')))

            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'wallet': wallet,
                'total_amount': calc_amount(actions, wallet.start_amount),
                'page_obj': page_obj,
                'categories':categories
                }
            return render(request, 'wallet.html', context)
        else:
            return HttpResponseRedirect('sign-in')


class LoginView(View):

    def get(self, request):
        form = LoginForm(request.POST or None)
        context = {'form': form,
                   'auth_check': 1,
                   'page_title':'Sign In', 
                   'button_title':'Sign Up'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,
                                password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {'form': form,
                   'auth_check': 1,
                   'page_title':'Sign In',
                   'button_title':'Sign Up'}
        return render(request, 'page_manager.html', context)

class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm(request.POST or None)
        context = {'form': form,
                   'auth_check': 2,
                   'page_title':'Sign Up',
                   'button_title':'Sign In'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'])
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            login(request, user)
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Registation completed!")
            return HttpResponseRedirect('/')
        context = {'form': form,
                   'auth_check': 2,
                   'page_title':'Sign Up',
                   'button_title':'Sign In'}
        return render(request, 'page_manager.html', context)


class SearchResultsView(View):

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('pk')
        wallet = Wallet.objects.get(user=request.user,
                                    pk=wallet_pk)

        q_from = self.request.GET.get("from")
        q_to = self.request.GET.get("to")
        q_category = self.request.GET.get("category")
        q_user = request.user
        actions = search_actions(wallet_pk, q_from, q_to, q_category, q_user)

        if q_category:
            category_out = Category.objects.get(id=q_category)
        else:
            category_out = None

        paginator = Paginator(actions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'q_from': q_from,
            'q_to': q_to,
            'q_category': q_category,
            'category_out': category_out,
            'button_url': 'wallet-page',
            'b_u2': wallet_pk,
            'button_title': 'Back',
            'wallet': wallet,
            'total_amount': calc_amount(actions, 0),
            'page_obj': page_obj
        }
        return render(request, 'search_actions.html', context)


class DownloadJSON(View):

    def get(self, request, **kwargs):
        q_wallet = kwargs.get('pk')
        q_from = request.GET.get('from')
        q_to = request.GET.get('to')
        q_category = request.GET.get("category")
        q_user = request.user
        actions = search_actions(q_wallet, q_from, q_to, q_category, q_user)
        json_str = serializers.serialize('json',
                                         actions,
                                         fields=('title',
                                                 'category',
                                                 'wallet',
                                                 'money',
                                                 'action_type',
                                                 'date'))
        response = HttpResponse(json_str, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=actions.json'

        return response


class CreateAction(View):

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('pk')
        form = ActionForm(request.user,
                          wallet_pk,
                          request.POST or None)
        next = request.GET.get('next')
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create action',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('pk')
        form = ActionForm(request.user,
                          wallet_pk,
                          request.POST or None)
        if form.is_valid():
            Action.objects.create(
                user=request.user,
                category=form.cleaned_data['category'],
                wallet=Wallet.objects.get(user=request.user,
                                          pk=wallet_pk),
                title=form.cleaned_data['title'],
                money=form.cleaned_data['money'],
                date=form.cleaned_data['date'],
                action_type=form.cleaned_data['action_type']
            )
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added action: {}"
                                 .format(form.cleaned_data['title']))
            next = request.GET.get('next')
            return HttpResponseRedirect(next)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create action',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateAction(View):

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        action = Action.objects.get(user=request.user,
                                    pk=(kwargs.get('action_pk')))

        next = request.GET.get('next')

        form = ActionForm(request.user,
                          wallet_pk,
                          request.POST or None,
                          instance=action)
        context = {'form': form,

                   'go_next': next,

                   'page_title':'Update action',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        action = Action.objects.get(user=request.user,
                                    pk=(kwargs.get('action_pk')))

        form = ActionForm(request.user,
                          wallet_pk,
                          request.POST,
                          instance=action)

        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Updated action: {}"
                                 .format(form.cleaned_data['title']))
                                 
            next = request.GET.get('next')
            return HttpResponseRedirect(next)
        else:
            form = ActionForm(instance=action)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Update action',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)


class CreateCategory(View):

    def get(self, request, **kwargs):
        next = request.GET.get('next')
        form = CategoryForm(request.POST or None)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create category',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('pk')
        next = request.GET.get('next')
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            Category.objects.create(user=request.user,
                                    title=form.cleaned_data['title'],
                                    wallet=Wallet.objects.get(user=request.user,
                                                              pk=wallet_pk))
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added category: {}!"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect(next)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create category', 
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateCategory(View):

    def get(self, request, **kwargs):
        next = request.GET.get('next')
        category = Category.objects.get(user=request.user,
                                        pk=(kwargs.get('pk')))
        form = CategoryForm(request.POST or None,
                            instance=category)
        context = {'form': form,

                   'go_next': next,
                   'page_title':'Update category',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        next = request.GET.get('next')

        category = Category.objects.get(user=request.user,
                                        pk=(kwargs.get('pk')))
        form = CategoryForm(request.POST or None,
                            instance=category)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Updated category: {}"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect(next)
        else:
            form = CategoryForm(instance=category)
        context = {'form': form,

                   'go_next': next,
                   'page_title':'Update category',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)


class CreateWallet(View):

    def get(self, request):
        next = request.GET.get('next')
        form = WalletForm(request.user,
                          request.POST or None)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create wallet',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        next = request.GET.get('next')
        form = WalletForm(request.user, request.POST or None)
        if form.is_valid():
            Wallet.objects.create(user=request.user,
                                  title=form.cleaned_data['title'],
                                  currency=form.cleaned_data['currency'],
                                  start_amount=form.cleaned_data['start_amount'],
                                  )
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added wallet: {}!"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect('/')
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create wallet', 
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateWallet(View):

    def get(self, request, **kwargs):
        next = request.GET.get('next')
        wallet = Wallet.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = WalletForm(request.user,
                          request.POST or None,
                          instance=wallet)
        context = {'form': form,

                   'go_next': next,
                   'page_title':'Update wallet',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        next = request.GET.get('next')
        wallet = Wallet.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = WalletForm(request.user,
                          request.POST or None,
                          instance=wallet)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Updated wallet: {}"
                                 .format(form.cleaned_data['title']))
            next = request.GET.get('next')
            return HttpResponseRedirect(next)
        else:
            form = CategoryForm(instance=wallet)
        context = {'form': form,

                   'go_next': next,
                   'page_title':'Update wallet',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)


class CreateCurrency(View):

    def get(self, request):
        next = request.GET.get('next')
        form = CurrencyForm(request.POST or None)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create currency',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        next = request.GET.get('next')
        form = CurrencyForm(request.POST or None)
        if form.is_valid():
            Currency.objects.create(user=request.user,
                                    title=form.cleaned_data['title'],
                                    coef=form.cleaned_data['coef']
                                    )
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added currency: {} [{}]!"
                                 .format(form.cleaned_data['title'],
                                         form.cleaned_data['coef']))
            return HttpResponseRedirect('/')
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Create currency', 
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

class UpdateCurrency(View):
    
    def get(self, request, **kwargs):
        next = request.GET.get('next')
        currency = Currency.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = CurrencyForm(request.POST or None,
                            instance=currency)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Update currency',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        next = request.GET.get('next')
        currency = Currency.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = CurrencyForm(request.POST or None,
                            instance=currency)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Updated currency: {}"
                                 .format(form.cleaned_data['title']))
            next = request.GET.get('next')
            return HttpResponseRedirect(next)
        else:
            form = CurrencyForm(instance=currency)
        context = {'form': form,
                   'go_next': next,
                   'page_title':'Update currency',
                   'button_title':'Back'}
        return render(request, 'page_manager.html', context)


class DeleteModelView(View):

    MODEL_CHOISE = {
        'category': Category,
        'action': Action,
        'wallet': Wallet,
        'currency': Currency
    }

    def get(self, request, **kwargs):
        messages.add_message(request,
                             messages.WARNING,
                             "Deleted action!")
        self.MODEL_CHOISE[kwargs['model']].objects.get(pk=(kwargs.get('pk')),
                                                       user=request.user).delete()
        return redirect(request.GET.get('next'))