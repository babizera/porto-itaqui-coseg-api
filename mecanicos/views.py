from django.shortcuts import render

# Create your views here.
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MecanicoForm
from .models import Mecanico

@login_required
def lista(request):
    termo = request.GET.get('q', '').strip()
    mecanicos = Mecanico.objects.all()
    if termo:
        filtro = Q(nome__icontains=termo) | Q(especialidade__icontains=termo)
        digitos = re.sub(r'\D', '', termo)
        if digitos:
            filtro |= Q(cpf__contains=digitos)
        mecanicos = mecanicos.filter(filtro)
    paginator = Paginator(mecanicos, 10)
    pagina = request.GET.get('page')
    mecanicos_paginados = paginator.get_page(pagina)
    return render(request, 'mecanicos/lista.html', {'mecanicos': mecanicos_paginados, 'termo': termo})

@login_required
def cadastrar(request):
    if request.method == 'POST':
        form = MecanicoForm(request.POST)
        if form.is_valid():
            mecanico = form.save(commit=False)
            mecanico.criado_por = request.user
            mecanico.atualizado_por = request.user
            mecanico.save()
            messages.success(request, 'Mecânico cadastrado com sucesso.')
            return redirect('mecanicos_lista')
    else:
        form = MecanicoForm()
    return render(request, 'mecanicos/form.html', {'form': form, 'modo': 'novo'})

@login_required
def editar(request, pk):
    mecanico = get_object_or_404(Mecanico, pk=pk)
    if request.method == 'POST':
        form = MecanicoForm(request.POST, instance=mecanico)
        if form.is_valid():
            mecanico = form.save(commit=False)
            mecanico.atualizado_por = request.user
            mecanico.save()
            messages.success(request, 'Mecânico atualizado com sucesso.')
            return redirect('mecanicos_lista')
    else:
        form = MecanicoForm(instance=mecanico)
    return render(request, 'mecanicos/form.html', {'form': form, 'modo': 'editar', 'mecanico': mecanico})

@login_required
def detalhe(request, pk):
    mecanico = get_object_or_404(Mecanico, pk=pk)
    return render(request, 'mecanicos/detalhe.html', {'mecanico': mecanico})

def _alterar_status(request, pk, ativo):
    mecanico = get_object_or_404(Mecanico, pk=pk)
    if mecanico.ativo == ativo:
        situacao = 'ativo' if ativo else 'inativo'
        messages.warning(request, f'O mecânico já está {situacao}.')
    else:
        mecanico.ativo = ativo
        mecanico.atualizado_por = request.user
        mecanico.save(update_fields=['ativo', 'atualizado_em', 'atualizado_por'])
        acao = 'reativado' if ativo else 'desativado'
        messages.success(request, f'Mecânico {acao} com sucesso.')
    return redirect('mecanicos_detalhe', pk=mecanico.pk)


@login_required
@require_POST
def desativar(request, pk):
    return _alterar_status(request, pk, ativo=False)


@login_required
@require_POST
def reativar(request, pk):
    return _alterar_status(request, pk, ativo=True)

