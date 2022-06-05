from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.core import serializers
import decimal
from .models import *
from .forms import *
from .utils import *
from .mixins import *


class HomePage(AuthUserMixin, View):
    """Home page view"""

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user)
        currencies = Currency.objects.filter(user=request.user)
        f_wallets = FamilyAccess.objects.filter(user=request.user)
        objectives = Objective.objects.filter(user=request.user)
        context = {
            'wallets': wallets,
            'currencies': currencies,
            'f_wallets': f_wallets,
            'objectives': objectives
        }
        return render(request, 'home.html', context)


class LoginView(View):
    """Login page view"""

    def get(self, request):
        form = LoginForm(request.POST or None)
        context = {
            'form': form,
            'auth_check': 1,
            'page_title':'Sign In',
            'button_title':'Sign Up'
        }
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

        context = {
            'form': form,
            'auth_check': 1,
            'page_title':'Sign In',
            'button_title':'Sign Up'
        }
        return render(request, 'page_manager.html', context)


class RegistrationView(View):
    """Registration page view"""

    def get(self, request):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form,
            'auth_check': 2,
            'page_title':'Sign Up',
            'button_title':'Sign In'
        }
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST or None)

        if form.is_valid():
            created_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            created_user.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            Profile.objects.create(user=created_user)
            login(request, user)
            messages.add_message(request,messages.SUCCESS,"Registation completed!")
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'auth_check': 2,
            'page_title':'Sign Up',
            'button_title':'Sign In'
        }
        return render(request, 'page_manager.html', context)


class LogoutView(View):
    """Logout view"""
    
    def get(self, request):
        logout(request)
        return redirect('login')


