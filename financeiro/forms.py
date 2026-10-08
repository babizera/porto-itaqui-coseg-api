from django import forms

from .models import Lancamento


class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = [
            'tipo', 'descricao', 'categoria', 'valor',
            'data_vencimento', 'data_pagamento', 'forma_pagamento', 'status',
            'ordem_servico', 'observacoes',
        ]
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tira a última opção (cancelado): cancelar só pelo botão Cancelar
        self.fields['status'].choices = Lancamento.STATUS_CHOICES[:-1]