from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from mecanicos.models import Mecanico
from pecas.models import Peca
from servicos.models import Servico
from veiculos.models import Veiculo


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', on_delete=models.PROTECT,
                                related_name='ordens_servico')
    veiculo = models.ForeignKey(Veiculo, verbose_name='Veículo', on_delete=models.PROTECT,
                                related_name='ordens_servico')
    mecanico = models.ForeignKey(Mecanico, verbose_name='Mecânico responsável', on_delete=models.PROTECT,
                                 related_name='ordens_servico', blank=True, null=True)

    status = models.CharField('Status', max_length=12, choices=STATUS_CHOICES, default='ABERTA')
    quilometragem_entrada = models.PositiveIntegerField('Quilometragem na entrada', default=0)
    defeito_relatado = models.TextField('Defeito relatado')
    observacoes = models.TextField('Observações', blank=True)
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0,
                                   validators=[MinValueValidator(0)])

    data_abertura = models.DateTimeField('Data de abertura', auto_now_add=True)
    data_conclusao = models.DateTimeField('Data de conclusão', blank=True, null=True)

    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        ordering = ['-data_abertura']
        verbose_name = 'Ordem de serviço'
        verbose_name_plural = 'Ordens de serviço'

    def __str__(self):
        return f'OS {self.pk} - {self.veiculo.placa}'

    def clean(self):
        if self.cliente_id and self.veiculo_id and self.veiculo.cliente_id != self.cliente_id:
            raise ValidationError({'veiculo': 'Este veículo não pertence ao cliente selecionado.'})

    def save(self, *args, **kwargs):
        if self.status == 'CONCLUIDA' and not self.data_conclusao:
            self.data_conclusao = timezone.now()
        elif self.status != 'CONCLUIDA':
            self.data_conclusao = None
        super().save(*args, **kwargs)

    @property
    def total_servicos(self):
        if not self.pk:
            return Decimal('0')
        return sum((item.subtotal for item in self.itens_servico.all()), Decimal('0'))

    @property
    def total_pecas(self):
        if not self.pk:
            return Decimal('0')
        return sum((item.subtotal for item in self.itens_peca.all()), Decimal('0'))

    @property
    def total(self):
        return max(self.total_servicos + self.total_pecas - self.desconto, Decimal('0'))


class ItemServico(models.Model):
    ordem = models.ForeignKey(OrdemServico, verbose_name='Ordem de serviço', on_delete=models.CASCADE,
                              related_name='itens_servico')
    servico = models.ForeignKey(Servico, verbose_name='Serviço', on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField('Quantidade', default=1, validators=[MinValueValidator(1)])
    valor_unitario = models.DecimalField('Valor unitário', max_digits=10, decimal_places=2,
                                         blank=True, null=True, validators=[MinValueValidator(0)],
                                         help_text='Deixe em branco para usar o preço do serviço.')

    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        verbose_name = 'Serviço da OS'
        verbose_name_plural = 'Serviços da OS'

    def __str__(self):
        return f'{self.servico} x{self.quantidade}'

    def save(self, *args, **kwargs):
        if self.valor_unitario is None:
            self.valor_unitario = self.servico.preco
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return (self.valor_unitario or Decimal('0')) * self.quantidade


class ItemPeca(models.Model):
    ordem = models.ForeignKey(OrdemServico, verbose_name='Ordem de serviço', on_delete=models.CASCADE,
                              related_name='itens_peca')
    peca = models.ForeignKey(Peca, verbose_name='Peça', on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField('Quantidade', default=1, validators=[MinValueValidator(1)])
    valor_unitario = models.DecimalField('Valor unitário', max_digits=10, decimal_places=2,
                                         blank=True, null=True, validators=[MinValueValidator(0)],
                                         help_text='Deixe em branco para usar o preço de venda da peça.')

    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        verbose_name = 'Peça da OS'
        verbose_name_plural = 'Peças da OS'

    def __str__(self):
        return f'{self.peca} x{self.quantidade}'

    def save(self, *args, **kwargs):
        if self.valor_unitario is None:
            self.valor_unitario = self.peca.preco_venda
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return (self.valor_unitario or Decimal('0')) * self.quantidade