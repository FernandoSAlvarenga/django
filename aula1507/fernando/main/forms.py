from django import forms

class ContatoForm(forms.Form):
    nome = forms.CharField(max_length=255, label='Nome')
    email = forms.EmailField(label='Email')
    mensagem = forms.CharField(widget=forms.Textarea, label='Mensagem')