from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory

from clientes.models import Cliente
from mecanicos.models import Mecanico
from pecas.models import Peca
from servicos.models import Servico
from veiculos.models import Veiculo

from .models import ItemPeca, ItemServico, OrdemServico


class VeiculoSelect(forms.Select):
    """Select de veículos que leva o cliente de cada veículo em data-cliente (usado pelo JS da tela)."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opcao = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            opcao['attrs']['data-cliente'] = value.instance.cliente_id
        return opcao


class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = [
            'cliente', 'veiculo', 'mecanico', 'status',
            'quilometragem_entrada', 'defeito_relatado', 'desconto', 'observacoes',
        ]
        widgets = {'veiculo': VeiculoSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ordem = self.instance
        # Mostra só registros ativos, mas mantém o que já está gravado na OS
        self.fields['cliente'].queryset = Cliente.objects.filter(
            Q(ativo=True) | Q(pk=ordem.cliente_id))
        self.fields['veiculo'].queryset = Veiculo.objects.select_related('cliente').filter(
            Q(ativo=True) | Q(pk=ordem.veiculo_id))
        self.fields['mecanico'].queryset = Mecanico.objects.filter(
            Q(ativo=True) | Q(pk=ordem.mecanico_id))
        # Tira a última opção (cancelado): cancelar só pelo botão Cancelar
        self.fields['status'].choices = OrdemServico.STATUS_CHOICES[:-1]


class ItemServicoForm(forms.ModelForm):
    class Meta:
        model = ItemServico
        fields = ['servico', 'quantidade', 'valor_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servico'].queryset = Servico.objects.filter(
            Q(ativo=True) | Q(pk=self.instance.servico_id))


class ItemPecaForm(forms.ModelForm):
    class Meta:
        model = ItemPeca
        fields = ['peca', 'quantidade', 'valor_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['peca'].queryset = Peca.objects.filter(
            Q(ativo=True) | Q(pk=self.instance.peca_id))


ItemServicoFormSet = inlineformset_factory(
    OrdemServico, ItemServico, form=ItemServicoForm, extra=1, can_delete=True,
)

ItemPecaFormSet = inlineformset_factory(
    OrdemServico, ItemPeca, form=ItemPecaForm, extra=1, can_delete=True,
)