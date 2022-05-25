from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #### home
    path('', HomePage.as_view(), name='home'),

    #### download
    path('wallet/<int:wallet_pk>/download/', DownloadJSON.as_view(), name='download'),

    #### model pages
        # wallet view
    path('wallet/<int:wallet_pk>/', WalletView.as_view(), name='wallet-page'),
        # category manager
    path('wallet/<int:wallet_pk>/category-manager', CategoryManager.as_view(), name='category-manager'),
        # search page
    path('wallet/<int:wallet_pk>/search/', SearchResultsView.as_view(), name='search-results'),

    # action
    path('wallet/<int:wallet_pk>/action/create/', CreateAction.as_view(), name='create-action'),
    path('wallet/<int:wallet_pk>/action/<int:pk>/update/', UpdateAction.as_view(), name='update-action'),
    path('wallet/<int:wallet_pk>/action/<int:pk>/delete/', DeleteActionView.as_view(), name='delete-action'),

    # category
    path('wallet/<int:wallet_pk>/category-manager/create/', CreateCategory.as_view(), name='create-category'),
    path('wallet/<int:wallet_pk>/category-manager/<int:pk>/update/', UpdateCategory.as_view(), name='update-category'),
    path('wallet/<int:wallet_pk>/category-manager/<int:pk>/delete/', DeleteCategoryView.as_view(), name='delete-category'),

    # wallet
    path('wallet/create/', CreateWallet.as_view(), name='create-wallet'),
    path('wallet/<int:wallet_pk>/update/', UpdateWallet.as_view(), name='update-wallet'),
    path('wallet/<int:wallet_pk>/transfer/', MoneyTransfer.as_view(), name='transfer-wallet'),

    # currency
    path('currency/create/', CreateCurrency.as_view(), name='create-currency'),
    path('currency/<int:pk>/update/', UpdateCurrency.as_view(), name='update-currency'),

    # auth
    path('login/', LoginView.as_view(), name='login'),
    path('sign-out/', LogoutView.as_view(), name='sign-out'),
    path('registration/', RegistrationView.as_view(), name='registration'),

    # access
    path('wallet/<int:wallet_pk>/access-manager/', FamilyAccessView.as_view(), name='wallet-access'),
    path('wallet/<int:wallet_pk>/access-manager/add/', AddAccessView.as_view(), name='add-access'),
    path('wallet/<int:wallet_pk>/access-manager/<str:user>/delete/', DeleteAccessView.as_view(), name='delete-access'),

    #### other delete
    path('<str:model>/<int:pk>/delete/', DeleteModelView.as_view(), name='delete-model'),

    # profile
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/update/', ProfileUpdate.as_view(), name='profile-update'),

    # objectives
    path('objective/create/', ObjectiveCreate.as_view(), name='objective-create'),
    path('objective/<int:pk>/update/', ObjectiveUpdate.as_view(), name='objective-update'),
    path('objective/<int:pk>/transfer/', ObjectiveTransfer.as_view(), name='objective-transfer'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
