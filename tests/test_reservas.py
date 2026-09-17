import os
import sqlite3
from main import app

def contar_reservas():
    conn = sqlite3.connect(os.environ["DATABASE_PATH"])
    total = conn.execute("SELECT COUNT(*) FROM reservas").fetchone()[0]
    conn.close()
    return total

def test_reserva_com_conflito_nao_e_criada():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['id_cliente'] = 1
            sess['nome'] = 'Cliente Teste'

        antes = contar_reservas()
        r = client.post("/reserva/3", data={
            "data_inicio": "2027-06-01",
            "data_fim": "2027-06-10",
            "forma_pagamento": "Cartão",
        })
       
        depois = contar_reservas()

        assert depois == antes 

def test_reserva_em_datas_livres_e_criada():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['id_cliente'] = 1
            sess['nome'] = 'Cliente Teste'

        antes = contar_reservas()
        client.post("/reserva/1", data={
            "data_inicio": "2028-06-01",
            "data_fim": "2028-06-10",
            "forma_pagamento": "Cartão",
        })
        depois = contar_reservas()

        assert depois == antes + 1