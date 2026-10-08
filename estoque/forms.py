from django import forms

from ordens_servico.models import OrdemServico
from pecas.models import Peca

from .models import MovimentacaoEstoque


class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['peca', 'tipo', 'quantidade', 'motivo', 'ordem_servico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['peca'].queryset = Peca.objects.filter(ativo=True)
        self.fields['ordem_servico'].queryset = OrdemServico.objects.exclude(status='CANCELADA')