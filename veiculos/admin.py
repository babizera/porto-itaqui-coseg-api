from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils import timezone

from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'cliente', 'ano_modelo', 'ativo')
    search_fields = ('placa', 'marca', 'modelo', 'cliente__nome_completo')
    list_filter = ('marca', 'combustivel', 'ativo')
    ordering = ('placa',)
    readonly_fields = ('ativo', 'criado_em', 'criado_por', 'atualizado_em', 'atualizado_por')
    actions = ['desativar', 'reativar']

    def save_model(self, request, obj, form, change):
        # Preenche quem cadastrou (só na criação) e quem alterou por último
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Desativar veículos selecionados')
    def desativar(self, request, queryset):
        total = queryset.filter(ativo=True).update(
            ativo=False, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} veículo(s) desativado(s).')

    @admin.action(description='Reativar veículos selecionados')
    def reativar(self, request, queryset):
        total = queryset.filter(ativo=False).update(
            ativo=True, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} veículo(s) reativado(s).')