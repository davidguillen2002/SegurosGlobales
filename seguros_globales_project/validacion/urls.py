from django.urls import path
from . import views

urlpatterns = [
    path('procesar/', views.procesar_reclamos_csv, name='procesar_reclamos'),
    path('actualizar/', views.actualizar_reclamos, name='actualizar_reclamos'),
]