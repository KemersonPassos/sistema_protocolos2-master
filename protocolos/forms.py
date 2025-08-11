from django import forms
from .models import Protocolo, Cliente

class ProtocoloForm(forms.ModelForm):
    clientes = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Clientes"
    )

    class Meta:
        model = Protocolo
        fields = ["clientes", "buic_dispositivo", "descricao_problema"]
        widgets = {
            "descricao_problema": forms.Textarea(attrs={"rows": 4}),
        }

class AtualizacaoForm(forms.ModelForm):
    class Meta:
        model = Protocolo
        fields = ["descricao_problema"]
        widgets = {
            "descricao_problema": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Adicione a primeira atualização aqui (opcional)"
            }),
        }
        labels = {
            "descricao_problema": "Primeira Atualização (Opcional)"
        }


