from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
     # admin page link (Django Admin Page)
     path('admin/',
          admin.site.urls),
     # included application link file
     path('',
          include('core.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
