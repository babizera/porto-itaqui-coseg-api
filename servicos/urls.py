from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='servicos_lista'),
    path('novo/', views.cadastrar, name='servicos_cadastrar'),
    path('<int:pk>/', views.detalhe, name='servicos_detalhe'),
    path('<int:pk>/editar/', views.editar, name='servicos_editar'),
    path('<int:pk>/desativar/', views.desativar, name='servicos_desativar'),
    path('<int:pk>/reativar/', views.reativar, name='servicos_reativar'),
]