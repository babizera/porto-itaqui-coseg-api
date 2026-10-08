from django import forms

from .models import Mecanico


class MecanicoForm(forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = [
            'nome', 'cpf',
            'telefone', 'whatsapp', 'email',
            'especialidade', 'registro_profissional', 'data_admissao',
            'observacoes',
        ]