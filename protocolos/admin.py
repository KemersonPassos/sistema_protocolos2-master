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
    extra = 1  # Permite adicionar uma atualização diretamente
    fields = ('descricao', 'usuario', 'data_hora')
    readonly_fields = ('usuario', 'data_hora')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for uma nova atualização
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


# Customização do Admin de Protocolos
@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = (
        'numero', 'status', 'buic_dispositivo', 'usuario_criador', 'data_criacao', 'data_finalizacao'
    )
    list_filter = ('status', 'data_criacao', 'usuario_criador')
    search_fields = ('numero__iexact', 'clientes__nome__icontains', 'descricao_problema__icontains')
    inlines = [AtualizacaoInline]
    
    # Campos organizados em fieldsets
    fieldsets = (
        ('Informações do Protocolo', {
            'fields': ('numero_exibicao', 'clientes', 'buic_dispositivo', 'descricao_problema')
        }),
        ('Status e Controle', {
            'fields': ('status', 'usuario_criador', 'data_criacao', 'data_finalizacao')
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ('numero_exibicao', 'usuario_criador', 'data_criacao', 'data_finalizacao')
    
    # Campos que aparecem ao criar um novo protocolo
    add_fieldsets = (
        ('Novo Protocolo', {
            'fields': ('numero_exibicao', 'clientes', 'buic_dispositivo', 'descricao_problema')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Criando um novo protocolo
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if not obj:  # Criando um novo protocolo
            return ['numero_exibicao']
        return readonly

    def numero_exibicao(self, obj):
        if obj and obj.numero:
            return f"#{obj.numero}"
        else:
            # Para novos protocolos, mostra qual número será gerado
            return f"#{Protocolo.get_proximo_numero()} (será gerado automaticamente)"
    numero_exibicao.short_description = "Número do Protocolo"

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