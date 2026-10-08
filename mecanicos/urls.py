from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='mecanicos_lista'),
    path('novo/', views.cadastrar, name='mecanicos_cadastrar'),
    path('<int:pk>/', views.detalhe, name='mecanicos_detalhe'),
    path('<int:pk>/editar/', views.editar, name='mecanicos_editar'),
    path('<int:pk>/desativar/', views.desativar, name='mecanicos_desativar'),
    path('<int:pk>/reativar/', views.reativar, name='mecanicos_reativar'),
]