from django import forms

from .models import Peca


class PecaForm(forms.ModelForm):
    class Meta:
        model = Peca
        fields = [
            'codigo', 'nome', 'fabricante', 'categoria',
            'unidade', 'estoque_atual', 'estoque_minimo', 'localizacao',
            'preco_custo', 'preco_venda', 'fornecedor', 'descricao',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Depois do cadastro, o estoque da peça só muda pelo app Estoque
            self.fields['estoque_atual'].disabled = True