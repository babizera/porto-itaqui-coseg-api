from django.db import models

# Create your models here.
import re

from django.conf import settings
from django.db import models


class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    nome_completo = models.CharField('Nome completo', max_length=150)
    tipo_pessoa = models.CharField('Tipo de pessoa', max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF')
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, unique=True, blank=True, null=True,
                                error_messages={'unique': 'Já existe um cliente com este CPF/CNPJ.'})

    telefone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)

    cep = models.CharField('CEP', max_length=9, blank=True)
    endereco = models.CharField('Endereço', max_length=150, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('UF', max_length=2, blank=True)

    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo

    def clean(self):
        super().clean()
        # Grava o CPF/CNPJ só com números (sem pontos, barra e traço)
        self.cpf_cnpj = re.sub(r'\D', '', self.cpf_cnpj or '') or None

    def save(self, *args, **kwargs):
        # A API não chama o clean: o CPF/CNPJ é limpo também ao salvar
        self.clean()
        super().save(*args, **kwargs)