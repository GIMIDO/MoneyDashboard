from dataclasses import field
from re import I
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, UpdateView, ListView
from django.db.models import Q
from django.urls.base import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from .models import *
from .forms import *

class HomePage(View):

    def get(self, request):
        if request.user.is_authenticated:
            context = {'actions': Action.objects.filter(user=request.user).order_by('-date', '-created_at')}
            return render(request, 'home.html', context)
        else:
            return HttpResponseRedirect('sign-in/')


class CreateAction(View):

    def get(self, request):
        form = ActionForm(request.POST or None)
        context = {'form': form}
        return render(request, 'create_action.html', context)

    def post(self, request):
        form = ActionForm(request.POST or None)
        if form.is_valid():
            Action.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                money=form.cleaned_data['money'],
                date=form.cleaned_data['date'],
                action_type=form.cleaned_data['action_type']
            )
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'create_action.html', context)


class DeleteAction(View):

    def get(self, request, **kwargs):
        Action.objects.get(pk=(kwargs.get('pk'))).delete()
        return redirect(request.META.get('HTTP_REFERER'))


class UpdateAction(UpdateView):
    
    model = Action
    fields = ['title','money','date','action_type']
    template_name = 'update_action.html'
    success_url = reverse_lazy('home')


class LoginView(View):

    def get(self, request):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'login.html', context)

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'login.html', context)


class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm(request.POST or None)
        context = {'form': form}
        return render(request, 'registration.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], email=form.cleaned_data['email'])
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'registration.html', context)


class SearchResultsView(View):

    def get(self, request):
        query = self.request.GET.get("q")
        actions = Action.objects.filter(
            Q(date__icontains=query)
        )
        context = {'actions': actions, 'search_q': query}
        return render(request, 'search_actions.html', context)
