from django import forms
from .models import Protocolo, Cliente

class ProtocoloForm(forms.ModelForm):
    clientes = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.filter(ativo=True).order_by('nome'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2-clientes',
            'data-placeholder': 'Digite o nome do cliente para buscar...',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=True,
        label="Clientes",
        help_text="Digite o nome do cliente para buscar. Você pode selecionar múltiplos clientes."
    )

    class Meta:
        model = Protocolo
        fields = ["clientes", "buic_dispositivo", "descricao_problema"]
        widgets = {
            "buic_dispositivo": forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BUIC-001'
            }),
            "descricao_problema": forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente o problema...'
            }),
        }

class AtualizacaoForm(forms.ModelForm):
    class Meta:
        model = Protocolo
        fields = ["descricao_problema"]
        widgets = {
            "descricao_problema": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Adicione a primeira atualização aqui (opcional)"
            }),
        }
        labels = {
            "descricao_problema": "Primeira Atualização (Opcional)"
        }