from rest_framework import viewsets
from .serializers import ClienteSerializer
from django.shortcuts import render

# Create your views here.
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ClienteForm
from .models import Cliente

def _pesquisar(clientes, termo):
    """Busca por nome, CPF/CNPJ, telefone, WhatsApp ou e-mail."""
    termo = (termo or '').strip()
    if not termo:
        return clientes
    filtro = (
        Q(nome_completo__icontains=termo)
        | Q(email__icontains=termo)
        | Q(telefone__icontains=termo)
        | Q(whatsapp__icontains=termo)
    )
    # O CPF/CNPJ é gravado só com números: compara sem a máscara digitada
    digitos = re.sub(r'\D', '', termo)
    if digitos:
        filtro |= Q(cpf_cnpj__contains=digitos)
    return clientes.filter(filtro)


@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    clientes = _pesquisar(Cliente.objects.all(), termo)
    paginator = Paginator(clientes, 10)
    pagina = request.GET.get('page')
    clientes_paginados = paginator.get_page(pagina)
    return render(request, 'clientes/lista.html', {'clientes': clientes_paginados, 'termo': termo})

@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.criado_por = request.user
            cliente.atualizado_por = request.user
            cliente.save()
            messages.success(request, 'Cliente cadastrado com sucesso.')
            return redirect('clientes_lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'modo': 'novo'})

@login_required
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.atualizado_por = request.user
            cliente.save()
            messages.success(request, 'Cliente atualizado com sucesso.')
            return redirect('clientes_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'modo': 'editar', 'cliente': cliente})

@login_required
def detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/detalhe.html', {'cliente': cliente})

def _alterar_status(request, pk, ativo):
    cliente = get_object_or_404(Cliente, pk=pk)
    if cliente.ativo == ativo:
        situacao = 'ativo' if ativo else 'inativo'
        messages.warning(request, f'O cliente já está {situacao}.')
    else:
        cliente.ativo = ativo
        cliente.atualizado_por = request.user
        cliente.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])
        acao = 'reativado' if ativo else 'desativado'
        messages.success(request, f'Cliente {acao} com sucesso.')
    return redirect('clientes_detalhe', pk=cliente.pk)


@login_required
@require_POST
def desativar(request, pk):
    return _alterar_status(request, pk, ativo=False)


@login_required
@require_POST
def reativar(request, pk):
    return _alterar_status(request, pk, ativo=True)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user, atualizado_por=self.request.user)

    def perform_update(self, serializer):
        serializer.save(atualizado_por=self.request.user)

    def perform_destroy(self, instance):
        # O DELETE não apaga do banco: só desativa o cliente
        instance.ativo = False
        instance.atualizado_por = self.request.user
        instance.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])