class SearchResultsView(AuthUserMixin, View):
    """Search page view"""

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))

        if FamilyAccess.objects.filter(user=request.user,wallet=wallet) \
        or wallet.user == request.user:
            q_wallet = kwargs.get('wallet_pk')
            q_from = self.request.GET.get("from")
            q_to = self.request.GET.get("to")
            q_category = self.request.GET.get("category")
            q_type = self.request.GET.get("type")
            actions = search_actions(q_wallet, q_from, q_to, q_category, q_type)

            if self.request.GET.get("category"):
                categories = Category.objects.filter(pk=q_category)
                t_g = total_graph(actions, categories)
            else:
                categories = Category.objects.filter(wallet=q_wallet)
                t_g = total_graph(actions,categories)
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
                'q_type': q_type,
                'category_out': category_out,
                'button_url': 'wallet-page',
                'b_u2': kwargs.get('wallet_pk'),
                'button_title': 'Back',
                'wallet': wallet,
                'total_amount': calc_amount(actions),
                'page_obj': page_obj,
                't_g': t_g
            }
            return render(request, 'search_actions.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class DownloadJSON(AuthUserMixin, View):
    """Download actions as JSON view"""

    def get(self, request, **kwargs):
        q_wallet = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=q_wallet)

        if FamilyAccess.objects.filter(user=request.user,wallet=wallet) \
        or wallet.user == request.user:
            q_from = request.GET.get('from')
            q_to = request.GET.get('to')
            q_category = request.GET.get("category")
            q_type = self.request.GET.get("type")
            actions = search_actions(q_wallet, q_from, q_to, q_category, q_type)
            json_str = serializers.serialize('json', actions,
                fields=('title', 'user', 'category', 'wallet','money', 'action_type', 'date'))
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=actions.json'
            return response
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class CreateAction(AuthUserMixin, View):
    """Create action page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = get_object_or_404(Wallet, pk=wallet_pk)
        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            form = ActionForm(wallet_pk, request.POST or None)
            messages.add_message(request, messages.SUCCESS,"Title length: {} symbols".format('150'))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Create action',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        form = ActionForm(wallet_pk, request.POST or None)

        if form.is_valid():
            action = Action.objects.create(
                user=request.user,
                category=form.cleaned_data['category'],
                wallet=Wallet.objects.get(pk=wallet_pk),
                title=form.cleaned_data['title'],
                money=form.cleaned_data['money'],
                date=form.cleaned_data['date'],
                action_type=form.cleaned_data['action_type'])
            action.save()
            calc_amount_wallet('create', action, wallet_pk)
            messages.add_message(request, messages.SUCCESS,"Added action: {}".format(form.cleaned_data['title']))
            log_write(wallet_pk, "create", "action", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create action',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class UpdateAction(AuthUserMixin, View):
    """Update action page view"""

    def get(self, request, **kwargs):
        action_pk = kwargs.get('pk')
        wallet_pk = kwargs.get('wallet_pk')

        if (Action.objects.get(pk=action_pk).user == request.user) \
        or (Wallet.objects.get(pk=wallet_pk).user == request.user):
            action = Action.objects.get(pk=action_pk)
            form = ActionForm(wallet_pk,request.POST or None,instance=action)
            messages.add_message(request, messages.SUCCESS, "Title length: {} symbols" .format('150'))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Update action', 
                'button_title':'Back'}
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        action_pk = kwargs.get('pk')
        wallet_pk = kwargs.get('wallet_pk')
        action = Action.objects.get(pk=action_pk)
        old_action = Action.objects.get(pk=action_pk)
        form = ActionForm(wallet_pk, request.POST, instance=action)

        if form.is_valid():
            form.save()
            calc_amount_wallet_update(action, wallet_pk, old_action)
            messages.add_message(request, messages.SUCCESS,"Updated action: {}".format(form.cleaned_data['title']))
            log_write(wallet_pk, "update", "action", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = ActionForm(instance=action)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update action',
            'button_title':'Back'}
        return render(request, 'page_manager.html', context)


class CreateCategory(AuthUserMixin, View):
    """Create category page view"""

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(pk=kwargs.get('wallet_pk'))

        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            form = CategoryForm(request.POST or None)
            messages.add_message(request, messages.SUCCESS,"Title length: {} symbols".format('25'))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Create category',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=wallet_pk)
        form = CategoryForm(request.POST or None)
        
        if form.is_valid():
            Category.objects.create(
                title=form.cleaned_data['title'], 
                wallet=wallet,
                user=request.user,
                color=form.cleaned_data['color']
            )
            messages.add_message(request, messages.SUCCESS,"Added category: {}!".format(form.cleaned_data['title']))
            log_write(wallet_pk, "create", "category", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create category',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class UpdateCategory(AuthUserMixin, View):
    """Update category page view"""

    def get(self, request, **kwargs):

        if (Category.objects.get(pk=kwargs.get('pk')).user == request.user) \
        or (Wallet.objects.get(pk=kwargs.get('wallet_pk')).user == request.user):
            category = Category.objects.get(pk=kwargs.get('pk'))
            form = CategoryForm(request.POST or None, instance=category)
            messages.add_message(request, messages.SUCCESS,"Title length: {} symbols".format('25'))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Update category',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request,messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        category = Category.objects.get(pk=kwargs.get('pk'))
        form = CategoryForm(request.POST or None, instance=category)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,"Updated category: {}".format(form.cleaned_data['title']))
            log_write(wallet_pk, "update", "category", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CategoryForm(instance=category)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update category',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class CategoryManager(AuthUserMixin, View):
    """Category manager page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=wallet_pk)

        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            categories = Category.objects.filter(wallet=wallet_pk)
            paginator = Paginator(categories, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'wallet': wallet,
                'page_obj': page_obj,
                'count': categories.count
            }
            return render(request, 'category_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class CreateWallet(AuthUserMixin, View):
    """Create wallet page view"""

    def get(self, request):
        form = WalletForm(request.user, request.POST or None)
        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create wallet',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = WalletForm(request.user, request.POST or None)

        if form.is_valid():
            Wallet.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                currency=form.cleaned_data['currency'],
                start_amount=form.cleaned_data['start_amount']
            )
            messages.add_message(request, messages.SUCCESS,"Added wallet: {}!".format(form.cleaned_data['title']))
            log_write('0', "create", "wallet", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create wallet',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class UpdateWallet(AuthUserMixin, View):
    """Update wallet page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')

        if (Wallet.objects.get(pk=wallet_pk).user == request.user):
            wallet = Wallet.objects.get(user=request.user, pk=wallet_pk)
            form = WalletForm(request.user, request.POST or None,instance=wallet)
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Update wallet', 
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")

            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(
            user=request.user,
            pk=wallet_pk
        )
        form = WalletForm(request.user, request.POST or None,instance=wallet)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Updated wallet: {}".format(form.cleaned_data['title']))
            log_write(wallet_pk, "update", "wallet", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CategoryForm(instance=wallet)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update wallet',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class WalletView(AuthUserMixin, View):
    """Wallet page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = get_object_or_404(Wallet, pk=wallet_pk)

        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            actions = Action.objects.filter(wallet=wallet_pk).order_by('-date', '-created_at')
            categories = Category.objects.filter(wallet=wallet_pk)
            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            w_messages = WalletMessage.objects.filter(wallet=wallet_pk)
            context = {
                'wallet': wallet,
                'total_amount': wallet.start_amount,
                'page_obj': page_obj,
                'count': actions.count,
                'categories': categories,
                't_g': total_graph(actions, categories),
                'w_messages': w_messages
            }
            return render(request, 'wallet.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class CreateCurrency(AuthUserMixin, View):
    """Create cyrrency page view"""

    def get(self, request):
        form = CurrencyForm(request.POST or None)
        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create currency',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = CurrencyForm(request.POST or None)

        if form.is_valid():
            Currency.objects.create(
                user=request.user,
                title=form.cleaned_data['title']
            )
            messages.add_message(request, messages.SUCCESS, "Added currency: {}!".format(form.cleaned_data['title']))
            log_write('0', "create", "currency", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create currency',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class UpdateCurrency(AuthUserMixin, View):
    """Update cyrrency page view"""
    
    def get(self, request, **kwargs):
        curr_pk = kwargs.get('pk')

        if (Currency.objects.get(pk=curr_pk).user == request.user):
            currency = Currency.objects.get(user=request.user, pk=curr_pk)
            form = CurrencyForm(request.POST or None, instance=currency)
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Update currency',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        currency = Currency.objects.get(user=request.user, pk=(kwargs.get('pk')))
        form = CurrencyForm(request.POST or None, instance=currency)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,"Updated currency: {}".format(form.cleaned_data['title']))
            log_write('0', "update", "currency", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CurrencyForm(instance=currency)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update currency',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class DeleteModelView(AuthUserMixin, View):
    """Delete view for "Wallet", "Cyrrency", "Family Access", "Objective" """

    CHOISE = {
        'wallet': Wallet,
        'currency': Currency,
        'familyAccess': FamilyAccess,
        'objective': Objective
    }

    def get(self, request, **kwargs):
        item = self.CHOISE[kwargs['model']].objects.get(pk=(kwargs.get('pk')),user=request.user)
        item.delete()
        messages.add_message(request, messages.WARNING,"Deleted {}".format(kwargs.get('model')))
        log_write('0', "delete", kwargs.get('model'), item.title, request.user)
        return HttpResponseRedirect(get_next_link(request))


class DeleteActionView(AuthUserMixin, View):
    """Delete action view
    When deleting, it recalculates the amount of funds in the wallet"""

    def get(self, request, **kwargs):
        action_pk = kwargs.get('pk')
        wallet_pk = kwargs.get('wallet_pk')

        if (Action.objects.get(pk=action_pk).user == request.user) \
        or (Wallet.objects.get(pk=wallet_pk).user == request.user):
            action = Action.objects.get(pk=action_pk)
            calc_amount_wallet('delete', action, action.wallet.pk)
            messages.add_message(request, messages.SUCCESS,"Deleted action {}".format(action.title))
            action.delete()
            log_write(wallet_pk, "delete", "action", action.title, request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class DeleteCategoryView(AuthUserMixin, View):
    """Delete category view
    When deleting, it recalculates the amount of funds in the wallet"""

    def get(self, request, **kwargs):
        ctg_pk = kwargs.get('pk')
        wallet_pk = kwargs.get('wallet_pk')

        if (Category.objects.get(pk=ctg_pk).user == request.user) \
        or (Wallet.objects.get(pk=wallet_pk).user == request.user):
            category = Category.objects.get(pk=ctg_pk)
            actions = Action.objects.filter(category=ctg_pk)

            for action in actions:
                calc_amount_wallet('delete', action, action.wallet.pk)

            messages.add_message(request, messages.SUCCESS,"Deleted category {}".format(category.title))
            log_write(wallet_pk, "delete", "category", category.title, request.user)
            category.delete()
            return HttpResponseRedirect(get_next_link(request))
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class DeleteWalletMessageView(AuthUserMixin, View):
    """Delete note in wallet view"""

    def get(self, request, **kwargs):
        msg_pk = kwargs.get('pk')
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=wallet_pk)

        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            w_message = WalletMessage.objects.get(pk=msg_pk)
            messages.add_message(request, messages.SUCCESS,"Deleted message!")
            log_write(wallet_pk, "delete", "note", w_message.message, request.user)
            w_message.delete()
            return HttpResponseRedirect(get_next_link(request))
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))


class FamilyAccessView(AuthUserMixin, OwnerAccessMixin, View):
    """Family Access page view"""

    def get(self, request, **kwargs):
        wallet = Wallet.objects.get(user=request.user, pk=kwargs.get('wallet_pk'))
        t_wallet = FamilyAccess.objects.filter(wallet=wallet)
        context = {
            'wallet_pk': wallet.pk,
            't_wallet': t_wallet,
            'go_next': get_next_link(request)
        }
        return render(request, 'wallet_access.html', context)


class DeleteAccessView(AuthUserMixin, OwnerAccessMixin, View):
    """Delete Family Access view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        instance = FamilyAccess.objects.get(
            wallet=Wallet.objects.get(
                user=request.user,
                pk=wallet_pk),
            user=User.objects.get(username=kwargs.get('user')))
        messages.add_message(request, messages.WARNING, "Deleted user: {}!".format(instance.user.username))
        log_write(wallet_pk, "delete", "access for", instance.user.username, request.user)
        instance.delete()
        return redirect(get_next_link(request))


class AddAccessView(AuthUserMixin, OwnerAccessMixin, View):
    """Add Family Access page view"""

    def get(self, request, **kwargs):
        form = FamilyAccessForm(request.POST or None)
        context = {
            'form': form,
            'go_next': get_next_link(request), 
            'page_title': 'Add user',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        form = FamilyAccessForm(request.POST or None)

        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['user1'])
            FamilyAccess.objects.create(
                user=user,
                wallet=Wallet.objects.get(
                    user=request.user,
                    pk=wallet_pk))
            messages.add_message(request, messages.SUCCESS, "Added user: {}".format(form.cleaned_data['user1']))
            log_write(wallet_pk, "create", "access for", user.username, request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Add user',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class ProfileView(AuthUserMixin, View):
    """User profile page view"""

    def get(self, request, **kwargs):
        user_profile = User.objects.get(username=kwargs.get('username'))
        profile = Profile.objects.get(user=user_profile)
        context = {
            'go_next': get_next_link(request),
            'profile': profile,
            'button_title':'Home'
        }
        return render(request, 'profile.html', context)


class ProfileUpdate(AuthUserMixin, View):
    """Update user profile page view"""

    def get(self, request, **kwargs):
        profile = Profile.objects.get(
            user=User.objects.get(
                username=kwargs.get('username')))

        if profile.user == request.user:
            form = ProfileForm(request.POST or None, instance=profile)
            context = {
                'form':form,
                'go_next': get_next_link(request),
                'page_title':'Profile update',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        profile = Profile.objects.get(
            user=User.objects.get(
                username=kwargs.get('username')))
        form = ProfileForm(request.POST or None, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,"Profile updated!")
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = ProfileForm(instance=profile)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update profile',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class ObjectiveCreate(AuthUserMixin, View):
    """Create objective page view"""

    def get(self, request):
        form = ObjectiveForm(request.user, request.POST or None)
        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create objective',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = ObjectiveForm(request.user, request.POST or None)

        if form.is_valid():
            Objective.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                currency=form.cleaned_data['currency'],
                target_amount=form.cleaned_data['target_amount'],
                now_amount=form.cleaned_data['now_amount']
            )
            messages.add_message(request, messages.SUCCESS, "Added objective: {}!".format(form.cleaned_data['title']))
            log_write('0', "create", "objective", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create objective',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class ObjectiveUpdate(AuthUserMixin, View):
    """Update objective page view"""

    def get(self, request, **kwargs):

        if (Objective.objects.get(pk=kwargs.get('pk')).user == request.user):
            objective = Objective.objects.get(
                user=request.user,
                pk=(kwargs.get('pk'))
            )
            form = ObjectiveForm(request.user, request.POST or None, instance=objective)
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Update objective',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING,"Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        objective = Objective.objects.get(
            user=request.user,
            pk=(kwargs.get('pk'))
        )
        form = ObjectiveForm(request.user,request.POST or None,instance=objective)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,"Updated objective: {}".format(form.cleaned_data['title']))
            log_write('0', "update", "objective", form.cleaned_data['title'], request.user)
            return HttpResponseRedirect(get_next_link(request))
        else:
            form = CategoryForm(instance=objective)

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Update objective',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class ObjectiveTransfer(AuthUserMixin, View):
    """Transfer money from wallet to objective page view"""

    def get(self, request, **kwargs):
        if (Objective.objects.get(pk=kwargs.get('pk')).user == request.user):
            objective = Objective.objects.get(pk=kwargs.get('pk'))
            form = ObjectiveTransferForm(objective.currency, request.user, request.POST or None)
            messages.add_message(request, messages.SUCCESS,"Objective target money: {}".format(objective.target_amount))
            messages.add_message(request, messages.SUCCESS,"Objective now money: {}".format(objective.now_amount))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Transfer money to {}'.format(objective.title),
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        objective = Objective.objects.get(pk=kwargs.get('pk'))
        form = ObjectiveTransferForm(objective.currency, request.user, request.POST or None)

        if form.is_valid():
            wallet = form.cleaned_data['wallets']
            money = decimal.Decimal(form.cleaned_data['money'])
            if wallet.start_amount >= money:
                if (objective.target_amount - objective.now_amount) >= money:
                    objective_transfer_money(objective, wallet, money, request.user)
                    messages.add_message(request, messages.SUCCESS,"{} {} transfered to {}".format( money, wallet.currency.title,objective.title))
                    return HttpResponseRedirect(get_next_link(request))
                else:
                    messages.add_message(request, messages.WARNING,"The amount entered is more than required!")
            else:
                messages.add_message(request, messages.WARNING,"No money!")

        messages.add_message(request, messages.SUCCESS,
            "Objective target money: {}".format(objective.target_amount)
        )
        messages.add_message(request, messages.SUCCESS,
            "Objective now money: {}".format(objective.now_amount)
        )

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Transfer money to Wallet',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class MoneyTransfer(AuthUserMixin, View):
    """Transfer money between wallets page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=wallet_pk)

        if (wallet.user == request.user):
            form = MoneyTransferForm(wallet_pk, request.user, wallet.currency, request.POST or None)
            messages.add_message(request, messages.SUCCESS,"Wallet money: {}".format(wallet.start_amount))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Transfer money to Wallet',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)
        else:
            messages.add_message(request, messages.WARNING, "Error!")
            return HttpResponseRedirect(get_next_link(request))

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        form = MoneyTransferForm(wallet_pk, request.user, request.POST or None)
        wallet_from = Wallet.objects.get(pk=wallet_pk)

        if form.is_valid():
            money = decimal.Decimal(form.cleaned_data['money'])
            if wallet_from.start_amount >= money:
                transfer_money(wallet_from,form.cleaned_data['wallets'],money,request.user)
                messages.add_message(request, messages.SUCCESS,"Money transfered to {}".format(form.cleaned_data['wallets'].title))
                return HttpResponseRedirect(get_next_link(request))
            else:
                messages.add_message(request, messages.WARNING,"No money!")

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Transfer money to Wallet',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class AddWalletMessage(AuthUserMixin, View):
    """Add wallet note page view"""

    def get(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        wallet = Wallet.objects.get(pk=wallet_pk)

        if FamilyAccess.objects.filter(user=request.user, wallet=wallet) \
        or wallet.user == request.user:
            form = WalletMessageForm(request.POST or None)
            messages.add_message(request, messages.SUCCESS,"Max message length: {} symbols".format('150'))
            context = {
                'form': form,
                'go_next': get_next_link(request),
                'page_title':'Create message',
                'button_title':'Back'
            }
            return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        wallet_pk = kwargs.get('wallet_pk')
        form = WalletMessageForm(request.POST or None)

        if form.is_valid():
            WalletMessage.objects.create(
                wallet=Wallet.objects.get(pk=wallet_pk),
                message=form.cleaned_data['message'])
            messages.add_message(request, messages.SUCCESS, "Added new message!")
            log_write(wallet_pk, "create", "note", form.cleaned_data['message'], request.user)
            return HttpResponseRedirect(get_next_link(request))

        context = {
            'form': form,
            'go_next': get_next_link(request),
            'page_title':'Create message',
            'button_title':'Back'
        }
        return render(request, 'page_manager.html', context)


class ShowLogView(AuthUserMixin, View):
    """Logging page view"""

    def get(self, request, **kwargs):
        username = kwargs.get('username')
        logs = LogTable.objects.filter(user=User.objects.get(username=username)).order_by('-created_at')
        context = {
            'go_next': get_next_link(request),
            'logs': logs,
            'button_title':'Back'
        }
        return render(request, 'logs_page.html', context)


class SearchUser(AuthUserMixin, View):
    """Show user profile after search page view"""

    def get(self, request, **kwargs):
        q_username = self.request.GET.get("q_username")
        try:
            User.objects.get(username=q_username)
        except:
            messages.add_message(request, messages.WARNING,'User "{}" not found'.format(q_username))
            return redirect('profile', username=request.user.username)
        return redirect('profile', username=q_username)
