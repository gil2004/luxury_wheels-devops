from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime, date, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DB_PATH = os.environ["DATABASE_PATH"]
app.secret_key = os.environ['SECRET_KEY'] # Use a secure secret key

@app.route('/')
def home():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos LIMIT 6")
    veiculos_destaque = cursor.fetchall()
    conn.close()
    return render_template('index.html', veiculos=veiculos_destaque)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE email = ? AND password = ?", (email, password))
        cliente = cursor.fetchone()
        conn.close()

        if cliente:
            session['id_cliente'] = cliente[0]
            session['nome'] = cliente[1]
            return redirect("/")
        else:
            return render_template('login.html', erro="Email ou password incorretos!")

    return render_template('login.html')


@app.route('/carros')
def carros():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    pesquisa = request.args.get('pesquisa', '')
    tipo = request.args.get('tipo', '')
    lotacao = request.args.get('lotacao', '')
    preco_max = request.args.get('preco_max', '')
    hoje = date.today().isoformat()
    um_ano_atras = (date.today() - timedelta(days=365)).isoformat()

    query = """
    SELECT * FROM veiculos
    WHERE id_veiculo NOT IN (
        SELECT id_veiculo FROM reservas
        WHERE data_fim >= ? AND data_inicio <= ?
    )
    AND (proxima_revisao IS NULL OR proxima_revisao > ?)
    AND (ultima_legalizacao IS NULL OR ultima_legalizacao >= ?)
    """
    params = [hoje, hoje, hoje, um_ano_atras]

    if pesquisa:
        query += " AND (marca LIKE ? OR modelo LIKE ?)"
        params += [f'%{pesquisa}%', f'%{pesquisa}%']
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if lotacao:
        query += " AND lotacao = ?"
        params.append(lotacao)
    if preco_max:
        query += " AND preco <= ?"
        params.append(preco_max)

    ordenar = request.args.get('ordenar', '')
    if ordenar == 'preco_asc':
        query += " ORDER BY preco ASC"
    elif ordenar == 'preco_desc':
        query += " ORDER BY preco DESC"
    else:
        query += " ORDER BY marca ASC"

    cursor.execute(query, params)
    lista_veiculos = cursor.fetchall()

    cursor.execute("SELECT id_veiculo, data_inicio, data_fim FROM reservas")
    reservas_rows = cursor.fetchall()

    cursor.execute("SELECT * FROM forma_pagamento")
    formas_pagamento = cursor.fetchall()

    conn.close()

    datas_indisponiveis = {}
    for r in reservas_rows:
        id_v = r[0]
        if id_v not in datas_indisponiveis:
            datas_indisponiveis[id_v] = []
        datas_indisponiveis[id_v].append({'inicio': r[1], 'fim': r[2]})

    return render_template('car-list.html', veiculos=lista_veiculos, datas_indisponiveis=json.dumps(datas_indisponiveis), formas_pagamento=formas_pagamento)


@app.route('/registar', methods=['GET', 'POST'])
def registar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['re-password']

        if password != re_password:
            return "As passwords não coincidem!"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE email = ?", (email,))
        cliente_existente = cursor.fetchone()
        if cliente_existente:
            conn.close()
            return "Email já registrado!"

        cursor.execute(
            "INSERT INTO clientes (nome, email, password) VALUES (?, ?, ?)", (nome, email, password)
        )
        conn.commit()
        session['id_cliente'] = cursor.lastrowid
        session['nome'] = nome
        conn.close()
        return redirect("/")

    return render_template('registration.html')


