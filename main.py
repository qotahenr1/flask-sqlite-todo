import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
  CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    complete INTEGER,
    user_id INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
  );
""")

cursor.execute("""
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
  );
""")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdlkj123'

@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/login')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM todos WHERE user_id = ?;',
    (session['user_id'],)
  )
  todos = cursor.fetchall()
  conn.close()

  return render_template(
    'index.html',
    todos = todos
  )

@app.route('/create', methods=['POST'])
def create():
  title = request.form.get('title')
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'INSERT INTO todos(title, complete, user_id) VALUES (?, ?, ?)',
    (title, 0, session['user_id'])
  )
  conn.commit()
  conn.close()
  flash('Todo criado com sucesso', 'success')
  return redirect('/')

@app.route('/delete/<id>')
def delete(id):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'DELETE FROM todos WHERE id = ?;',
    (id,)
  )
  conn.commit()
  conn.close()
  flash('Todo deletado com sucesso', 'success')
  return redirect('/')

@app.route('/complete/<id>')
def complete(id):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'UPDATE todos SET complete = 1 WHERE id = ?;',
    (id,)
  )
  conn.commit()
  conn.close()
  flash('Todo completado com sucesso', 'success')
  return redirect('/')

@app.route('/update/<id>', methods=['POST'])
def update(id):
  title = request.form.get('title')
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'UPDATE todos SET title = ? WHERE id = ?;',
    (title, id)
  )
  conn.commit()
  conn.close()
  flash('Todo editado com sucesso', 'success')
  return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html')

  email = request.form.get('email')
  password = request.form.get('password')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM users WHERE email = ?;',
    (email,)
  )
  user = cursor.fetchone()
  conn.close()

  if (
    not user or
    not check_password_hash(user[3], password)
  ):
    flash('Login incorreto!', 'error')
    return redirect('/login')

  session['user_id'] = user[0]
  flash('Bem vindo, ' + user[1], 'success')
  return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup.html')

  name = request.form.get('name')
  email = request.form.get('email')
  password = request.form.get('password')

  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor.execute(
    'SELECT * FROM users WHERE email = ?;',
    (email,)
  )
  user = cursor.fetchone()

  if user:
    conn.close()
    flash('E-mail já existente', 'error')
    return redirect('/signup')

  cursor.execute(
    'INSERT INTO users (name, email, password) VALUES (?, ?, ?);',
    (name, email, generate_password_hash(password, method='sha256'))
  )

  conn.commit()
  conn.close()
  flash('Usuário criado com sucesso', 'success')
  return redirect('/login')

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  return redirect('/')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))  
  app.run(host='0.0.0.02', port=port)