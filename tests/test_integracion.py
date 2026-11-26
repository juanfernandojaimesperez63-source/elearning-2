from io import BytesIO
from datetime import timedelta
import pytest
from db import get_db
from auth import ahora

def ids(app):
    with app.app_context():
        db=get_db()
        return (db.execute("SELECT id FROM cursos WHERE titulo='Python desde cero'").fetchone()[0], db.execute("SELECT id FROM evaluaciones WHERE titulo='Evaluación de Python'").fetchone()[0])

def inscribir(app,post):
    curso,ev=ids(app)
    post(f'/cursos/{curso}/inscribirse')
    return curso,ev

def test_registro_validaciones(client,post):
    datos={'nombre':'Laura Gómez','correo':'laura@example.com','clave':'Abcdef1!','confirmacion':'Abcdef1!','rol':'docente'}
    assert post('/registro',datos).status_code==302
    assert post('/registro',datos).status_code==400
    for campo,valor in [('nombre',''),('correo','laura@'),('clave','abc'),('confirmacion','otra')]:
        assert post('/registro',{**datos,'correo':'nueva@example.com',campo:valor}).status_code==400
    assert post('/login',{'correo':datos['correo'],'clave':datos['clave']}).status_code==302
    assert client.get('/docente/cursos/nuevo').status_code==403

def test_permisos_logout(client,post,login,app):
    curso,ev=ids(app)
    assert client.get('/mis-cursos').status_code==302
    login()
    assert client.get('/docente/cursos/nuevo').status_code==403
    assert client.get(f'/cursos/{curso}/materiales').status_code==403
    assert post(f'/evaluaciones/{ev}/iniciar').status_code==403
    assert client.get('/calificaciones').headers['Cache-Control']=='no-store'
    post('/logout')
    assert client.get('/calificaciones').status_code==302
    login('ana@demo.local')
    assert client.get(f'/cursos/{curso}/materiales').status_code==403
    assert post(f'/docente/cursos/{curso}/materiales').status_code==403
    assert client.get(f'/docente/evaluaciones/{ev}/editar').status_code==403

def test_cursos_filtros_duplicados(client,login,post,app):
    login('carlos@demo.local')
    datos={'titulo':'Curso nuevo','descripcion':'Práctica','categoria':'Ciencias','nivel':'Avanzado'}
    assert post('/docente/cursos/nuevo',datos).status_code==302
    assert post('/docente/cursos/nuevo',datos).status_code==400
    assert post('/docente/cursos/nuevo',{**datos,'nivel':'Inventado'}).status_code==400
    login()
    pagina=client.get('/cursos?q=Python&categoria=Programación&nivel=Básico').get_data(as_text=True)
    assert 'Python desde cero' in pagina and 'Inglés conversacional' not in pagina
    assert 'No hay resultados' in client.get('/cursos?q=zzz').get_data(as_text=True)
    assert 'Python desde cero' not in client.get('/cursos?q=Python&nivel=Avanzado').get_data(as_text=True)
    curso,_=ids(app)
    post(f'/cursos/{curso}/inscribirse');post(f'/cursos/{curso}/inscribirse')
    with app.app_context():
        assert get_db().execute('SELECT count(*) FROM inscripciones').fetchone()[0]==1
        inactivo=get_db().execute("SELECT id FROM cursos WHERE estado='inactivo'").fetchone()[0]
    assert post(f'/cursos/{inactivo}/inscribirse').status_code==403
    assert 'Diseño avanzado' not in client.get('/cursos').get_data(as_text=True)

@pytest.mark.parametrize('tamano,extension,mime,firma,aceptado',[(5*1024*1024,'.pdf','application/pdf',b'%PDF',True),(10*1024*1024,'.pdf','application/pdf',b'%PDF',True),(11*1024*1024,'.pdf','application/pdf',b'%PDF',False),(20,'.exe','application/pdf',b'%PDF',False),(20,'.pdf','application/pdf',b'xxxx',False),(20,'.pdf','text/plain',b'%PDF',False)])
def test_pdf_bordes(app,client,post,login,tamano,extension,mime,firma,aceptado):
    curso,_=ids(app);login('carlos@demo.local')
    respuesta=post(f'/docente/cursos/{curso}/materiales',{'titulo':'Recurso','tipo':'pdf','archivo':(BytesIO(firma+b' '*(tamano-len(firma))),'prueba'+extension,mime)})
    assert respuesta.status_code==302
    with app.app_context(): assert get_db().execute('SELECT count(*) FROM materiales').fetchone()[0]==int(aceptado)

