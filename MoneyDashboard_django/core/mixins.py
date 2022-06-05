from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import *


class AuthUserMixin(object):
    '''Checking for an authorized user'''

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.INFO,'Log in first!')
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)


class OwnerAccessMixin(object):
    '''Checking the user for the role of the creator of the wallet'''

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('next'):
            next = request.GET.get('next')
        else:
            next = '/'

        try:
            Wallet.objects.get(
                user=request.user,
                pk=kwargs.get('wallet_pk')
            )
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING,"Error!")
            return redirect(next)

        return super().dispatch(request, *args, **kwargs)
