from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('wallet/<int:pk>/download/', DownloadJSON.as_view(), name='download'),

    path('wallet/<int:pk>/', WalletView.as_view(), name='wallet-page'),

    path('wallet/<int:pk>/action/create/', CreateAction.as_view(), name='create-action'),
    path('wallet/<int:pk>/category/create/', CreateCategory.as_view(), name='create-category'),
    path('wallet/create/', CreateWallet.as_view(), name='create-wallet'),
    path('currency/create/', CreateCurrency.as_view(), name='create-currency'),

    path('<str:model>/<int:pk>/delete/', DeleteModelView.as_view(), name='delete-action'),

    path('wallet/<int:wallet_pk>/action/<int:action_pk>/update/', UpdateAction.as_view(), name='update-action'),
    path('wallet/<int:wallet_pk>/category/<int:pk>/update/', UpdateCategory.as_view(), name='update-category'),
    path('wallet/<int:pk>/update/', UpdateWallet.as_view(), name='update-wallet'),
    path('currency/<int:pk>/update/', UpdateCurrency.as_view(), name='update-currency'),

    path('sign-in/', LoginView.as_view(), name='sign-in'),
    path('sign-out/', LogoutView.as_view(next_page="/"), name='sign-out'),
    path('sign-up/', RegistrationView.as_view(), name='sign-up'),

    path('wallet/<int:pk>/search/', SearchResultsView.as_view(), name='search-results'),
]