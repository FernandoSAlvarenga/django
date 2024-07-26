from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from main.bd_config import conecta_no_banco_de_dados
from .forms import ContatoForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout  # Use Django authentication
from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required  # For 'login_required' decorator
from django.views.decorators.csrf import csrf_protect  # Adicione esta linha
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.db import transaction  # Para transações atômicas
from django.http import HttpResponse, JsonResponse
from django.contrib import messages


def login(request):
    request.session['usuario_id'] =""
    try:
        # Tentar estabelecer conexão com o banco de dados (dentro do bloco POST)
        if request.method == 'POST':
            bd = conecta_no_banco_de_dados()

            # Extrair credenciais do usuário do formulário enviado
            email = request.POST['username']
            senha = request.POST['password']
            # usuario1 = authenticate(username=request.POST['username'], password=request.POST['password'])
             # Validar as credenciais
            cursor = bd.cursor()
            cursor.execute("""
                        SELECT *
                        FROM usuarios
                        WHERE email = %s AND senha = %s;
                    """, (email, senha,))
            usuario = cursor.fetchone()
            cursor.close()
            bd.close()
            if usuario:
                request.session['usuario_id'] = usuario[0]  # Iniciar sessão do usuário
                
              
                return redirect('paginainicial')                     
            else:
                print('Email ou senha inválidos.')
                    # Autenticação falhou, exibir mensagem de erro
                mensagem_erro = 'Email ou senha inválidos.'
                return render(request, 'login.html', {'mensagem_erro': mensagem_erro})
             

        else:
            # Se não for uma solicitação POST, renderizar o formulário de login
            return render(request, 'login.html')

    except Exception as e:
        # Se ocorrer um erro de conexão, exibir mensagem de erro
        mensagem_erro = f"Erro ao conectar ao banco de dados: {e}"
        return render(request, 'login.html', {'mensagem_erro': mensagem_erro})
def paginainicial(request):
        if not request.session.get('usuario_id'):
            return redirect('login')
        else:
            return render(request, 'paginainicial.html')
def contatos(request):
     if not request.session.get('usuario_id'):
            return redirect('login')
     else:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        cursor.execute('SELECT * FROM contatos where situacao!="Atendimento" AND situacao!="Finalizado";')
        contatos = cursor.fetchall()
        
        # Renderize o template HTML com os contatos recuperados
        return render(request, 'contatos.html', {"contatos": contatos})
def usuarios(request):
    if not request.session.get('usuario_id'):
            return redirect('login')
    else:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        cursor.execute('SELECT * FROM usuarios;')
        usuarios = cursor.fetchall()
        
        # Renderize o template HTML com os contatos recuperados
        return render(request, 'usuarios.html', {"usuarios": usuarios})
def atenderchamado(request, id):
     if not request.session.get('usuario_id'):
            return redirect('login')
     else:
        usuario_id = request.session['usuario_id']

        try:
            # Connect to the database
            bd = conecta_no_banco_de_dados()
            cursor =  bd.cursor()

            # Update contato's status
            sql = 'UPDATE contatos SET situacao = %s WHERE id_contato = %s;'
            values = ("Atendimento", int(id))
            cursor.execute(sql, values)

            # Insert record into usuario_contato table
            sql = """
                INSERT INTO usuario_contato (usuario_id, contato_id, situacao)
                VALUES (%s, %s, %s);
            """
            values = (int(usuario_id), int(id), "Atendimento")
            cursor.execute(sql, values)

            # Commit changes and close connection
            bd.commit()
            bd.close()

            # Successful update
            return redirect('/pagina_inicial')

        except Exception as e:
            # Handle errors
            print(f"Erro ao atender chamado: {e}")
            return redirect('/contatos')  



