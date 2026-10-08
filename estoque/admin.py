from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import MovimentacaoEstoque


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('data', 'peca', 'tipo', 'quantidade', 'estoque_anterior', 'estoque_posterior',
                    'ordem_servico')
    search_fields = ('peca__nome', 'peca__codigo', 'motivo')
    list_filter = ('tipo',)
    readonly_fields = ('estoque_anterior', 'estoque_posterior', 'data',
                       'criado_em', 'criado_por', 'atualizado_em', 'atualizado_por')

    def save_model(self, request, obj, form, change):
        # Preenche quem cadastrou (só na criação) e quem alterou por último
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return obj is None

    def has_delete_permission(self, request, obj=None):
        return False