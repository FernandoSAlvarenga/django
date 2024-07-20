import mysql.connector

def conecta_no_banco_de_dados():
    cnx = mysql.connector.connect(host='127.0.0.1', user='root', password='')

    cursor = cnx.cursor()
    cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "aula_django";')

    num_results = cursor.fetchone()[0]

    cnx.close()

    if num_results > 0:
        print('O banco de dados aula_django existe e esta pronto para uso.')
    else:
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )

        cursor = cnx.cursor()
        cursor.execute('CREATE DATABASE aula_django;')
        cnx.commit()

        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='aula_django'
        )

        cursor = cnx.cursor()
        cursor.execute('CREATE TABLE contatos (id_contato INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, mensagem TEXT NOT NULL, situacao VARCHAR(50) NOT NULL);')

        cursor.execute('CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), email VARCHAR(255), senha VARCHAR(255));')

        cursor.execute('CREATE TABLE usuario_contato (usuario_id INT NOT NULL, contato_id INT NOT NULL, situacao VARCHAR(255) NOT NULL, PRIMARY KEY (usuario_id, contato_id), FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE, FOREIGN KEY (contato_id) REFERENCES contatos(id_contato) ON DELETE CASCADE);')
        cnx.commit()

        nome = "ROOT"
        email = "peres@peres.com"
        senha = "12345"
        sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        valores = (nome, email, senha)
        cursor.execute(sql, valores)
        cnx.commit()
        
        cnx.close()
        
    try:
        bd = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='aula_django'
        )
    except mysql.connector.Error as err:
        print("Erro de conexão com o banco de dados:", err)
        raise

    return bd
