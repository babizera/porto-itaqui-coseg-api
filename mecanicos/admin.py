from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils import timezone

from .models import Mecanico


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'especialidade', 'data_admissao', 'ativo')
    search_fields = ('nome', 'cpf', 'especialidade')
    list_filter = ('ativo', 'especialidade')
    ordering = ('nome',)
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

    @admin.action(description='Desativar mecânicos selecionados')
    def desativar(self, request, queryset):
        total = queryset.filter(ativo=True).update(
            ativo=False, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} mecânico(s) desativado(s).')

    @admin.action(description='Reativar mecânicos selecionados')
    def reativar(self, request, queryset):
        total = queryset.filter(ativo=False).update(
            ativo=True, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} mecânico(s) reativado(s).')