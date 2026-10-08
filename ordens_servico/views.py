from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ItemPecaFormSet, ItemServicoFormSet, OrdemServicoForm
from .models import OrdemServico


def _montar_formularios(request, ordem=None):
    dados = request.POST if request.method == 'POST' else None
    form = OrdemServicoForm(dados, instance=ordem)
    servicos = ItemServicoFormSet(dados, instance=ordem, prefix='servicos')
    pecas = ItemPecaFormSet(dados, instance=ordem, prefix='pecas')
    return form, servicos, pecas


def _salvar_itens(request, formset, ordem):
    formset.instance = ordem
    for item in formset.save(commit=False):
        if item.pk is None:
            item.criado_por = request.user
        item.atualizado_por = request.user
        item.save()
    for item in formset.deleted_objects:
        item.delete()


def _salvar(request, form, servicos, pecas):
    with transaction.atomic():
        ordem = form.save(commit=False)
        if ordem.pk is None:
            ordem.criado_por = request.user
        ordem.atualizado_por = request.user
        ordem.save()
        _salvar_itens(request, servicos, ordem)
        _salvar_itens(request, pecas, ordem)
    return ordem


@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    ordens = OrdemServico.objects.select_related('cliente', 'veiculo', 'mecanico')
    if termo:
        ordens = ordens.filter(
            Q(veiculo__placa__icontains=termo.replace(' ', '')) | Q(cliente__nome_completo__icontains=termo))
    if status:
        ordens = ordens.filter(status=status)
    paginator = Paginator(ordens, 10)
    pagina = request.GET.get('page')
    ordens_paginadas = paginator.get_page(pagina)
    contexto = {
        'ordens': ordens_paginadas,
        'termo': termo,
        'status': status,
        'status_choices': OrdemServico.STATUS_CHOICES,
    }
    return render(request, 'ordens_servico/lista.html', contexto)


@login_required
def cadastrar(request):
    form, servicos, pecas = _montar_formularios(request)
    if request.method == 'POST' and all([form.is_valid(), servicos.is_valid(), pecas.is_valid()]):
        ordem = _salvar(request, form, servicos, pecas)
        messages.success(request, f'Ordem de serviço {ordem.pk} aberta com sucesso.')
        return redirect('ordens_servico_detalhe', pk=ordem.pk)
    contexto = {'form': form, 'servicos': servicos, 'pecas': pecas, 'modo': 'novo'}
    return render(request, 'ordens_servico/form.html', contexto)


@login_required
def editar(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    if ordem.status == 'CANCELADA':
        messages.error(request, 'Uma ordem de serviço cancelada não pode ser editada.')
        return redirect('ordens_servico_detalhe', pk=ordem.pk)
    form, servicos, pecas = _montar_formularios(request, ordem)
    if request.method == 'POST' and all([form.is_valid(), servicos.is_valid(), pecas.is_valid()]):
        _salvar(request, form, servicos, pecas)
        messages.success(request, 'Ordem de serviço atualizada com sucesso.')
        return redirect('ordens_servico_detalhe', pk=ordem.pk)
    contexto = {'form': form, 'servicos': servicos, 'pecas': pecas, 'modo': 'editar', 'ordem': ordem}
    return render(request, 'ordens_servico/form.html', contexto)


@login_required
def detalhe(request, pk):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related('cliente', 'veiculo', 'mecanico'), pk=pk)
    contexto = {
        'ordem': ordem,
        'itens_servico': ordem.itens_servico.select_related('servico'),
        'itens_peca': ordem.itens_peca.select_related('peca'),
    }
    return render(request, 'ordens_servico/detalhe.html', contexto)


@login_required
@require_POST
def cancelar(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    if ordem.status == 'CANCELADA':
        messages.warning(request, 'A ordem de serviço já está cancelada.')
    else:
        ordem.status = 'CANCELADA'
        ordem.atualizado_por = request.user
        ordem.save()
        messages.success(request, 'Ordem de serviço cancelada.')
    return redirect('ordens_servico_detalhe', pk=ordem.pk)