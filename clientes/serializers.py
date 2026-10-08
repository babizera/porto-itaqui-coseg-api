from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Cliente

MENSAGEM_DUPLICADO = 'Já existe um cliente com este CPF/CNPJ.'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'nome_completo', 'tipo_pessoa', 'cpf_cnpj',
            'telefone', 'whatsapp', 'email',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'observacoes', 'ativo',
            'criado_em', 'criado_por', 'atualizado_em', 'atualizado_por',
        ]
        # Campos que a API mostra, mas não deixa alterar
        read_only_fields = ['ativo', 'criado_em', 'criado_por', 'atualizado_em', 'atualizado_por']

    def save(self, **kwargs):
        # Dois cadastros ao mesmo tempo com o mesmo documento viram erro 400
        try:
            with transaction.atomic():
                return super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError({'cpf_cnpj': [MENSAGEM_DUPLICADO]})