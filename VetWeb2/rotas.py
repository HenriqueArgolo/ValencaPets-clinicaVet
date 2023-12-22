from flask import Flask, render_template,render_template_string, request, session, redirect, url_for
from banco.banco import Banco
from checker import check_logged_in, check_user

app = Flask(__name__)
app.secret_key = 'ksfjgne537hbigw97rtymsgu4'


@app.route('/login', methods=['get', 'post'])
def login() -> 'html':
	return render_template('login.html')


@app.route('/cadastro')
def cadastro() -> 'html':
	return render_template('cadastroUser.html')


@app.route('/cadastro_pet_form')
@check_logged_in
def cadastroPet() -> 'html':
	return render_template('cadastroPet.html')


@app.route('/cadastro_cliente_form')
@check_logged_in
def cadastroCliente() -> 'html':
	return render_template('cliente.html')

@app.route('/cadastro_servicos')
@check_logged_in
def cadastrarServicos() -> 'html':
	return render_template('cadastroServicos.html')

@app.route('/atendimento')
@check_logged_in
def fichaDeAtendimento() -> 'html':
      render_template('ficha_de_atendimento.html')


@app.route('/ficha_pet')
@check_logged_in
def hisotricoPet() ->'html':
      render_template('ficha.html')



@app.route('/cadastro_pet', methods=['post'])
@check_logged_in
def salvar_pet():
    cpfDono = request.form.get('cpfDono')
    nomePet = request.form.get('nomePet')
    especie = request.form.get('especiePet')
    raca = request.form.get('racaPet')
    cor = request.form.get('corPet')
    idade = request.form.get('idadePet')
    db = Banco()
    dados_pet = (cpfDono, nomePet, especie, raca, cor, idade)
    dono = db.buscar_cliente_por_cpf(cpfDono)
    if dono:
        db.insert_pet(dados_pet)
        return redirect('/home')
    else:
        return 'Dono não cadastrado no banco de dados'


@app.route('/salvar_cliente', methods=['post'])
@check_logged_in
def salvar_cliente():
    nome_completo = request.form.get('nomeCompleto')
    cpf = request.form.get('cpf')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    db = Banco()
    dados_cliente = (nome_completo, cpf, telefone, email)
    db.salvar_cliente(dados_cliente)
    return redirect('/home')



@app.route('/salvar', methods=['post'])
def salvar():
	dados = []
	for k, v in request.form.items():
		dados.append(v)
	db = Banco()
	db.insert(dados=dados)	
	return redirect('/home')



@app.route('/editarCliente', methods=['POST'])
@check_logged_in
def editar_cliente():
    cpf = request.form.get('cpf')
    novo_nome = request.form.get('nome')
    novo_email = request.form.get('email')
    novo_telefone = request.form.get('telefone')
    db = Banco()
    db.editar_cliente(cpf, novo_nome, novo_email, novo_telefone)
    dados_cliente = db.buscar_cliente_por_cpf(cpf)
    return render_template('index.html', dados_cliente=dados_cliente)


@app.route('/excluirCliente', methods=['POST'])
@check_logged_in
def excluir_cliente():
    cpf = request.form.get('cpf')
    db = Banco()
    db.excluir_cliente(cpf)
    return redirect('/home')



@app.route('/buscarCliente', methods=['POST'])
@check_logged_in
def buscar_cliente():
    cpf_termo = request.form.get('termoBusca') 
    db = Banco()
    dados_cliente = db.buscar_cliente_por_cpf(cpf_termo)
    dados_pet = db.buscar_pets_por_cpf_dono(cpf_termo)
    if dados_cliente and dados_pet:
        return render_template('index.html', dados_cliente=dados_cliente, dados_pet=dados_pet)
    elif dados_cliente: 
        return render_template('index.html', dados_cliente=dados_cliente)
    else:
        return render_template('index.html', mensagem_erro='Cliente não encontrado')

@app.route('/home')
def home() -> 'html':
    db = Banco()
    dados = db.get_user(session.get('user'))  
    user_data = dados[0][1] if dados else None 
    return render_template('index.html', user=user_data)



