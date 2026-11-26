from flask import Blueprint, render_template, request, g
from auth import rol_requerido
from db import get_db
from evaluaciones import entrega_propia
bp = Blueprint('calificaciones', __name__)

@bp.get('/calificaciones')
@rol_requerido('estudiante')
def lista():
    sql = "SELECT e.*,v.titulo evaluacion,c.titulo curso FROM entregas e JOIN evaluaciones v ON v.id=e.evaluacion_id JOIN cursos c ON c.id=v.curso_id WHERE e.estudiante_id=? AND e.estado='enviada'"
    parametros = [g.usuario['id']]
    if request.args.get('curso'):
        sql += ' AND c.id=?'
        parametros.append(request.args['curso'])
    cursos = get_db().execute('SELECT c.* FROM cursos c JOIN inscripciones i ON i.curso_id=c.id WHERE i.estudiante_id=?', (g.usuario['id'],)).fetchall()
    return render_template('evaluaciones/notas.html', entregas=get_db().execute(sql, parametros).fetchall(), cursos=cursos)

@bp.get('/resultados/<int:id>')
@rol_requerido('estudiante')
def resultado(id):
    entrega = entrega_propia(id)
    if entrega['estado'] != 'enviada':
        from flask import redirect, url_for
        return redirect(url_for('evaluaciones.resolver', id=id))
    datos = get_db().execute('SELECT e.*,v.titulo evaluacion,c.titulo curso FROM entregas e JOIN evaluaciones v ON v.id=e.evaluacion_id JOIN cursos c ON c.id=v.curso_id WHERE e.id=? AND e.estudiante_id=?', (id, g.usuario['id'])).fetchone()
    return render_template('evaluaciones/notas.html', entregas=[datos], cursos=None)