def test_materiales_crud_y_descarga(app,client,post,login):
    curso,_=ids(app);login('carlos@demo.local')
    post(f'/docente/cursos/{curso}/materiales',{'titulo':'PDF','tipo':'pdf','archivo':(BytesIO(b'%PDF-demo'),'a.pdf','application/pdf')})
    with app.app_context(): mid=get_db().execute('SELECT id FROM materiales').fetchone()[0]
    assert client.get(f'/materiales/{mid}/archivo').status_code==200
    login();assert client.get(f'/materiales/{mid}/archivo').status_code==403
    post(f'/cursos/{curso}/inscribirse');assert client.get(f'/materiales/{mid}/archivo').status_code==200
    login('ana@demo.local');assert client.get(f'/materiales/{mid}/archivo').status_code==403
    login('carlos@demo.local')
    post(f'/docente/cursos/{curso}/materiales',{'accion':'editar','mid':mid,'tipo':'pdf','titulo':'Editado'})
    assert 'Editado' in client.get(f'/cursos/{curso}/materiales').get_data(as_text=True)
    post(f'/docente/cursos/{curso}/materiales',{'accion':'eliminar','mid':mid})
    assert client.get(f'/materiales/{mid}/archivo').status_code==200
    post(f'/docente/cursos/{curso}/materiales',{'accion':'eliminar','mid':mid,'confirmar':'si'})
    assert client.get(f'/materiales/{mid}/archivo').status_code==404
    post(f'/docente/cursos/{curso}/materiales',{'titulo':'Video','tipo':'video','url':'javascript:alert(1)'})
    with app.app_context(): assert get_db().execute('SELECT count(*) FROM materiales').fetchone()[0]==0
    post(f'/docente/cursos/{curso}/materiales',{'titulo':'Video','tipo':'video','url':'https://example.com/video'})
    with app.app_context(): assert get_db().execute('SELECT count(*) FROM materiales').fetchone()[0]==1

def test_error_413(client,post,login,app):
    login('carlos@demo.local');curso,_=ids(app)
    assert post(f'/docente/cursos/{curso}/materiales',{'archivo':(BytesIO(b'x'*(13*1024*1024)),'a.pdf')}).status_code==413

def test_evaluacion_completa_recarga_idor(app,client,post,login):
    login();curso,ev=inscribir(app,post)
    respuesta=post(f'/evaluaciones/{ev}/iniciar');url=respuesta.location
    assert url.startswith('/entregas/')
    pagina=client.get(url).get_data(as_text=True);assert 'data-segundos=' in pagina
    with app.app_context():
        entrega=dict(get_db().execute('SELECT * FROM entregas').fetchone())
        get_db().execute('UPDATE entregas SET iniciada_en=? WHERE id=?',((ahora()-timedelta(minutes=10)).isoformat(),entrega['id']))
        get_db().commit()
        preguntas=get_db().execute('SELECT p.id,o.id opcion FROM preguntas p JOIN opciones o ON o.pregunta_id=p.id WHERE p.evaluacion_id=? AND o.es_correcta=1',(ev,)).fetchall()
        respuestas={'respuesta_'+str(p['id']):str(p['opcion']) for p in preguntas}
    recarga=client.get(url).get_data(as_text=True)
    import re
    assert 1190<=int(re.search(r'data-segundos="(\d+)"',recarga)[1])<=1200
    assert post(f'/evaluaciones/{ev}/iniciar').location==url
    resultado=post(url+'/enviar',respuestas)
    assert '5,0' in client.get(resultado.location).get_data(as_text=True)
    assert post(url+'/enviar',{}).location==resultado.location
    assert post(f'/evaluaciones/{ev}/iniciar').location==resultado.location
    assert '5,0' in client.get('/calificaciones?curso='+str(curso)).get_data(as_text=True)
    login('carlos@demo.local')
    assert 'Hay entregas' in post(f'/docente/evaluaciones/{ev}/eliminar',{'confirmar':'si'},follow_redirects=True).get_data(as_text=True)
    assert 'Hay entregas' in client.get(f'/docente/evaluaciones/{ev}/editar',follow_redirects=True).get_data(as_text=True)
    post('/registro',{'nombre':'Otra','correo':'otra@example.com','clave':'Abcdef1!','confirmacion':'Abcdef1!'})
    login('otra@example.com')
    assert client.get(resultado.location).status_code==404
    assert client.get(url).status_code==404
    assert post(url+'/enviar',respuestas).status_code==404

