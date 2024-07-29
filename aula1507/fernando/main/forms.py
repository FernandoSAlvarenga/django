from django import forms
from .models import Pizza, Pedido

class ContatoForm(forms.Form):
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    mensagem = forms.CharField(widget=forms.Textarea)

class UserForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'pizza', 'status']

class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizza
        fields = ['sabor']  # Ajuste os campos conforme necessário
