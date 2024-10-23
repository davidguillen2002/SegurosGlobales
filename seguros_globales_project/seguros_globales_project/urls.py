from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reclamos/', include('reclamos.urls')),
    path('validacion/', include('validacion.urls')),
]