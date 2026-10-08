from django.db import models

# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from ordens_servico.models import OrdemServico
from pecas.models import Peca


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('AJUSTE', 'Ajuste de inventário'),
    ]

    peca = models.ForeignKey(Peca, verbose_name='Peça', on_delete=models.PROTECT,
                             related_name='movimentacoes')
    tipo = models.CharField('Tipo', max_length=7, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField('Quantidade')
    motivo = models.CharField('Motivo', max_length=150, blank=True)
    ordem_servico = models.ForeignKey(OrdemServico, verbose_name='Ordem de serviço',
                                      on_delete=models.PROTECT, related_name='movimentacoes_estoque',
                                      blank=True, null=True)

    estoque_anterior = models.IntegerField('Estoque anterior', default=0, editable=False)
    estoque_posterior = models.IntegerField('Estoque posterior', default=0, editable=False)
    data = models.DateTimeField('Data', auto_now_add=True)

    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Criado por',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False, related_name='+')
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Atualizado por',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       editable=False, related_name='+')

    class Meta:
        ordering = ['-data']
        verbose_name = 'Movimentação de estoque'
        verbose_name_plural = 'Movimentações de estoque'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.peca} ({self.quantidade})'

    def clean(self):
        if self.tipo in ('ENTRADA', 'SAIDA') and not self.quantidade:
            raise ValidationError({'quantidade': 'Informe uma quantidade maior que zero.'})
        if self.tipo == 'SAIDA' and self.peca_id and self.quantidade \
                and self.quantidade > self.peca.estoque_atual:
            raise ValidationError(
                {'quantidade': f'Estoque insuficiente. Disponível: {self.peca.estoque_atual}.'})

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError('Movimentações não podem ser alteradas. Registre um ajuste.')
        with transaction.atomic():
            peca = Peca.objects.select_for_update().get(pk=self.peca_id)
            self.estoque_anterior = peca.estoque_atual
            if self.tipo == 'ENTRADA':
                novo_estoque = peca.estoque_atual + self.quantidade
            elif self.tipo == 'SAIDA':
                novo_estoque = peca.estoque_atual - self.quantidade
            else:
                novo_estoque = self.quantidade
            if novo_estoque < 0:
                raise ValidationError('A movimentação deixaria o estoque negativo.')
            peca.estoque_atual = novo_estoque
            peca.save(update_fields=['estoque_atual', 'atualizado_em'])
            self.estoque_posterior = novo_estoque
            super().save(*args, **kwargs)