@app.route('/reservas')
def reservas():
    if 'id_cliente' not in session:
        return redirect('/login')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reservas.*, veiculos.marca, veiculos.modelo, veiculos.preco
        FROM reservas
        JOIN veiculos ON reservas.id_veiculo = veiculos.id_veiculo
        WHERE reservas.id_cliente = ?
    """, (session['id_cliente'],))
    minhas_reservas = cursor.fetchall()
    conn.close()
    return render_template('reserva.html', reservas=minhas_reservas)


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        if 'id_cliente' not in session:
            return redirect('/login')

        mensagem = request.form['mensagem']
        id_cliente = session['id_cliente']
        nome = session['nome']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensagens (id_cliente, nome, email, mensagem) VALUES (?, ?, ?, ?)",
            (id_cliente, nome, '', mensagem)
        )
        conn.commit()
        conn.close()
        return render_template('contact.html', sucesso="Mensagem enviada com sucesso!")

    return render_template('contact.html')


@app.route('/reserva/<int:id_veiculo>', methods=['POST', 'GET'])
def reserva(id_veiculo):
    if 'id_cliente' not in session:
        return redirect('/login')

    if request.method == 'POST':
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        forma_pagamento = request.form['forma_pagamento']
        d1 = datetime.strptime(data_inicio, "%Y-%m-%d")
        d2 = datetime.strptime(data_fim, "%Y-%m-%d")
        dias = (d2 - d1).days

        if dias <= 0:
            return redirect('/carros')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM reservas 
            WHERE id_veiculo = ? 
            AND data_fim >= ? 
            AND data_inicio <= ?
        """, (id_veiculo, data_inicio, data_fim))
        reserva_existente = cursor.fetchone()

        if reserva_existente:
            conn.close()
            return redirect('/carros')

        cursor.execute("SELECT * FROM veiculos WHERE id_veiculo = ?", (id_veiculo,))
        veiculo = cursor.fetchone()
        preco_total = veiculo[5] * dias

        cursor.execute(
            "INSERT INTO reservas (id_cliente, id_veiculo, data_inicio, data_fim, preco_total, forma_pagamento) VALUES (?, ?, ?, ?, ?, ?)",
            (session['id_cliente'], id_veiculo, data_inicio, data_fim, preco_total, forma_pagamento)
        )
        conn.commit()
        conn.close()
        return redirect('/reservas')

    return redirect('/carros')


@app.route('/alterar_reserva/<int:id_reserva>', methods=['POST'])
def alterar_reserva(id_reserva):
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']

    d1 = datetime.strptime(data_inicio, "%Y-%m-%d")
    d2 = datetime.strptime(data_fim, "%Y-%m-%d")
    dias = (d2 - d1).days

    if dias <= 0:
        return redirect('/reservas')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reservas 
        WHERE id_veiculo = (SELECT id_veiculo FROM reservas WHERE id_reserva = ?)
        AND id_reserva != ?
        AND data_fim >= ? 
        AND data_inicio <= ?
    """, (id_reserva, id_reserva, data_inicio, data_fim))
    reserva_existente = cursor.fetchone()

    if reserva_existente:
        conn.close()
        minhas_reservas = sqlite3.connect(DB_PATH).cursor().execute("""
            SELECT reservas.*, veiculos.marca, veiculos.modelo, veiculos.preco
            FROM reservas
            JOIN veiculos ON reservas.id_veiculo = veiculos.id_veiculo
            WHERE reservas.id_cliente = ?
        """, (session['id_cliente'],)).fetchall()
        return render_template('reserva.html', reservas=minhas_reservas, erro="O veículo já está reservado para essas datas!")

    cursor.execute("""
        SELECT veiculos.preco FROM reservas
        JOIN veiculos ON reservas.id_veiculo = veiculos.id_veiculo
        WHERE reservas.id_reserva = ?
    """, (id_reserva,))
    preco_dia = cursor.fetchone()[0]
    preco_total = preco_dia * dias

    cursor.execute("""
        UPDATE reservas SET data_inicio = ?, data_fim = ?, preco_total = ?
        WHERE id_reserva = ? AND id_cliente = ?
    """, (data_inicio, data_fim, preco_total, id_reserva, session['id_cliente']))
    conn.commit()
    conn.close()
    return redirect('/reservas')


@app.route('/cancelar_reserva/<int:id_reserva>')
def cancelar_reserva(id_reserva):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id_reserva = ? AND id_cliente = ?",
                   (id_reserva, session['id_cliente']))
    conn.commit()
    conn.close()
    return redirect('/reservas')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/health')
def health():
    return "ok", 200

@app.route('/ready')
def ready():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1 FROM veiculos LIMIT 1")
        conn.close()
        return "ready", 200
    except Exception:
        return "not ready", 503

if __name__ == '__main__':
    app.run(debug=True)