from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='veiculos_lista'),
    path('novo/', views.cadastrar, name='veiculos_cadastrar'),
    path('<int:pk>/', views.detalhe, name='veiculos_detalhe'),
    path('<int:pk>/editar/', views.editar, name='veiculos_editar'),
    path('<int:pk>/desativar/', views.desativar, name='veiculos_desativar'),
    path('<int:pk>/reativar/', views.reativar, name='veiculos_reativar'),
]