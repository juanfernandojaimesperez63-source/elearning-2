from flask import request, url_for, g
from db import get_db


def destino_volver():
    if g.usuario is None or request.endpoint == 'panel.inicio':
        return None
    endpoint = request.endpoint or ''
    args = request.view_args or {}
    if endpoint in ('materiales.lista', 'evaluaciones.nueva'):
        curso_id = args['id']
        if endpoint == 'evaluaciones.nueva':
            return url_for('materiales.lista', id=curso_id)
        if g.usuario['rol'] == 'estudiante':
            return url_for('cursos.detalle', id=curso_id)
        return url_for('cursos.docente')
    if endpoint in ('evaluaciones.iniciar', 'evaluaciones.editar'):
        evaluacion = get_db().execute('SELECT curso_id FROM evaluaciones WHERE id=?', (args['eid'],)).fetchone()
        if evaluacion:
            return url_for('materiales.lista', id=evaluacion['curso_id'])
    if endpoint == 'evaluaciones.resolver':
        entrega = get_db().execute('SELECT v.curso_id FROM entregas e JOIN evaluaciones v ON v.id=e.evaluacion_id WHERE e.id=? AND e.estudiante_id=?', (args['id'], g.usuario['id'])).fetchone()
        if entrega:
            return url_for('materiales.lista', id=entrega['curso_id'])
    if endpoint == 'calificaciones.resultado':
        return url_for('calificaciones.lista')
    if endpoint == 'cursos.detalle':
        return url_for('cursos.catalogo')
    if endpoint == 'cursos.nuevo':
        return url_for('cursos.docente')
    return url_for('panel.inicio')
