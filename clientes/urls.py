from django.urls import path,include 

from . import views

urlpatterns = [
    path('', views.lista, name='clientes_lista'),
    path('novo/', views.cadastrar, name='clientes_cadastrar'),
    path('<int:pk>/', views.detalhe, name='clientes_detalhe'),
    path('<int:pk>/editar/', views.editar, name='clientes_editar'),
    path('<int:pk>/desativar/', views.desativar, name='clientes_desativar'),
    path('<int:pk>/reativar/', views.reativar, name='clientes_reativar'),
    path('api/', include('clientes.api_urls')),
]