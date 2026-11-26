import sqlite3
from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort
from auth import rol_requerido
from db import get_db
bp = Blueprint('cursos', __name__)
NIVELES = ('Básico', 'Intermedio', 'Avanzado')
CATEGORIAS = ('Programación', 'Diseño', 'Ciencias', 'Idiomas')
PORTADAS = {
    'programacion-hd.png': 'Programación',
    'diseno-hd.png': 'Diseño',
    'ciencias-hd.png': 'Ciencias',
    'idiomas-hd.png': 'Idiomas',
    'tecnologia.jpg': 'Tecnología',
    'equipo.jpg': 'Trabajo en equipo',
    'libros.jpg': 'Libros y lectura',
}
PORTADAS_CATEGORIA = dict(zip(CATEGORIAS, list(PORTADAS)[:4]))


def portada_curso(curso):
    imagen = curso['imagen_portada']
    if imagen not in PORTADAS:
        imagen = PORTADAS_CATEGORIA.get(curso['categoria'], 'programacion-hd.png')
    return 'img/' + imagen


def curso_por_id(id):
    curso = get_db().execute('SELECT * FROM cursos WHERE id=?', (id,)).fetchone()
    if curso is None: abort(404)
    return curso

def propietario(id):
    curso = curso_por_id(id)
    if curso['docente_id'] != g.usuario['id']: abort(403)
    return curso

def acceso(id):
    curso = curso_por_id(id)
    if g.usuario['rol'] == 'docente':
        if curso['docente_id'] != g.usuario['id']: abort(403)
    elif not get_db().execute('SELECT id FROM inscripciones WHERE curso_id=? AND estudiante_id=?', (id, g.usuario['id'])).fetchone():
        abort(403)
    return curso

@bp.get('/cursos')
@rol_requerido('estudiante')
def catalogo():
    sql = "SELECT c.*,u.nombre docente FROM cursos c JOIN usuarios u ON u.id=c.docente_id WHERE c.estado='activo'"
    valores = []
    for campo, parametro in [('c.titulo', 'q'), ('c.categoria', 'categoria'), ('c.nivel', 'nivel')]:
        valor = request.args.get(parametro, '').strip()
        if valor:
            sql += f' AND {campo} ' + ('LIKE ?' if campo == 'c.titulo' else '= ?')
            valores.append('%' + valor + '%' if campo == 'c.titulo' else valor)
    return render_template('cursos/lista.html', titulo='Explorar cursos', cursos=get_db().execute(sql, valores).fetchall(), filtros=True, niveles=NIVELES, categorias=CATEGORIAS)

@bp.get('/cursos/<int:id>')
@rol_requerido('estudiante')
def detalle(id):
    curso = curso_por_id(id)
    if curso['estado'] != 'activo': abort(404)
    inscrito = get_db().execute('SELECT id FROM inscripciones WHERE curso_id=? AND estudiante_id=?', (id, g.usuario['id'])).fetchone()
    return render_template('cursos/detalle.html', curso=curso, inscrito=inscrito)

@bp.post('/cursos/<int:id>/inscribirse')
@rol_requerido('estudiante')
def inscribir(id):
    if curso_por_id(id)['estado'] != 'activo': abort(403)
    try:
        get_db().execute('INSERT INTO inscripciones(estudiante_id,curso_id) VALUES(?,?)', (g.usuario['id'], id))
        get_db().commit()
        flash('Inscripción exitosa.', 'exito')
    except sqlite3.IntegrityError:
        flash('Ya está inscrito en este curso.', 'advertencia')
    return redirect(url_for('cursos.mis_cursos'))

@bp.get('/mis-cursos')
@rol_requerido('estudiante')
def mis_cursos():
    cursos = get_db().execute('SELECT c.*,u.nombre docente FROM cursos c JOIN usuarios u ON u.id=c.docente_id JOIN inscripciones i ON i.curso_id=c.id WHERE i.estudiante_id=?', (g.usuario['id'],)).fetchall()
    return render_template('cursos/lista.html', titulo='Mis cursos', cursos=cursos)

@bp.get('/docente/cursos')
@rol_requerido('docente')
def docente():
    return render_template('cursos/lista.html', titulo='Mis cursos', cursos=get_db().execute('SELECT c.*,u.nombre docente FROM cursos c JOIN usuarios u ON u.id=c.docente_id WHERE c.docente_id=?', (g.usuario['id'],)).fetchall())

@bp.route('/docente/cursos/nuevo', methods=['GET', 'POST'])
@rol_requerido('docente')
def nuevo():
    errores = {}
    if request.method == 'POST':
        datos = {c: request.form.get(c, '').strip() for c in ('titulo', 'descripcion', 'categoria', 'nivel')}
        for campo in ('titulo', 'descripcion'):
            if not datos[campo]: errores[campo] = 'Campo obligatorio.'
        if datos['categoria'] not in CATEGORIAS: errores['categoria'] = 'Categoría inválida.'
        if datos['nivel'] not in NIVELES: errores['nivel'] = 'Nivel inválido.'
        portada = request.form.get('portada', '')
        if portada and portada not in PORTADAS:
            errores['portada'] = 'Seleccione una portada de la galería.'
        if not errores:
            try:
                get_db().execute('INSERT INTO cursos(docente_id,titulo,descripcion,categoria,nivel,imagen_portada) VALUES(?,?,?,?,?,?)', (g.usuario['id'], *datos.values(), portada or None))
                get_db().commit()
                return redirect(url_for('cursos.docente'))
            except sqlite3.IntegrityError:
                errores['titulo'] = 'Ya tiene un curso con este título.'
    return render_template('cursos/nuevo.html', errores=errores, categorias=CATEGORIAS, niveles=NIVELES, portadas=PORTADAS), 400 if errores else 200
