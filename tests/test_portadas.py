import sqlite3
from pathlib import Path
from app import create_app
from db import get_db


def test_portada_se_conserva_en_catalogo_y_detalle(app, client, login, post):
    login('carlos@demo.local')
    datos = dict(titulo='Curso con libros', descripcion='Lectura', categoria='Idiomas', nivel='Básico', portada='libros.jpg')
    assert post('/docente/cursos/nuevo', datos).status_code == 302
    with app.app_context():
        curso = get_db().execute('SELECT * FROM cursos WHERE titulo=?', (datos['titulo'],)).fetchone()
        assert curso['imagen_portada'] == 'libros.jpg'
        curso_id = curso['id']
    login()
    assert 'img/libros.jpg' in client.get('/cursos').text
    assert 'img/libros.jpg' in client.get(f'/cursos/{curso_id}').text
    assert client.get('/static/img/libros.jpg').status_code == 200
    login('carlos@demo.local')
    assert post('/docente/cursos/nuevo', {**datos, 'titulo':'Inválido', 'portada':'../../archivo'}).status_code == 400
    with app.app_context():
        assert get_db().execute("SELECT count(*) FROM cursos WHERE titulo='Inválido'").fetchone()[0] == 0


def test_base_anterior_se_actualiza_sin_perder_cursos(tmp_path):
    project = Path(__import__('app').__file__).parent
    esquema_anterior = (project/'schema.sql').read_text().replace(' imagen_portada TEXT,', '')
    archivo = tmp_path/'anterior.db'
    with sqlite3.connect(archivo) as db:
        db.executescript(esquema_anterior)
        db.execute("INSERT INTO usuarios(nombre,correo,password_hash,rol) VALUES('Docente','docente@example.com','hash','docente')")
        db.execute("INSERT INTO cursos(docente_id,titulo,descripcion,categoria,nivel) VALUES(1,'Curso anterior','Prueba','Ciencias','Básico')")
    app = create_app({'TESTING':True,'DB_PATH':str(archivo),'UPLOAD_DIR':str(tmp_path/'uploads')})
    with app.app_context():
        curso = get_db().execute('SELECT * FROM cursos WHERE id=1').fetchone()
        assert curso['titulo'] == 'Curso anterior'
        assert curso['imagen_portada'] is None
    # Un segundo arranque reconoce la migración ya aplicada.
    create_app(dict(app.config))
