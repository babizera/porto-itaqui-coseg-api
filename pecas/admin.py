from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils import timezone

from .models import Peca


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'fabricante', 'categoria', 'estoque_atual', 'preco_venda', 'ativo')
    search_fields = ('codigo', 'nome', 'fabricante', 'categoria')
    list_filter = ('categoria', 'ativo', 'unidade')
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

    def get_readonly_fields(self, request, obj=None):
        campos = super().get_readonly_fields(request, obj)
        if obj is not None:
            # Depois do cadastro, o estoque da peça só muda pelo app Estoque
            campos += ('estoque_atual',)
        return campos

    @admin.action(description='Desativar peças selecionadas')
    def desativar(self, request, queryset):
        total = queryset.filter(ativo=True).update(
            ativo=False, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} peça(s) desativada(s).')

    @admin.action(description='Reativar peças selecionadas')
    def reativar(self, request, queryset):
        total = queryset.filter(ativo=False).update(
            ativo=True, atualizado_em=timezone.now(), atualizado_por=request.user)
        self.message_user(request, f'{total} peça(s) reativada(s).')