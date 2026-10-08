from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ItemPeca, ItemServico, OrdemServico


class ItemServicoInline(admin.TabularInline):
    model = ItemServico
    extra = 1


class ItemPecaInline(admin.TabularInline):
    model = ItemPeca
    extra = 1


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'veiculo', 'mecanico', 'status', 'data_abertura', 'total_formatado')
    search_fields = ('veiculo__placa', 'cliente__nome_completo')
    list_filter = ('status', 'mecanico')
    readonly_fields = ('data_abertura', 'data_conclusao', 'total_formatado',
                       'criado_em', 'criado_por', 'atualizado_em', 'atualizado_por')
    inlines = [ItemServicoInline, ItemPecaInline]

    def save_model(self, request, obj, form, change):
        # Preenche quem cadastrou (só na criação) e quem alterou por último
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Os itens da OS (serviços e peças) também guardam quem cadastrou e quem alterou
        for item in formset.save(commit=False):
            if item.pk is None:
                item.criado_por = request.user
            item.atualizado_por = request.user
            item.save()
        for item in formset.deleted_objects:
            item.delete()
        formset.save_m2m()

    @admin.display(description='Total')
    def total_formatado(self, obj):
        return f'R$ {obj.total:.2f}'

    def has_delete_permission(self, request, obj=None):
        return False