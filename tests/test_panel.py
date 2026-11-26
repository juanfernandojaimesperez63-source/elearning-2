from db import get_db

def test_panel_exige_sesion(client):
    assert client.get('/inicio').status_code == 302
    assert client.get('/evaluaciones').status_code == 302

def test_panel_estudiante_no_filtra_cursos_ajenos(app,client,login,post):
    login()
    assert '¡Hola, Sofía!' in client.get('/inicio').get_data(as_text=True)
    with app.app_context():
        curso=get_db().execute("SELECT id FROM cursos WHERE titulo='Python desde cero'").fetchone()[0]
    assert 'Evaluación de Python' not in client.get('/evaluaciones').get_data(as_text=True)
    post(f'/cursos/{curso}/inscribirse')
    pagina=client.get('/inicio').get_data(as_text=True)
    assert 'Python desde cero' in pagina
    assert 'Inglés conversacional' not in pagina
    assert 'Evaluación de Python' in client.get('/evaluaciones').get_data(as_text=True)
    with app.app_context():
        get_db().execute("UPDATE evaluaciones SET estado='borrador'")
        get_db().commit()
    assert 'Evaluación de Python' not in client.get('/evaluaciones').get_data(as_text=True)
    assert 'Evaluación de Python' not in client.get('/inicio').get_data(as_text=True)

def test_panel_docente_solo_cursos_propios(client,login):
    login('ana@demo.local')
    pagina=client.get('/inicio').get_data(as_text=True)
    assert 'Inglés conversacional' in pagina
    assert 'Python desde cero' not in pagina
    assert 'Evaluación de Python' not in client.get('/evaluaciones').get_data(as_text=True)

def test_plantillas_mockup_y_recursos_locales(client,login,app):
    acceso=client.get('/login').get_data(as_text=True)
    assert 'acceso-layout' in acceso and 'data-ver-clave' in acceso
    for recurso in ['css/app.css','css/componentes.css','img/acceso-referencia.png','img/catalogo-referencia.png','fonts/Inter.ttf']:
        assert client.get('/static/'+recurso).status_code==200
    login()
    for url in ['/inicio','/evaluaciones','/cursos','/mis-cursos','/calificaciones']:
        pagina=client.get(url)
        assert pagina.status_code==200
        assert pagina.headers['Cache-Control']=='no-store'
    contenido=client.get('/inicio').get_data(as_text=True)
    assert 'Foros de discusión' not in contenido and 'Certificados' not in contenido and 'Administrador' not in contenido
