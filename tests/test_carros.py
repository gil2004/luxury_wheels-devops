from main import app

def test_listagem_de_carros():
    with app.test_client() as client:
        response = client.get("/carros")
        assert response.status_code == 200
        assert b"ModeloA" in response.data