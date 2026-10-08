from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import VeiculoForm
from .models import Veiculo

@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    veiculos = Veiculo.objects.select_related('cliente')
    if termo:
        veiculos = veiculos.filter(
            Q(placa__icontains=termo.replace(' ', '')) | Q(modelo__icontains=termo)
            | Q(cliente__nome_completo__icontains=termo))
    paginator = Paginator(veiculos, 10)
    pagina = request.GET.get('page')
    veiculos_paginados = paginator.get_page(pagina)
    return render(request, 'veiculos/lista.html', {'veiculos': veiculos_paginados, 'termo': termo})

@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.criado_por = request.user
            veiculo.atualizado_por = request.user
            veiculo.save()
            messages.success(request, 'Veículo cadastrado com sucesso.')
            return redirect('veiculos_lista')
    else:
        form = VeiculoForm()
    return render(request, 'veiculos/form.html', {'form': form, 'modo': 'novo'})

@login_required
def editar(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.atualizado_por = request.user
            veiculo.save()
            messages.success(request, 'Veículo atualizado com sucesso.')
            return redirect('veiculos_lista')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'veiculos/form.html', {'form': form, 'modo': 'editar', 'veiculo': veiculo})

@login_required
def detalhe(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    return render(request, 'veiculos/detalhe.html', {'veiculo': veiculo})

def _alterar_status(request, pk, ativo):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if veiculo.ativo == ativo:
        situacao = 'ativo' if ativo else 'inativo'
        messages.warning(request, f'O veículo já está {situacao}.')
    else:
        veiculo.ativo = ativo
        veiculo.atualizado_por = request.user
        veiculo.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])
        acao = 'reativado' if ativo else 'desativado'
        messages.success(request, f'Veículo {acao} com sucesso.')
    return redirect('veiculos_detalhe', pk=veiculo.pk)


@login_required
@require_POST
def desativar(request, pk):
    return _alterar_status(request, pk, ativo=False)


@login_required
@require_POST
def reativar(request, pk):
    return _alterar_status(request, pk, ativo=True)