#Visto em aula dia 22/07/2024
def excluirususario(request,id):
    if not request.session.get('usuario_id'):
            return redirect('login')
    else:
        try:
            # Estabelecer conexão com o banco de dados (substitua 'seu_banco_de_dados' pelo nome real)
            bd =conecta_no_banco_de_dados()
            cursor = bd.cursor()

            # Evitar SQL injection usando parâmetros nomeados
            sql = 'DELETE FROM usuarios WHERE id = %(user_id)s;'
            params = {'user_id': id}

            cursor.execute(sql, params)
            bd.commit()
            cursor.close()

            messages.success(request, 'Usuário excluído com sucesso!')
            return redirect('paginainicial')

        except Exception as e:
            print(f"Erro ao excluir usuário: {e}")
            messages.error(request, 'Falha ao excluir usuário. Tente novamente mais tarde.')
            return redirect('pagina_inicial')
def editarusuario(request,id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    else:
        id_usuario = id
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        cursor.execute("""
            SELECT id, nome, email
            FROM usuarios
            WHERE id = %s;
        """, (id,))
        dados_usuario = cursor.fetchone()
        cursor.close()
        bd.close()
        if request.method == 'POST':
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            senha = request.POST.get('senha')    
            if not all([nome, email, senha]):
                return render(request, 'usuarios.html')
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            sql = (
                """
                UPDATE usuarios
                SET nome = %s, email = %s, senha = %s
                WHERE id = %s;
                """
            )
            values = (nome, email, senha, id)
            cursor.execute(sql, values)
            bd.commit()  # Assumindo que você tenha gerenciamento de transações
            cursor.close()
            bd.close()

            # Redirecione para a página de sucesso ou exiba a mensagem de confirmação
            return redirect('paginainicial')     

        # Exiba o formulário (assumindo lógica de renderização)
        return render(request, 'editarusuario.html',{'id': id_usuario})
def cadastro(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    else:
        if request.method == 'POST':
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            senha = request.POST.get('senha')
          
      
            # Valide a entrada (assumindo lógica de validação)
            if not all([nome, email, senha]):
                # Lide com erros de validação (por exemplo, exiba mensagens de erro)
                return render(request, 'cadastro.html')

            # Atualize os dados do usuário se a validação for aprovada
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            sql = (
                """
                INSERT INTO usuarios
                SET nome = %s, email = %s, senha = %s;
                """
            )
            values = (nome, email, senha)
            cursor.execute(sql, values)
            bd.commit()  # Assumindo que você tenha gerenciamento de transações
            cursor.close()
            bd.close()

            # Redirecione para a página de sucesso ou exiba a mensagem de confirmação
            return redirect('paginainicial')     

        # Exiba o formulário (assumindo lógica de renderização)
        return render(request, 'cadastro.html')            






def index(request):
    return render(request, 'Guia/index.html')
def sobre(request):
    return render(request, 'Sobre/sobre.html')
def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                # Estabelecer conexão com o banco de dados
                bd = conecta_no_banco_de_dados()

                # Preparar consulta SQL e valores
                nome = form.cleaned_data['nome']
                email = form.cleaned_data['email']
                mensagem = form.cleaned_data['mensagem']
                sql = "INSERT INTO contatos (nome, email, mensagem) VALUES (%s, %s, %s)"
                values = (nome, email, mensagem)

                # Executar consulta SQL e confirmar alterações
                cursor = bd.cursor()
                cursor.execute(sql, values)
                bd.commit()

                # Mensagem de sucesso e redirecionamento
                print(f"Dados do formulário salvos com sucesso!")
                return HttpResponseRedirect('/')

            except Exception as err:
                # Manipular erros de banco de dados
                print(f"Erro ao salvar dados no banco de dados: {err}")
                mensagem_erro = "Ocorreu um erro ao processar o seu contato. Tente novamente mais tarde."
                return render(request, 'erro.html', mensagem_erro=mensagem_erro), 500

            finally:
                # Fechar conexão com o banco de dados se estiver aberta
                if bd is not None:
                    bd.close()

        else:
            # Manipular dados de formulário inválidos
            return render(request, 'contato.html', {'form': form})

    else:
        # Renderizar formulário vazio
        form = ContatoForm()
        return render(request, 'contato.html', {'form': form})
    