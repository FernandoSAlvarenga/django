from django.db import models
from django.contrib.auth.models import User

class Pizza(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    imagem = models.ImageField(upload_to='pizzas/', null=True, blank=True)

    def __str__(self):
        return self.nome

class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pendente', 'Pendente'), ('Pronto', 'Pronto'), ('Entregue', 'Entregue')])

    def __str__(self):
        return f'Pedido {self.id} - {self.pizza.nome}'
