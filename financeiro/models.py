from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from ordens_servico.models import OrdemServico


class Lancamento(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('CARTAO_CREDITO', 'Cartão de crédito'),
        ('CARTAO_DEBITO', 'Cartão de débito'),
        ('BOLETO', 'Boleto'),
        ('TRANSFERENCIA', 'Transferência'),
    ]

    tipo = models.CharField('Tipo', max_length=7, choices=TIPO_CHOICES)
    descricao = models.CharField('Descrição', max_length=150)
    categoria = models.CharField('Categoria', max_length=60, blank=True)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.01'))])

    data_vencimento = models.DateField('Data de vencimento')
    data_pagamento = models.DateField('Data de pagamento', blank=True, null=True)
    forma_pagamento = models.CharField('Forma de pagamento', max_length=15,
                                       choices=FORMA_PAGAMENTO_CHOICES, blank=True)
    status = models.CharField('Status', max_length=9, choices=STATUS_CHOICES, default='PENDENTE')

    ordem_servico = models.ForeignKey(OrdemServico, verbose_name='Ordem de serviço',
                                      on_delete=models.PROTECT, related_name='lancamentos',
                                      blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        ordering = ['data_vencimento']
        verbose_name = 'Lançamento'
        verbose_name_plural = 'Lançamentos'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.descricao} - R$ {self.valor}'

    def clean(self):
        if self.status == 'PAGO' and not self.data_pagamento:
            raise ValidationError({'data_pagamento': 'Informe a data de pagamento.'})

    @property
    def atrasado(self):
        return self.status == 'PENDENTE' and self.data_vencimento < timezone.localdate()