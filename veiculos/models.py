from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from clientes.models import Cliente


class Veiculo(models.Model):
    COMBUSTIVEL_CHOICES = [
        ('FLEX', 'Flex'), ('GASOLINA', 'Gasolina'), ('ETANOL', 'Etanol'),
        ('DIESEL', 'Diesel'), ('GNV', 'GNV'), ('ELETRICO', 'Elétrico'), ('HIBRIDO', 'Híbrido'),
    ]

    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', on_delete=models.PROTECT, related_name='veiculos')

    placa = models.CharField('Placa', max_length=8, unique=True,
                             error_messages={'unique': 'Já existe um veículo cadastrado com esta placa.'})
    marca = models.CharField('Marca', max_length=60)
    modelo = models.CharField('Modelo', max_length=60)
    ano_fabricacao = models.PositiveIntegerField('Ano de fabricação', blank=True, null=True)
    ano_modelo = models.PositiveIntegerField('Ano do modelo', blank=True, null=True)
    cor = models.CharField('Cor', max_length=30, blank=True)
    chassi = models.CharField('Chassi', max_length=17, blank=True)
    combustivel = models.CharField('Combustível', max_length=10, choices=COMBUSTIVEL_CHOICES, default='FLEX')
    quilometragem = models.PositiveIntegerField('Quilometragem', default=0)

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
        ordering = ['placa']

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'

    def save(self, *args, **kwargs):
        if self.placa:
            self.placa = self.placa.upper().replace(' ', '')
        super().save(*args, **kwargs)