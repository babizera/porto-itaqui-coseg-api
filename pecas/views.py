from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PecaForm
from .models import Peca

@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    pecas = Peca.objects.all()
    if termo:
        pecas = pecas.filter(
            Q(nome__icontains=termo) | Q(codigo__icontains=termo)
            | Q(fabricante__icontains=termo) | Q(categoria__icontains=termo))
    paginator = Paginator(pecas, 10)
    pagina = request.GET.get('page')
    pecas_paginadas = paginator.get_page(pagina)
    return render(request, 'pecas/lista.html', {'pecas': pecas_paginadas, 'termo': termo})

@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = PecaForm(request.POST)
        if form.is_valid():
            peca = form.save(commit=False)
            peca.criado_por = request.user
            peca.atualizado_por = request.user
            peca.save()
            messages.success(request, 'Peça cadastrada com sucesso.')
            return redirect('pecas_lista')
    else:
        form = PecaForm()
    return render(request, 'pecas/form.html', {'form': form, 'modo': 'novo'})

@login_required
def editar(request, pk):
    peca = get_object_or_404(Peca, pk=pk)
    if request.method == 'POST':
        form = PecaForm(request.POST, instance=peca)
        if form.is_valid():
            peca = form.save(commit=False)
            peca.atualizado_por = request.user
            peca.save()
            messages.success(request, 'Peça atualizada com sucesso.')
            return redirect('pecas_lista')
    else:
        form = PecaForm(instance=peca)
    return render(request, 'pecas/form.html', {'form': form, 'modo': 'editar', 'peca': peca})

@login_required
def detalhe(request, pk):
    peca = get_object_or_404(Peca, pk=pk)
    return render(request, 'pecas/detalhe.html', {'peca': peca})

def _alterar_status(request, pk, ativo):
    peca = get_object_or_404(Peca, pk=pk)
    if peca.ativo == ativo:
        situacao = 'ativa' if ativo else 'inativa'
        messages.warning(request, f'A peça já está {situacao}.')
    else:
        peca.ativo = ativo
        peca.atualizado_por = request.user
        peca.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])
        acao = 'reativada' if ativo else 'desativada'
        messages.success(request, f'Peça {acao} com sucesso.')
    return redirect('pecas_detalhe', pk=peca.pk)


@login_required
@require_POST
def desativar(request, pk):
    return _alterar_status(request, pk, ativo=False)


@login_required
@require_POST
def reativar(request, pk):
    return _alterar_status(request, pk, ativo=True)