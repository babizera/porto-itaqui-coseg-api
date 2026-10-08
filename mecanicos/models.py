from django.db import models

# Create your models here.
import re

from django.conf import settings
from django.db import models


class Mecanico(models.Model):
    nome = models.CharField('Nome', max_length=150)
    cpf = models.CharField('CPF', max_length=14, blank=True, null=True)

    telefone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)

    especialidade = models.CharField('Especialidade', max_length=100, blank=True)
    registro_profissional = models.CharField('Registro profissional', max_length=50, blank=True)
    data_admissao = models.DateField('Data de admissão', blank=True, null=True)
    salario_base = models.DecimalField('Salário/base de custo', max_digits=10, decimal_places=2,
                                        blank=True, null=True)

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
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()
        # Grava o CPF só com números (sem pontos e traço)
        self.cpf = re.sub(r'\D', '', self.cpf or '') or None