import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from seed import cargar

@pytest.fixture
def app(tmp_path):
    app = create_app({'TESTING':True,'SECRET_KEY':'pruebas','DB_PATH':str(tmp_path/'test.db'),'UPLOAD_DIR':str(tmp_path/'uploads')})
    with app.app_context(): cargar()
    return app

@pytest.fixture
def client(app): return app.test_client()

@pytest.fixture
def post(client):
    def enviar(url, datos=None, **kwargs):
        client.get('/login')
        with client.session_transaction() as sesion: token = sesion['csrf']
        datos = dict(datos or {})
        datos['csrf'] = token
        return client.post(url, data=datos, **kwargs)
    return enviar

@pytest.fixture
def login(post):
    def entrar(correo='sofia@demo.local'):
        return post('/login', {'correo':correo,'clave':'Abcdef1!'})
    return entrar
