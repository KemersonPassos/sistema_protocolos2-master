from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Case, When
from .models import Cliente, Protocolo, Atualizacao

# Customização do Admin de Usuários
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_superuser'
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (
            ('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Inline para Atualizações no Admin de Protocolos
class AtualizacaoInline(admin.TabularInline):
    model = Atualizacao
    extra = 0
    fields = ('descricao', 'usuario', 'data_hora')
    readonly_fields = ('usuario', 'data_hora')


# Customização do Admin de Protocolos
@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = (
        'numero', 'status', 'buic_dispositivo', 'usuario_criador', 'data_criacao', 'data_finalizacao'
    )
    list_filter = ('status', 'data_criacao', 'usuario_criador')
    search_fields = ('numero__iexact', 'clientes__nome__icontains', 'descricao_problema__icontains')
    inlines = [AtualizacaoInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by(
            Case(
                When(status='aberto', then=0),
                When(status='em_andamento', then=1),
                When(status='finalizado', then=2),
                default=99,
            )
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for um novo protocolo
            obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # Se for uma nova atualização
                instance.usuario = request.user
            instance.save()
        formset.save_m2m()


# Customização do Admin de Clientes
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_cadastro', 'ativo')
    search_fields = ('nome__icontains', 'email__icontains')
    list_filter = ('ativo', 'data_cadastro')


# Customização da interface administrativa
admin.site.site_header = "Sistema de Gestão de Protocolos"
admin.site.site_title = "Sistema de Protocolos"
admin.site.index_title = "Bem-vindo ao Admin do Sistema de Protocolos"