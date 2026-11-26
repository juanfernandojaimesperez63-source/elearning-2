"""Vistas de navegación sobre cursos, evaluaciones y notas del MVP."""
from flask import Blueprint, g, render_template
from auth import login_required, ahora
from db import get_db
from evaluaciones import fecha
bp = Blueprint('panel', __name__)


def cursos_usuario():
    db = get_db()
    if g.usuario['rol'] == 'docente':
        return db.execute('SELECT c.*,u.nombre docente FROM cursos c JOIN usuarios u ON u.id=c.docente_id WHERE c.docente_id=? ORDER BY c.id DESC', (g.usuario['id'],)).fetchall()
    return db.execute('SELECT c.*,u.nombre docente FROM cursos c JOIN usuarios u ON u.id=c.docente_id JOIN inscripciones i ON i.curso_id=c.id WHERE i.estudiante_id=? ORDER BY c.id DESC', (g.usuario['id'],)).fetchall()


def evaluaciones_usuario():
    db = get_db()
    if g.usuario['rol'] == 'docente':
        return [dict(e) for e in db.execute('SELECT v.*,c.titulo curso,NULL entrega_id,NULL entrega_estado,NULL nota FROM evaluaciones v JOIN cursos c ON c.id=v.curso_id WHERE c.docente_id=? ORDER BY v.fecha_limite', (g.usuario['id'],))]
    filas = db.execute("SELECT v.*,c.titulo curso,e.id entrega_id,e.estado entrega_estado,e.nota FROM evaluaciones v JOIN cursos c ON c.id=v.curso_id JOIN inscripciones i ON i.curso_id=c.id LEFT JOIN entregas e ON e.evaluacion_id=v.id AND e.estudiante_id=i.estudiante_id WHERE i.estudiante_id=? AND v.estado='publicada' ORDER BY v.fecha_limite", (g.usuario['id'],)).fetchall()
    evaluaciones = []
    for fila in filas:
        e = dict(fila)
        e['disponible'] = fecha(e['fecha_inicio']) <= ahora() <= fecha(e['fecha_limite'])
        e['situacion'] = 'Completada' if e['entrega_estado'] == 'enviada' else 'En curso' if e['entrega_estado'] == 'en_curso' else 'Disponible' if e['disponible'] else 'Fuera de fechas'
        evaluaciones.append(e)
    return evaluaciones


@bp.get('/inicio')
@login_required
def inicio():
    cursos = cursos_usuario()
    evaluaciones = evaluaciones_usuario()
    enviadas = [e for e in evaluaciones if e['entrega_estado'] == 'enviada']
    promedio = round(sum(e['nota'] for e in enviadas) / len(enviadas)) if enviadas else None
    return render_template('panel.html', cursos=cursos, evaluaciones=evaluaciones, enviadas=enviadas, promedio=promedio)


@bp.get('/evaluaciones')
@login_required
def lista_evaluaciones():
    return render_template('evaluaciones/lista.html', evaluaciones=evaluaciones_usuario())
