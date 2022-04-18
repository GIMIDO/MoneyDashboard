from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),

    path('download/', DownloadJSON.as_view(), name='download'),

    path('create/', CreateAction.as_view(), name='create-action'),
    path('delete/<int:pk>/', DeleteAction.as_view(), name='delete-action'),
    path('update/<int:pk>/', UpdateAction.as_view(), name='update-action'),

    path('sign-in/', LoginView.as_view(), name='sign-in'),
    path('sign-out/', LogoutView.as_view(next_page="/"), name='sign-out'),
    path('sign-up/', RegistrationView.as_view(), name='sign-up'),

    path('search/', SearchResultsView.as_view(), name='search-results'),
]