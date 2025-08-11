from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("novo_protocolo/", views.novo_protocolo, name="novo_protocolo"),
    path("busca/", views.busca_global, name="busca_global"),
    path("exportar_csv/", views.exportar_protocolos_csv, name="exportar_protocolos_csv"),
]


