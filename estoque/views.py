from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render

from pecas.models import Peca

from .forms import MovimentacaoEstoqueForm
from .models import MovimentacaoEstoque


@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    movimentacoes = MovimentacaoEstoque.objects.select_related('peca', 'ordem_servico')
    if termo:
        movimentacoes = movimentacoes.filter(
            Q(peca__nome__icontains=termo) | Q(peca__codigo__icontains=termo))
    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)
    paginator = Paginator(movimentacoes, 10)
    pagina = request.GET.get('page')
    movimentacoes_paginadas = paginator.get_page(pagina)
    contexto = {
        'movimentacoes': movimentacoes_paginadas,
        'termo': termo,
        'tipo': tipo,
        'tipo_choices': MovimentacaoEstoque.TIPO_CHOICES,
    }
    return render(request, 'estoque/lista.html', contexto)


@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.criado_por = request.user
            movimentacao.atualizado_por = request.user
            movimentacao.save()
            messages.success(
                request,
                f'Movimentação registrada. Estoque de {movimentacao.peca.nome}: '
                f'{movimentacao.estoque_posterior}.')
            return redirect('estoque_lista')
    else:
        form = MovimentacaoEstoqueForm()
    return render(request, 'estoque/form.html', {'form': form})


@login_required
def detalhe(request, pk):
    movimentacao = get_object_or_404(
        MovimentacaoEstoque.objects.select_related('peca', 'ordem_servico'), pk=pk)
    return render(request, 'estoque/detalhe.html', {'movimentacao': movimentacao})


@login_required
def estoque_baixo(request):
    pecas = Peca.objects.filter(ativo=True, estoque_atual__lte=F('estoque_minimo')).order_by('nome')
    return render(request, 'estoque/estoque_baixo.html', {'pecas': pecas})