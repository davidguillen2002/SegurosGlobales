from django.urls import path
from .views import exportar_reclamos_csv, exportar_reclamos_view

urlpatterns = [
    path('exportar/', exportar_reclamos_view, name='exportar_reclamos'),  # Página de exportación
    path('exportar-csv/', exportar_reclamos_csv, name='exportar_reclamos_csv'),  # Descarga del CSV
]