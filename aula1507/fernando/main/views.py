from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import ContatoForm
from main.bd_config import conecta_no_banco_de_dados
import mysql.connector
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect  # Adicione esta linha

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        try:
            # Estabelecer conexão com o banco de dados
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()

            # Extrair credenciais do formulário
            email = request.POST['username']
            senha = request.POST['password']

            # Consultar banco de dados para verificar credenciais
            cursor.execute("""
                SELECT *
                FROM usuarios
                WHERE email = %s AND senha = %s;
            """, (email, senha,))
            usuario = cursor.fetchone()

            cursor.close()
            bd.close()

            if usuario:
                # Iniciar sessão do usuário
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

def logout_view(request):
    request.session['usuario_id'] = ""
    return redirect('login')

@login_required
def pagina_inicial(request):
    return render(request, 'Guia/index.html')

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

        # Atualizar status do contato
        sql_update = 'UPDATE contatos SET situacao = %s WHERE id_contato = %s;'
        values_update = ('Atendimento', int(id))
        cursor.execute(sql_update, values_update)

        # Inserir registro na tabela usuario_contato
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
def index(request):
    return render(request, 'Guia/index.html')

@login_required
def sobre(request):
    return render(request, 'Sobre/sobre.html')

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                bd = conecta_no_banco_de_dados()

                # Preparar consulta SQL e valores
                nome = form.cleaned_data['nome']
                email = form.cleaned_data['email']
                mensagem = form.cleaned_data['mensagem']
                sql = "INSERT INTO contatos (nome, email, mensagem) VALUES (%s, %s, %s)"
                values = (nome, email, mensagem)

                cursor = bd.cursor()
                cursor.execute(sql, values)
                bd.commit()

                print(f"Dados do formulário salvos com sucesso!")
                return HttpResponseRedirect('/')

            except Exception as err:
                print(f"Erro ao salvar dados no banco de dados: {err}")
                mensagem_erro = "Ocorreu um erro ao processar o seu contato. Tente novamente mais tarde."
                return render(request, 'erro.html', {'mensagem_erro': mensagem_erro}), 500

            finally:
                if bd:
                    bd.close()

        else:
            return render(request, 'contato.html', {'form': form})

    else:
        form = ContatoForm()
        return render(request, 'contato.html', {'form': form})
