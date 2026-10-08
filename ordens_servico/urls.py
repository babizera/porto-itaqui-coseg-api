from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='ordens_servico_lista'),
    path('nova/', views.cadastrar, name='ordens_servico_cadastrar'),
    path('<int:pk>/', views.detalhe, name='ordens_servico_detalhe'),
    path('<int:pk>/editar/', views.editar, name='ordens_servico_editar'),
    path('<int:pk>/cancelar/', views.cancelar, name='ordens_servico_cancelar'),
]