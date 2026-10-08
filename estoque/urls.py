from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista, name='estoque_lista'),
    path('nova/', views.cadastrar, name='estoque_cadastrar'),
    path('estoque-baixo/', views.estoque_baixo, name='estoque_baixo'),
    path('<int:pk>/', views.detalhe, name='estoque_detalhe'),
]