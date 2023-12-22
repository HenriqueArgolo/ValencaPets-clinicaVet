from flask import app, redirect, request
from checker import check_logged_in
from financas.banco.banco import Banco

@app.route('/editarCliente', methods=['POST'])
def editar_cliente():
    # Obter dados do formulário
    cpf = request.form.get('cpf')
    novo_nome = request.form.get('nome')
    novo_email = request.form.get('email')
    novo_telefone = request.form.get('telefone')

    # Atualizar os dados do cliente no banco de dados
    db = Banco()
    db.editar_cliente(cpf, novo_nome, novo_email, novo_telefone)

    # Redirecionar para a página de busca ou outra página de sua escolha
    return redirect('/home')
