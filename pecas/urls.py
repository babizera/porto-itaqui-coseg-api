from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='pecas_lista'),
    path('nova/', views.cadastrar, name='pecas_cadastrar'),
    path('<int:pk>/', views.detalhe, name='pecas_detalhe'),
    path('<int:pk>/editar/', views.editar, name='pecas_editar'),
    path('<int:pk>/desativar/', views.desativar, name='pecas_desativar'),
    path('<int:pk>/reativar/', views.reativar, name='pecas_reativar'),
]