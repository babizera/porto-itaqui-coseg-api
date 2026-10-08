from django import forms

from .models import Servico


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = [
            'nome', 'categoria', 'duracao_estimada_minutos', 'preco',
            'descricao',
        ]