from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import Pizza, Pedido
from .forms import ContatoForm, UserForm, PizzaForm
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from .bd_config import conecta_no_banco_de_dados
from django.contrib.auth.models import User

def index(request):
    return render(request, 'index.html')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, 'menu.html', {'pizzas': pizzas})

@login_required
def pedido_pizza(request, pizza_id):
    pizza = get_object_or_404(Pizza, id=pizza_id)
    Pedido.objects.create(cliente=request.user, pizza=pizza)
    messages.success(request, 'Pedido realizado com sucesso!')
    return redirect('menu')

@login_required
def pedidos_cliente(request):
    pedidos = Pedido.objects.filter(cliente=request.user)
    return render(request, 'pedidos_cliente.html', {'pedidos': pedidos})

@login_required
def pedidos_admin(request):
    if not request.user.is_superuser:
        return redirect('menu')
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos_admin.html', {'pedidos': pedidos})

@login_required
def editar_cliente(request, user_id):
    if not request.user.is_superuser:
        return redirect('menu')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('pedidos_admin')
    else:
        form = UserForm(instance=user)
    return render(request, 'editar_cliente.html', {'form': form})

@login_required
def excluir_cliente(request, user_id):
    if not request.user.is_superuser:
        return redirect('menu')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Cliente excluído com sucesso!')
    return redirect('pedidos_admin')

@csrf_protect
def login(request):
    if request.method == 'POST':
        try:
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            email = request.POST['username']
            senha = request.POST['password']
            cursor.execute("""
                SELECT *
                FROM usuarios
                WHERE email = %s AND senha = %s;
            """, (email, senha,))
            usuario = cursor.fetchone()
            cursor.close()
            bd.close()
            if usuario:
                request.session['usuario_id'] = usuario[0]
                return redirect('pagina_inicial')
            else:
                mensagem_erro = 'Email ou senha inválidos.'
                return render(request, 'login.html', {'mensagem_erro': mensagem_erro})
        except Exception as e:
            mensagem_erro = f"Erro ao conectar ao banco de dados: {e}"
            return render(request, 'login.html', {'mensagem_erro': mensagem_erro})
    else:
        return render(request, 'login.html')

@login_required
def contatos(request):
    try:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        cursor.execute('SELECT * FROM contatos WHERE situacao != "Atendimento" AND situacao != "Finalizado";')
        contatos = cursor.fetchall()
        return render(request, 'contatos.html', {'contatos': contatos})
    except Exception as e:
        mensagem_erro = f"Erro ao recuperar contatos: {e}"
        return render(request, 'erro.html', {'mensagem_erro': mensagem_erro})
    finally:
        if bd:
            bd.close()

@login_required
def atenderchamado(request, id):
    try:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        sql_update = 'UPDATE contatos SET situacao = %s WHERE id_contato = %s;'
        values_update = ('Atendimento', int(id))
        cursor.execute(sql_update, values_update)
        sql_insert = """
            INSERT INTO usuario_contato (usuario_id, contato_id, situacao)
            VALUES (%s, %s, %s);
        """
        values_insert = (request.session['usuario_id'], int(id), 'Atendimento')
        cursor.execute(sql_insert, values_insert)
        bd.commit()
        return redirect('pagina_inicial')
    except Exception as e:
        mensagem_erro = f"Erro ao atender chamado: {e}"
        return render(request, 'erro.html', {'mensagem_erro': mensagem_erro})
    finally:
        if bd:
            bd.close()

@login_required
def sobre(request):
    return render(request, 'Sobre/sobre.html')

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                bd = conecta_no_banco_de_dados()
                cursor = bd.cursor()
                nome = form.cleaned_data['nome']
                email = form.cleaned_data['email']
                mensagem = form.cleaned_data['mensagem']
                cursor.execute("""
                    INSERT INTO contatos (nome, email, mensagem, situacao)
                    VALUES (%s, %s, %s, %s);
                """, (nome, email, mensagem, 'Novo'))
                bd.commit()
                return redirect('pagina_inicial')
            except Exception as e:
                mensagem_erro = f"Erro ao conectar ao banco de dados: {e}"
                return render(request, 'contato.html', {'form': form, 'mensagem_erro': mensagem_erro})
            finally:
                if bd:
                    bd.close()
    else:
        form = ContatoForm()
    return render(request, 'contato.html', {'form': form})