@app.route('/autenticar', methods=['post'])
def autenticar() -> 'html':
	dados = check_user(request.form['username'], request.form['password'])
	if len(dados) > 0:
		session['logged_in'] = True
		session['user'] = dados[0][0]
		return redirect('/home')
	return '<h1>Email ou senha estão incorretos</h1>'


@app.route('/cadastrar_produto', methods=['POST'])
@check_logged_in
def cadastrar_produto():
    categoria = request.form.get('product')
    nome = request.form.get('nomeProduto')
    preco = request.form.get('precoProduto')
    quantidade_estoque = request.form.get('quantidadeEstoque')

    if categoria is not None: 
        db = Banco()
        db.insert_produto(categoria, nome, preco, quantidade_estoque)
        return "Produto cadastrado com sucesso!"
    else:
        return "Erro: Categoria não selecionada no formulário."

@app.route('/cadastrar_procedimento', methods=['POST'])
@check_logged_in
def cadastrar_procedimento():
    categoria = request.form['service']
    nome = request.form['nomeProcedimento']
    valor = request.form['valorProcedimento']

    print(f'Categoria: {categoria}, Nome: {nome}, Valor: {valor}')

    db = Banco()  
    db.insert_servico(categoria, nome, valor)
    
    return "Procedimento cadastrado com sucesso!"

@app.route('/ficha_atendimento/<int:pet_id>', methods=['GET', 'POST'])
def ficha_atendimento(pet_id):
    db = Banco()
    pet = db.obter_pet_por_id(pet_id)
    atendimentos = db.obter_atendimentos_por_pet(pet_id)
    servicos = db.obter_todos_servicos()
    produtos = db.obter_todos_produtos()

    if request.method == 'POST':
        data_atendimento = request.form['data_atendimento']
        observacao = request.form['observacao']
        procedimentos = request.form.getlist('procedimento_id')
        produtos = request.form.getlist('produto_id')
        db.inserir_atendimento(pet_id, data_atendimento, observacao, procedimentos, produtos)
        atendimentos = db.obter_atendimentos_por_pet(pet_id)
    return render_template('ficha_atendimento.html', pet=pet, atendimentos=atendimentos, servicos=servicos, produtos=produtos)

@app.route('/historico/<int:pet_id>', methods=['GET', 'POST'])
def ficha_historico(pet_id):
    if request.method == 'POST':
        db = Banco()
        data_atendimento = request.form['data_atendimento']
        observacao = request.form['observacao']
        procedimento_id = int(request.form['procedimento_id'])
        produto_id = int(request.form['produto_id'])
        procedimentos = [procedimento_id] if procedimento_id else []
        produtos = [produto_id] if produto_id else []
        db.inserir_atendimento(pet_id, data_atendimento, observacao, procedimentos, produtos)

    db = Banco()
    pet = db.obter_pet_por_id(pet_id)
    atendimentos = db.obter_atendimentos_por_pet(pet_id)
    servicos = db.obter_todos_servicos()
    produtos = db.obter_todos_produtos()

    return render_template('ficha_atendimento.html', pet=pet, atendimentos=atendimentos, servicos=servicos, produtos=produtos, db=db)

@app.route('/editar_pet/<int:pet_id>', methods=['POST'])
def editar_pet(pet_id):
     if request.method == 'POST':
        nome_pet = request.form.get('nomePet')
        especie_pet = request.form.get('especiePet')
        raca_pet = request.form.get('racaPet')
        cor_pet = request.form.get('corPet')
        idade_pet = request.form.get('idadePet')
        db = Banco()
        db.editar_pet(pet_id, nome_pet, especie_pet, raca_pet, cor_pet, idade_pet)
        cpf = db.buscar_cliente_por_cpf('cpfDono')
        dados_cliente = db.buscar_cliente_por_cpf(cpf)
        return render_template('index.html', dados_cliente=dados_cliente)

@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged_in')
    session.pop('user')

    return redirect(url_for('login'))



app.run(debug=True)
