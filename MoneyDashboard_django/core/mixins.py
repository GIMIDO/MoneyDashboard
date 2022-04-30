from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import View

from .models import *


class AuthenticatedUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.INFO, 'Сначала войдите в аккаунт!')
            return redirect('sign-in')
        return super().dispatch(request, *args, **kwargs)