from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Servico(models.Model):
    CATEGORIA_CHOICES = [
        ('MECANICA', 'Mecânica geral'),
        ('ELETRICA', 'Elétrica'),
        ('SUSPENSAO', 'Suspensão'),
        ('FREIOS', 'Freios'),
        ('MOTOR', 'Motor'),
        ('AR_CONDICIONADO', 'Ar-condicionado'),
        ('FUNILARIA', 'Funilaria e pintura'),
        ('REVISAO', 'Revisão'),
        ('OUTROS', 'Outros'),
    ]

    nome = models.CharField('Nome', max_length=150)
    descricao = models.TextField('Descrição', blank=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='OUTROS')
    duracao_estimada_minutos = models.PositiveIntegerField('Duração estimada (minutos)', default=60)
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)])

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

    @property
    def duracao_formatada(self):
        horas, minutos = divmod(self.duracao_estimada_minutos, 60)
        if horas and minutos:
            return f'{horas}h{minutos:02d}min'
        if horas:
            return f'{horas}h'
        return f'{minutos}min'