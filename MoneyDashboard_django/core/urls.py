from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),

    path('download/', DownloadJSON.as_view(), name='download'),

    path('action/create/', CreateAction.as_view(), name='create-action'),
    path('category/create/', CreateCategory.as_view(), name='create-category'),
    path('wallet/create/', CreateWallet.as_view(), name='create-wallet'),
    path('currency/create/', CreateCurrency.as_view(), name='create-currency'),

    path('<str:model>/<int:pk>/delete/', DeleteAction.as_view(), name='delete-action'),

    path('action/<int:pk>/update/', UpdateAction.as_view(), name='update-action'),
    path('category/<int:pk>/update/', UpdateCategory.as_view(), name='update-category'),
    path('wallet/<int:pk>/update/', UpdateWallet.as_view(), name='update-wallet'),
    path('currency/<int:pk>/update/', UpdateCurrency.as_view(), name='update-currency'),

    path('sign-in/', LoginView.as_view(), name='sign-in'),
    path('sign-out/', LogoutView.as_view(next_page="/"), name='sign-out'),
    path('sign-up/', RegistrationView.as_view(), name='sign-up'),

    path('search/', SearchResultsView.as_view(), name='search-results'),
]