def formulario_evaluacion():
    return {'titulo':'Borrador secreto','descripcion':'Prueba','fecha_inicio':(ahora()-timedelta(hours=1)).isoformat(),'fecha_limite':(ahora()+timedelta(hours=1)).isoformat(),'duracion_min':'30','pregunta_indice':['0'],'enunciado_0':'¿Correcta?','puntaje_0':'5,0','opcion_0':['Sí','No'],'correcta_0':'0'}

def test_borrador_publicacion_edicion(app,client,post,login):
    curso,_=ids(app);login('carlos@demo.local')
    datos=formulario_evaluacion()
    assert post(f'/docente/cursos/{curso}/evaluaciones/nueva',datos).status_code==302
    with app.app_context(): eid=get_db().execute("SELECT id FROM evaluaciones WHERE titulo='Borrador secreto'").fetchone()[0]
    login();post(f'/cursos/{curso}/inscribirse')
    assert 'Borrador secreto' not in client.get(f'/cursos/{curso}/materiales').get_data(as_text=True)
    assert client.get(f'/evaluaciones/{eid}').status_code==404
    login('carlos@demo.local')
    assert post(f'/docente/evaluaciones/{eid}/editar',{**datos,'titulo':'Editada'}).status_code==302
    with app.app_context():
        get_db().execute('UPDATE preguntas SET puntaje=450 WHERE evaluacion_id=?',(eid,));get_db().commit()
    assert 'exactamente 5,0' in post(f'/docente/evaluaciones/{eid}/publicar',follow_redirects=True).get_data(as_text=True)
    post(f'/docente/evaluaciones/{eid}/editar',datos)
    post(f'/docente/evaluaciones/{eid}/publicar')
    login();assert client.get(f'/evaluaciones/{eid}').status_code==200
    login('carlos@demo.local');post(f'/docente/evaluaciones/{eid}/eliminar',{'confirmar':'si'})
    with app.app_context(): assert get_db().execute('SELECT id FROM evaluaciones WHERE id=?',(eid,)).fetchone() is None

def test_vencida_y_envio_tardio(app,client,post,login):
    login();curso,ev=inscribir(app,post)
    with app.app_context(): vencida=get_db().execute("SELECT id FROM evaluaciones WHERE titulo='Evaluación vencida'").fetchone()[0]
    post(f'/evaluaciones/{vencida}/iniciar')
    with app.app_context(): assert get_db().execute('SELECT count(*) FROM entregas').fetchone()[0]==0
    url=post(f'/evaluaciones/{ev}/iniciar').location
    with app.app_context():
        get_db().execute('UPDATE entregas SET iniciada_en=?',((ahora()-timedelta(hours=1)).isoformat(),));get_db().commit()
    assert 'data-segundos="0"' in client.get(url).get_data(as_text=True)
    assert '0,0' in post(url+'/enviar',follow_redirects=True).get_data(as_text=True)

def test_csrf(client,login):
    login()
    assert client.post('/logout').status_code==403

def test_persistencia(app,client,post,login):
    login();curso,_=inscribir(app,post)
    from app import create_app
    segunda=create_app(dict(app.config))
    with segunda.app_context():
        assert get_db().execute('PRAGMA foreign_keys').fetchone()[0]==1
        assert get_db().execute('SELECT count(*) FROM inscripciones WHERE curso_id=?',(curso,)).fetchone()[0]==1
        assert get_db().execute("SELECT password_hash FROM usuarios WHERE correo='sofia@demo.local'").fetchone()[0]!='Abcdef1!'

