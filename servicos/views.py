from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ServicoForm
from .models import Servico

@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    servicos = Servico.objects.all()
    if termo:
        servicos = servicos.filter(Q(nome__icontains=termo) | Q(categoria__icontains=termo))
    paginator = Paginator(servicos, 10)
    pagina = request.GET.get('page')
    servicos_paginados = paginator.get_page(pagina)
    return render(request, 'servicos/lista.html', {'servicos': servicos_paginados, 'termo': termo})

@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = ServicoForm(request.POST)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.criado_por = request.user
            servico.atualizado_por = request.user
            servico.save()
            messages.success(request, 'Serviço cadastrado com sucesso.')
            return redirect('servicos_lista')
    else:
        form = ServicoForm()
    return render(request, 'servicos/form.html', {'form': form, 'modo': 'novo'})

@login_required
def editar(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.atualizado_por = request.user
            servico.save()
            messages.success(request, 'Serviço atualizado com sucesso.')
            return redirect('servicos_lista')
    else:
        form = ServicoForm(instance=servico)
    return render(request, 'servicos/form.html', {'form': form, 'modo': 'editar', 'servico': servico})

@login_required
def detalhe(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    return render(request, 'servicos/detalhe.html', {'servico': servico})

def _alterar_status(request, pk, ativo):
    servico = get_object_or_404(Servico, pk=pk)
    if servico.ativo == ativo:
        situacao = 'ativo' if ativo else 'inativo'
        messages.warning(request, f'O serviço já está {situacao}.')
    else:
        servico.ativo = ativo
        servico.atualizado_por = request.user
        servico.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])
        acao = 'reativado' if ativo else 'desativado'
        messages.success(request, f'Serviço {acao} com sucesso.')
    return redirect('servicos_detalhe', pk=servico.pk)


@login_required
@require_POST
def desativar(request, pk):
    return _alterar_status(request, pk, ativo=False)


@login_required
@require_POST
def reativar(request, pk):
    return _alterar_status(request, pk, ativo=True)

