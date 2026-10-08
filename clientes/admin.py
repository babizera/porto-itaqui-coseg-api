from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf_cnpj', 'telefone', 'ativo')
    search_fields = ('nome_completo', 'cpf_cnpj')
    list_filter = ('ativo',)
    readonly_fields = ('criado_em', 'criado_por', 'atualizado_em', 'atualizado_por')

    def save_model(self, request, obj, form, change):
        # Preenche a auditoria
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # Nenhum cliente é apagado: desmarque "Ativo" para desativar
        return False