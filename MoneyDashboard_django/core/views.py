from django.shortcuts import render, redirect
from django.views.generic import View
from django.db.models import Q

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
            actions = Action.objects.filter(user=request.user).order_by('-date', '-created_at')
            # actions

            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'total_amount': calc_amount(actions),
                'page_obj': page_obj
                }
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
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added action: {}!"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect('/')
        context = {'form': form}
        return render(request, 'create_action.html', context)


class DeleteAction(View):

    def get(self, request, **kwargs):
        messages.add_message(request,
                             messages.WARNING,
                             "Deleted action!")
        Action.objects.get(pk=(kwargs.get('pk')),
                           user=request.user).delete()
        return redirect(request.GET.get('next'))


class UpdateAction(View):

    def get(self, request, **kwargs):
        action = Action.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = ActionForm(instance=action)
        context = {'form': form}
        return render(request, 'update_action.html', context)

    def post(self, request, **kwargs):
        action = Action.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = ActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Updated action: {}"
                                 .format(form.cleaned_data['title']))
            next = request.GET.get('next')
            print(next)
            return HttpResponseRedirect(next)
        else:
            form = ActionForm(instance=action)
        context = {'form': form}
        return render(request, 'update_action.html', context)


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
            user = authenticate(
                username=username,
                password=password)
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
        context = {'form': form}
        return render(request, 'registration.html', context)


class SearchResultsView(View):

    def get(self, request):
        q_from = self.request.GET.get("from")
        q_to = self.request.GET.get("to")
        actions_all = Action.objects.filter(user=request.user)

        if q_from:
            if q_to:    
                actions = actions_all.filter(
                    Q(date__gte=q_from,date__lte=q_to))
            else:
                actions = actions_all.filter(
                    Q(date__gte=q_from))
        else:
            if q_to:
                actions = actions_all.filter(
                        Q(date__lte=q_to))
            else:
                actions = []

        paginator = Paginator(actions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'q_from': q_from,
            'q_to': q_to,
            'total_amount': calc_amount(actions),
            'page_obj': page_obj
        }
        return render(request, 'search_actions.html', context)


class DownloadJSON(View):

    def get(self, request, **kwargs):
        actions_all = Action.objects.filter(user=request.user).order_by('-date', '-created_at')

        q_from = request.GET.get('from')
        q_to = request.GET.get('to')

        if q_from:
            if q_to:    
                actions = actions_all.filter(
                    Q(date__gte=q_from,date__lte=q_to))
                f_name = q_from + '_' + q_to
            else:
                actions = actions_all.filter(
                    Q(date__gte=q_from))
                f_name = q_from + '_'
        else:
            if q_to:
                actions = actions_all.filter(
                        Q(date__lte=q_to))
                f_name = '_' + q_to
            else:
                actions = actions_all
                f_name = 'all_actions'

        json_str = serializers.serialize('json', actions, fields=('title','money','action_type','date'))
        response = HttpResponse(json_str, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=%s.json' % f_name

        return response
