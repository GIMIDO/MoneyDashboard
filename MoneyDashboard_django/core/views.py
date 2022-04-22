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
            actions = Action.objects.filter(user=request.user).order_by('-date', '-created_at')
            categories = Category.objects.filter(user=request.user)
            paginator = Paginator(actions, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'total_amount': calc_amount(actions),
                'page_obj': page_obj,
                'categories':categories
                }
            return render(request, 'home.html', context)
        else:
            return HttpResponseRedirect('sign-in/')


class CreateAction(View):

    def get(self, request):
        form = ActionForm(request.user, request.POST or None)
        context = {'form': form,
                   'button_url':'home',
                   'page_title':'Create action',
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = ActionForm(request.user, request.POST or None)
        if form.is_valid():
            Action.objects.create(
                user=request.user,
                category=form.cleaned_data['category'],
                title=form.cleaned_data['title'],
                money=form.cleaned_data['money'],
                date=form.cleaned_data['date'],
                action_type=form.cleaned_data['action_type']
            )
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added action: {}"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect('/')
        context = {'form': form,
                   'button_url':'home',
                   'page_title':'Create action',
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)


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
        form = ActionForm(request.user,
                          request.POST or None,
                          instance=action)
        context = {'form': form,
                   'button_url':'home',
                   'page_title':'Update action',
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)

    def post(self, request, **kwargs):
        action = Action.objects.get(user=request.user,
                                    pk=(kwargs.get('pk')))
        form = ActionForm(request.user,
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
                   'button_url':'home',
                   'page_title':'Update action',
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)


class LoginView(View):

    def get(self, request):
        form = LoginForm(request.POST or None)
        context = {'form': form,
                   'button_url':'sign-up',
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
                   'button_url':'sign-up',
                   'page_title':'Sign In',
                   'button_title':'Sign Up'}
        return render(request, 'page_manager.html', context)


class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm(request.POST or None)
        context = {'form': form,
                   'button_url':'sign-in',
                   'page_title':'Sign Un',
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
                   'button_url':'sign-in',
                   'page_title':'Sign Un',
                   'button_title':'Sign In'}
        return render(request, 'page_manager.html', context)


class SearchResultsView(View):

    def get(self, request):
        q_from = self.request.GET.get("from")
        q_to = self.request.GET.get("to")
        q_category = self.request.GET.get("category")
        q_user = request.user
        actions = search_actions(q_from, q_to, q_category, q_user)

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
            'total_amount': calc_amount(actions),
            'page_obj': page_obj
        }
        return render(request, 'search_actions.html', context)


class DownloadJSON(View):

    def get(self, request, **kwargs):
        q_from = request.GET.get('from')
        q_to = request.GET.get('to')
        q_category = request.GET.get("category")
        q_user = request.user
        actions = search_actions(q_from, q_to, q_category, q_user)
        json_str = serializers.serialize('json',
                                         actions,
                                         fields=('title',
                                                 'category',
                                                 'money',
                                                 'action_type',
                                                 'date'))
        response = HttpResponse(json_str, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=actions.json'

        return response


class CreateCategory(View):

    def get(self, request):
        form = CategoryForm(request.POST or None)
        context = {'form': form,
                   'button_url':'home',
                   'page_title':'Create category',
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)

    def post(self, request):
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            Category.objects.create(user=request.user,
                                    title=form.cleaned_data['title'])
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Added ctegory: {}!"
                                 .format(form.cleaned_data['title']))
            return HttpResponseRedirect('/')
        context = {'form': form,
                   'button_url':'home',
                   'page_title':'Create category', 
                   'button_title':'Home'}
        return render(request, 'page_manager.html', context)
