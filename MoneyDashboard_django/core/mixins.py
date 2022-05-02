from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import SingleObjectMixin

from .models import *


class AuthUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.INFO, 'Сначала войдите в аккаунт!')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class OwnerAccessMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('next'):
            next = request.GET.get('next')
        else:
            next = '/'

        try:
            Wallet.objects.get(user=request.user, pk=kwargs.get('wallet_pk'))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, "Error!")
            return redirect(next)
        return super().dispatch(request, *args, **kwargs)


class Name(object):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)