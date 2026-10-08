from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='financeiro_lista'),
    path('novo/', views.cadastrar, name='financeiro_cadastrar'),
    path('<int:pk>/', views.detalhe, name='financeiro_detalhe'),
    path('<int:pk>/editar/', views.editar, name='financeiro_editar'),
    path('<int:pk>/cancelar/', views.cancelar, name='financeiro_cancelar'),
    path('os/<int:os_pk>/gerar/', views.gerar_da_os, name='financeiro_gerar_da_os'),
]