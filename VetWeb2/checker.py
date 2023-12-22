from flask import session, redirect
from banco.banco import Banco

from functools import wraps

def check_logged_in(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'logged_in' in session:
			return func(*args, **kwargs)
		return redirect('/login')
	return wrapper

def check_user(email, senha):
	db = Banco()
	cursor = db.get_db()
	sql = """SELECT cpf, nome, email FROM usuario WHERE email=? and senha=?;"""
	valor = cursor.execute(sql, (email, senha))
	return valor.fetchall()
