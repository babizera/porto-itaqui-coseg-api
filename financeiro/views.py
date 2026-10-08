from django.shortcuts import render

# Create your views here.
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ordens_servico.models import OrdemServico

from .forms import LancamentoForm
from .models import Lancamento


def _total(queryset):
    return queryset.aggregate(total=Sum('valor'))['total'] or Decimal('0')


@login_required
def lista(request):
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    lancamentos = Lancamento.objects.select_related('ordem_servico')
    if tipo:
        lancamentos = lancamentos.filter(tipo=tipo)
    if status:
        lancamentos = lancamentos.filter(status=status)

    pagos = Lancamento.objects.filter(status='PAGO')
    receitas = _total(pagos.filter(tipo='RECEITA'))
    despesas = _total(pagos.filter(tipo='DESPESA'))

    paginator = Paginator(lancamentos, 10)
    pagina = request.GET.get('page')
    contexto = {
        'lancamentos': paginator.get_page(pagina),
        'tipo': tipo,
        'status': status,
        'tipo_choices': Lancamento.TIPO_CHOICES,
        'status_choices': Lancamento.STATUS_CHOICES,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': receitas - despesas,
    }
    return render(request, 'financeiro/lista.html', contexto)


@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = LancamentoForm(request.POST)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.criado_por = request.user
            lancamento.atualizado_por = request.user
            lancamento.save()
            messages.success(request, 'Lançamento cadastrado com sucesso.')
            return redirect('financeiro_lista')
    else:
        form = LancamentoForm()
    return render(request, 'financeiro/form.html', {'form': form, 'modo': 'novo'})


@login_required
def editar(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk)
    if lancamento.status == 'CANCELADO':
        messages.error(request, 'Um lançamento cancelado não pode ser editado.')
        return redirect('financeiro_detalhe', pk=lancamento.pk)
    if request.method == 'POST':
        form = LancamentoForm(request.POST, instance=lancamento)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.atualizado_por = request.user
            lancamento.save()
            messages.success(request, 'Lançamento atualizado com sucesso.')
            return redirect('financeiro_lista')
    else:
        form = LancamentoForm(instance=lancamento)
    return render(request, 'financeiro/form.html', {'form': form, 'modo': 'editar', 'lancamento': lancamento})


@login_required
def detalhe(request, pk):
    lancamento = get_object_or_404(Lancamento.objects.select_related('ordem_servico'), pk=pk)
    return render(request, 'financeiro/detalhe.html', {'lancamento': lancamento})


@login_required
@require_POST
def cancelar(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk)
    if lancamento.status == 'CANCELADO':
        messages.warning(request, 'O lançamento já está cancelado.')
    else:
        lancamento.status = 'CANCELADO'
        lancamento.atualizado_por = request.user
        lancamento.save()
        messages.success(request, 'Lançamento cancelado.')
    return redirect('financeiro_detalhe', pk=lancamento.pk)


@login_required
@require_POST
def gerar_da_os(request, os_pk):
    ordem = get_object_or_404(OrdemServico.objects.select_related('veiculo'), pk=os_pk)
    if ordem.status != 'CONCLUIDA':
        messages.error(request, 'Só é possível gerar a receita de uma OS concluída.')
    elif ordem.total <= 0:
        messages.error(request, 'A OS não tem valor a receber.')
    elif ordem.lancamentos.exclude(status='CANCELADO').exists():
        messages.error(request, 'Esta OS já tem um lançamento no financeiro.')
    else:
        lancamento = Lancamento(
            tipo='RECEITA',
            descricao=f'OS {ordem.pk} - {ordem.veiculo.placa}',
            categoria='Serviços',
            valor=ordem.total,
            data_vencimento=timezone.localdate(),
            ordem_servico=ordem,
        )
        lancamento.criado_por = request.user
        lancamento.atualizado_por = request.user
        lancamento.save()
        messages.success(request, 'Receita da OS gerada no financeiro.')
        return redirect('financeiro_detalhe', pk=lancamento.pk)
    return redirect('ordens_servico_detalhe', pk=ordem.pk)