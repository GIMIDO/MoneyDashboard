from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('download/', DownloadJSON.as_view(), name='download'),
    path('action/create/', CreateAction.as_view(), name='create-action'),
    path('category/create/', CreateCategory.as_view(), name='create-category'),
    path('<int:pk>/delete/', DeleteAction.as_view(), name='delete-action'),
    path('<int:pk>/update/', UpdateAction.as_view(), name='update-action'),
    path('sign-in/', LoginView.as_view(), name='sign-in'),
    path('sign-out/', LogoutView.as_view(next_page="/"), name='sign-out'),
    path('sign-up/', RegistrationView.as_view(), name='sign-up'),
    path('search/', SearchResultsView.as_view(), name='search-results'),
]