@pytest.mark.parametrize('cambio',[
    {'fecha_inicio':'no-fecha'}, {'duracion_min':'0'}, {'duracion_min':'abc'},
    {'pregunta_indice':[]}, {'opcion_0':['Solo una']}, {'correcta_0':'9'},
    {'puntaje_0':'4,5'}, {'puntaje_0':'5,5'}, {'puntaje_0':'NaN'}, {'titulo':''}])
def test_evaluacion_invalida(app,client,post,login,cambio):
    curso,_=ids(app);login('carlos@demo.local')
    cantidad_antes=0
    with app.app_context(): cantidad_antes=get_db().execute('SELECT count(*) FROM evaluaciones').fetchone()[0]
    respuesta=post(f'/docente/cursos/{curso}/evaluaciones/nueva',{**formulario_evaluacion(),**cambio})
    assert respuesta.status_code==200
    assert 'Error:' in respuesta.get_data(as_text=True)
    with app.app_context(): assert get_db().execute('SELECT count(*) FROM evaluaciones').fetchone()[0]==cantidad_antes

def test_pantallas_y_formulario_editor(app,client,login,post):
    assert client.get('/registro').status_code==200
    login('carlos@demo.local');curso,ev=ids(app)
    assert client.get('/docente/cursos/nuevo').status_code==200
    assert client.get(f'/docente/cursos/{curso}/evaluaciones/nueva').status_code==200
    pagina=client.get(f'/docente/evaluaciones/{ev}/editar')
    assert pagina.status_code==200 and 'datetime-local' in pagina.get_data(as_text=True)
    login();post(f'/cursos/{curso}/inscribirse')
    for url in ['/mis-cursos',f'/cursos/{curso}','/calificaciones',f'/cursos/{curso}/materiales']:
        assert client.get(url).status_code==200

def test_opcion_de_otra_pregunta_no_puntua(app,client,login,post):
    login();_,ev=inscribir(app,post)
    url=post(f'/evaluaciones/{ev}/iniciar').location
    with app.app_context():
        opciones=get_db().execute('SELECT p.id pregunta,o.id opcion FROM preguntas p JOIN opciones o ON o.pregunta_id=p.id WHERE p.evaluacion_id=? AND o.es_correcta=1 ORDER BY p.orden',(ev,)).fetchall()
    post(url+'/enviar',{'respuesta_'+str(opciones[0]['pregunta']):str(opciones[1]['opcion'])})
    with app.app_context(): assert get_db().execute('SELECT nota FROM entregas').fetchone()[0]==0

def test_login_real_bloqueo(app,client,post,monkeypatch):
    import auth
    tiempo=ahora()
    monkeypatch.setattr(auth,'ahora',lambda:tiempo)
    for _ in range(5): post('/login',{'correo':'sofia@demo.local','clave':'errónea'})
    assert post('/login',{'correo':'sofia@demo.local','clave':'Abcdef1!'}).status_code==200
    tiempo+=timedelta(minutes=15)
    assert post('/login',{'correo':'sofia@demo.local','clave':'Abcdef1!'}).status_code==302
    assert post('/login',{'correo':'inactiva@demo.local','clave':'Abcdef1!'}).status_code==200


def test_iniciar_evaluacion_desde_formulario(app, client, post, login):
    from html.parser import HTMLParser

    class Formularios(HTMLParser):
        def __init__(self):
            super().__init__()
            self.acciones = []

        def handle_starttag(self, tag, attrs):
            atributos = dict(attrs)
            if tag == 'form' and atributos.get('method') == 'post':
                self.acciones.append(atributos.get('action', ''))

    login()
    _, evaluacion = inscribir(app, post)
    pagina = client.get(f'/evaluaciones/{evaluacion}')
    formularios = Formularios()
    formularios.feed(pagina.get_data(as_text=True))
    accion = next(a for a in formularios.acciones if a.startswith('/evaluaciones/'))
    respuesta = post(accion)
    assert respuesta.status_code == 302
    assert respuesta.location.startswith('/entregas/')
    assert b'id="temporizador"' in client.get(respuesta.location).data
