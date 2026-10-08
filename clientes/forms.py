from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome_completo', 'tipo_pessoa', 'cpf_cnpj',
            'telefone', 'whatsapp', 'email',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'observacoes',
        ]