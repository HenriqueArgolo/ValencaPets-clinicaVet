import sqlite3
import os

class Banco:

    def __init__(self) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'banco.db')

        self.sql_drop_table = """DROP TABLE IF EXISTS usuario;
                            DROP TABLE IF EXISTS cliente;
                            DROP TABLE IF EXISTS pets;"""

        self.sql_create_usuario = """CREATE TABLE usuario (
                                    cpf text PRIMARY KEY,
                                    nome TEXT NOT NULL,
                                    senha TEXT NOT NULL,
                                    email TEXT NOT NULL
                                );"""
        
        self.sql_create_cliente = """CREATE TABLE cliente (
                                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                                    nome_completo TEXT NOT NULL,
                                    cpf TEXT NOT NULL UNIQUE,
                                    telefone TEXT NOT NULL UNIQUE,
                                    email TEXT NOT NULL UNIQUE
                                );"""


        self.sql_create_pet = """CREATE TABLE pets (
                            id_pet INTEGER PRIMARY KEY AUTOINCREMENT,
                            cpfDono TEXT NOT NULL,
                            nome TEXT NOT NULL,
                            especie TEXT NOT NULL,
                            raca TEXT NOT NULL, 
                            cor TEXT NOT NULL,
                            idade TEXT NOT NULL
                        );"""
        
        self.sql_create_produto = """CREATE TABLE IF NOT EXISTS produtos (
                            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                            categoria TEXT NOT NULL,
                            nome TEXT NOT NULL,
                            preco REAL NOT NULL,
                            quantidade_estoque INTEGER NOT NULL
                        );"""
        
        self.sql_create_servico = """CREATE TABLE IF NOT EXISTS servicos (
                            id_procedimento INTEGER PRIMARY KEY AUTOINCREMENT,
                            categoria TEXT NOT NULL,
                            nome TEXT NOT NULL,
                            valor REAL NOT NULL
                        );"""
       
        self.sql_create_atendimento = """CREATE TABLE atendimentos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            pet_id INTEGER,
                            data_atendimento TEXT,
                            procedimento_id INTEGER,
                            produto_id INTEGER,
                            observacao TEXT,  -- Adicione a coluna de observação
                            FOREIGN KEY (pet_id) REFERENCES pets(id_pet),
                            FOREIGN KEY (procedimento_id) REFERENCES servicos(id_procedimento),
                            FOREIGN KEY (produto_id) REFERENCES produtos(id_produto)
                        );"""
        
        
        with sqlite3.connect(db_path) as con:
            self.con = con
            self.cursor = con.cursor()

    def create_schema(self):
        self.cursor.executescript(self.sql_drop_table)
        self.cursor.executescript(self.sql_create_usuario)
        self.cursor.executescript(self.sql_create_cliente)
        self.cursor.executescript(self.sql_create_pet)
        self.cursor.executescript(self.sql_create_produto)
        self.cursor.executescript(self.sql_create_servico)
        self.cursor.executescript(self.sql_create_atendimento)

    def get_db(self):
        return self.cursor
    
    def conexao(self):
        return self.con

    def insert(self, dados):
        sql = """INSERT INTO usuario(nome, cpf, email, senha)
                 VALUES(?, ?, ?, ?)"""
        
        self.cursor.execute(sql, dados)
        self.con.commit()

    def insert_pet(self, dados_pet):
        sql = """INSERT INTO pets(cpfDono, nome, especie, raca, cor, idade)
                 VALUES(?,?,?,?,?,?)"""
        
        self.cursor.execute(sql, dados_pet)
        self.con.commit()

    def get_user(self, user):
        sql = """SELECT cpf, nome, email FROM usuario WHERE cpf=?;"""
        valor = self.cursor.execute(sql, (user,))
        return valor.fetchall()
    
    def salvar_cliente(self, dados_cliente):
        sql = "INSERT INTO cliente (nome_completo, cpf, telefone, email) VALUES (?, ?, ?, ?);"
        self.cursor.execute(sql, dados_cliente)
        self.con.commit()

    def buscar_cliente_por_cpf(self, cpf):
        sql = "SELECT nome_completo, cpf, email, telefone FROM cliente WHERE cpf = ?"
        result = self.cursor.execute(sql, (cpf,)).fetchone()

        if result:
            return {'nome': result[0], 'cpf': result[1], 'email': result[2], 'telefone': result[3]}
        else:
            return None
        
    def editar_cliente(self, cpf, novo_nome, novo_email, novo_telefone):
        cursor = self.con.cursor()
        cursor.execute('''
            UPDATE cliente
            SET nome_completo = ?, email = ?, telefone = ?
            WHERE cpf = ?
        ''', (novo_nome, novo_email, novo_telefone, cpf))
        self.con.commit()
        

    def excluir_cliente(self, cpf):
        sql = "DELETE FROM cliente WHERE cpf = ?;"
        self.cursor.execute(sql, (cpf,))
        self.con.commit()    


    def buscar_pets_por_cpf_dono(self, cpf_dono):
        sql = "SELECT  id_pet, nome, especie, raca, cor, idade FROM pets WHERE cpfDono = ?"
        pets = self.cursor.execute(sql, (cpf_dono,)).fetchall()
        
        if pets:
            return pets
        else:
            return None
    def editar_pet(self, pet_id, nome, especie, raca, cor, idade):
        sql = """
        UPDATE pets
        SET nome = ?, especie = ?, raca = ?, cor = ?, idade = ?
        WHERE id_pet = ?
        """
        dados_pet = (nome, especie, raca, cor, idade, pet_id)
        self.cursor.execute(sql, dados_pet)
        self.con.commit()
        
    def insert_produto(self, categoria, nome, preco, quantidade_estoque):
        sql = """INSERT INTO produtos(categoria, nome, preco, quantidade_estoque)
                 VALUES(?, ?, ?, ?)"""

        dados_produto = (categoria, nome, preco, quantidade_estoque)

        self.cursor.execute(sql, dados_produto)
        self.con.commit()

    def insert_servico(self, categoria, nome, valor):
        sql = """INSERT INTO servicos(categoria, nome, valor)
                 VALUES(?, ?, ?)"""

        dados_procedimento = (categoria, nome, valor)

        self.cursor.execute(sql, dados_procedimento)
        self.con.commit()

    def inserir_atendimento(self, pet_id, data_atendimento, observacao, procedimentos=None, produtos=None):
        sql = """
        INSERT INTO atendimentos (pet_id, data_atendimento, observacao, procedimento_id, produto_id)
        VALUES (?, ?, ?, ?, ?)
        """
        
        if procedimentos is None:
            procedimentos = []
        if produtos is None:
            produtos = []

        for procedimento_id in procedimentos:
            dados_atendimento = (pet_id, data_atendimento, observacao, procedimento_id, None)
            self.cursor.execute(sql, dados_atendimento)

        for produto_id in produtos:
            dados_atendimento = (pet_id, data_atendimento, observacao, None, produto_id)
            self.cursor.execute(sql, dados_atendimento)

        self.con.commit()


    def obter_pet_por_id(self, pet_id):
        sql = "SELECT * FROM pets WHERE id_pet = ?"
        self.cursor.execute(sql, (pet_id,))
        resultado = self.cursor.fetchone()
        return resultado
    

    def obter_todos_servicos(self):
        sql = "SELECT * FROM servicos"
        self.cursor.execute(sql)
        servicos = self.cursor.fetchall()
        return servicos

    def obter_todos_produtos(self):
        sql = "SELECT * FROM produtos"
        self.cursor.execute(sql)
        produtos = self.cursor.fetchall()
        return produtos
    
    def obter_atendimentos_por_pet(self, pet_id):
        sql = "SELECT * FROM atendimentos WHERE pet_id = ?"
        self.cursor.execute(sql, (pet_id,))
        atendimentos = self.cursor.fetchall()
        return atendimentos
    

    
    

if __name__ == '__main__':
    db = Banco()
    dados_usuario = ['Erica', '0002484132', 'erica@financas.com', '0012']
    dados_pet = ['0002484132', 'PetName', 'Dog', 'Golden Retriever', 'Golden', '3 years']

    db.create_schema()
    db.insert(dados_usuario)
    db.insert_pet(dados_pet)



