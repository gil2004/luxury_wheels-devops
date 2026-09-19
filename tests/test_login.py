from main import app

def test_login_com_sucesso():
    with app.test_client() as client:
        response = client.post("/login", data={
            "email": "teste@exemplo.pt",
            "password": "password123"
        })
        assert response.status_code == 302  # Redirecionamento após login bem-sucedido

def test_login_com_erro():
    with app.test_client() as client:
        response = client.post("/login", data={
            "email": "teste@exemplo.pt",
            "password": "wrongpassword"
        })
        assert response.status_code == 200  # Página de login com erro