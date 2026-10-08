from django import forms
from django.db.models import Q

from clientes.models import Cliente

from .models import Veiculo


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'cliente', 'placa', 'marca', 'modelo',
            'ano_fabricacao', 'ano_modelo', 'cor', 'chassi',
            'combustivel', 'quilometragem',
            'observacoes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só clientes ativos, mantendo o dono atual de um veículo já cadastrado
        self.fields['cliente'].queryset = Cliente.objects.filter(
            Q(ativo=True) | Q(pk=self.instance.cliente_id))

    def clean_placa(self):
        # Grava a placa em maiúsculas e sem espaços (ABC1D23)
        return self.cleaned_data['placa'].upper().replace(' ', '')