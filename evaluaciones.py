from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort
from auth import rol_requerido, ahora
from cursos import acceso, propietario
from db import get_db
from servicios.validaciones import centesimas, suma_valida
from servicios.calificar import calcular_nota
bp = Blueprint('evaluaciones', __name__)
ZONA_LOCAL = timezone(timedelta(hours=-5))

def fecha(valor):
    try:
        valor = datetime.fromisoformat(valor)
        return (valor.replace(tzinfo=ZONA_LOCAL) if valor.tzinfo is None else valor).astimezone(timezone.utc)
    except (ValueError, TypeError):
        raise ValueError('Fecha inválida.') from None

def obtener(eid):
    evaluacion = get_db().execute('SELECT * FROM evaluaciones WHERE id=?', (eid,)).fetchone()
    if evaluacion is None: abort(404)
    return evaluacion

def preguntas_de(eid):
    preguntas = [dict(p) for p in get_db().execute('SELECT * FROM preguntas WHERE evaluacion_id=? ORDER BY orden', (eid,))]
    for p in preguntas:
        p['opciones'] = [dict(o) for o in get_db().execute('SELECT * FROM opciones WHERE pregunta_id=? ORDER BY id', (p['id'],))]
        p['correcta'] = next((o['id'] for o in p['opciones'] if o['es_correcta']), None)
    return preguntas

def validar(evaluacion, preguntas):
    if not evaluacion['titulo'].strip(): raise ValueError('El título es obligatorio.')
    if fecha(evaluacion['fecha_inicio']) >= fecha(evaluacion['fecha_limite']): raise ValueError('El inicio debe ser anterior al límite.')
    if int(evaluacion['duracion_min']) <= 0: raise ValueError('La duración debe ser mayor que cero.')
    if not preguntas: raise ValueError('Agregue al menos una pregunta.')
    for p in preguntas:
        if not p['enunciado'].strip() or p['puntaje'] <= 0: raise ValueError('Pregunta o puntaje inválido.')
        if len(p['opciones']) < 2 or any(not o['texto'].strip() for o in p['opciones']) or sum(o['es_correcta'] for o in p['opciones']) != 1:
            raise ValueError('Cada pregunta requiere al menos dos opciones y exactamente una correcta.')
    if not suma_valida(p['puntaje'] for p in preguntas): raise ValueError('Los puntajes deben sumar exactamente 5,0.')

def leer_formulario():
    datos = {c: request.form.get(c, '').strip() for c in ('titulo', 'descripcion', 'fecha_inicio', 'fecha_limite')}
    datos['fecha_inicio'] = fecha(datos['fecha_inicio']).isoformat()
    datos['fecha_limite'] = fecha(datos['fecha_limite']).isoformat()
    try: datos['duracion_min'] = int(request.form.get('duracion_min', ''))
    except ValueError: raise ValueError('Duración inválida.') from None
    preguntas = []
    for indice in request.form.getlist('pregunta_indice'):
        textos = request.form.getlist('opcion_' + indice)
        correcta = request.form.get('correcta_' + indice)
        preguntas.append({'enunciado': request.form.get('enunciado_' + indice, ''), 'puntaje': centesimas(request.form.get('puntaje_' + indice, '')), 'opciones': [{'texto': t, 'es_correcta': int(str(i) == correcta)} for i, t in enumerate(textos)]})
    validar(datos, preguntas)
    return datos, preguntas

def recuperar_preguntas():
    """Conserva lo escrito al mostrar un error de validación."""
    return [{'enunciado': request.form.get('enunciado_' + i, ''),
             'puntaje': 0, 'valor_puntaje': request.form.get('puntaje_' + i, ''),
             'opciones': [{'texto': t, 'es_correcta': str(n) == request.form.get('correcta_' + i)}
                          for n, t in enumerate(request.form.getlist('opcion_' + i))]}
            for i in request.form.getlist('pregunta_indice')]

def guardar_preguntas(eid, preguntas):
    for orden, p in enumerate(preguntas):
        pid = get_db().execute('INSERT INTO preguntas(evaluacion_id,enunciado,puntaje,orden) VALUES(?,?,?,?)', (eid, p['enunciado'], p['puntaje'], orden)).lastrowid
        for o in p['opciones']:
            get_db().execute('INSERT INTO opciones(pregunta_id,texto,es_correcta) VALUES(?,?,?)', (pid, o['texto'], o['es_correcta']))

@bp.route('/docente/cursos/<int:id>/evaluaciones/nueva', methods=['GET', 'POST'])
@rol_requerido('docente')
def nueva(id):
    curso = propietario(id)
    if request.method == 'POST':
        try:
            datos, preguntas = leer_formulario()
            eid = get_db().execute('INSERT INTO evaluaciones(curso_id,titulo,descripcion,fecha_inicio,fecha_limite,duracion_min) VALUES(?,?,?,?,?,?)', (id, *datos.values())).lastrowid
            guardar_preguntas(eid, preguntas)
            get_db().commit()
            flash('Evaluación creada como borrador.', 'exito')
            return redirect(url_for('materiales.lista', id=id))
        except ValueError as error:
            flash(str(error), 'error')
    return render_template('evaluaciones/formulario.html', curso=curso, evaluacion=None, preguntas=recuperar_preguntas() if request.method == 'POST' else [])

@bp.route('/docente/evaluaciones/<int:eid>/editar', methods=['GET', 'POST'])
@rol_requerido('docente')
def editar(eid):
    ev = obtener(eid)
    curso = propietario(ev['curso_id'])
    # El bloqueo de escritura evita una entrega concurrente mientras se edita.
    get_db().execute('BEGIN IMMEDIATE')
    if get_db().execute('SELECT id FROM entregas WHERE evaluacion_id=?', (eid,)).fetchone():
        get_db().rollback()
        flash('Hay entregas: no se puede editar esta evaluación.', 'advertencia')
        return redirect(url_for('materiales.lista', id=curso['id']))
    if request.method == 'POST':
        try:
            datos, preguntas = leer_formulario()
            get_db().execute("UPDATE evaluaciones SET titulo=?,descripcion=?,fecha_inicio=?,fecha_limite=?,duracion_min=?,estado='borrador' WHERE id=?", (*datos.values(), eid))
            get_db().execute('DELETE FROM preguntas WHERE evaluacion_id=?', (eid,))
            guardar_preguntas(eid, preguntas)
            get_db().commit()
            flash('Cambios guardados en borrador. Publique nuevamente.', 'exito')
            return redirect(url_for('materiales.lista', id=curso['id']))
        except ValueError as error:
            flash(str(error), 'error')
    get_db().rollback()
    return render_template('evaluaciones/formulario.html', curso=curso, evaluacion=ev, preguntas=recuperar_preguntas() if request.method == 'POST' else preguntas_de(eid))

@bp.post('/docente/evaluaciones/<int:eid>/<accion>')
@rol_requerido('docente')
def gestionar(eid, accion):
    ev = obtener(eid)
    propietario(ev['curso_id'])
    if accion not in ('publicar', 'eliminar'): abort(404)
    get_db().execute('BEGIN IMMEDIATE')
    try:
        if get_db().execute('SELECT id FROM entregas WHERE evaluacion_id=?', (eid,)).fetchone():
            raise ValueError('Hay entregas: no se puede modificar ni eliminar esta evaluación.')
        if accion == 'publicar':
            validar(ev, preguntas_de(eid))
            get_db().execute("UPDATE evaluaciones SET estado='publicada' WHERE id=?", (eid,))
        else:
            if request.form.get('confirmar') != 'si': raise ValueError('Confirme la eliminación.')
            get_db().execute('DELETE FROM evaluaciones WHERE id=?', (eid,))
        get_db().commit()
        flash('Evaluación publicada.' if accion == 'publicar' else 'Evaluación eliminada.', 'exito')
    except ValueError as error:
        get_db().rollback()
        flash(str(error), 'error')
    return redirect(url_for('materiales.lista', id=ev['curso_id']))

@bp.route('/evaluaciones/<int:eid>', methods=['GET'])
@bp.route('/evaluaciones/<int:eid>/iniciar', methods=['POST'])
@rol_requerido('estudiante')
def iniciar(eid):
    ev = obtener(eid)
    acceso(ev['curso_id'])
    if ev['estado'] != 'publicada': abort(404)
    if request.method == 'POST': get_db().execute('BEGIN IMMEDIATE')
    previa = get_db().execute('SELECT * FROM entregas WHERE evaluacion_id=? AND estudiante_id=?', (eid, g.usuario['id'])).fetchone()
    if previa:
        get_db().commit()
        return redirect(url_for('calificaciones.resultado' if previa['estado'] == 'enviada' else 'evaluaciones.resolver', id=previa['id']))
    if not fecha(ev['fecha_inicio']) <= ahora() <= fecha(ev['fecha_limite']):
        get_db().rollback()
        flash('La evaluación está fuera de fechas.', 'advertencia')
        return redirect(url_for('materiales.lista', id=ev['curso_id']))
    if request.method == 'POST':
        id = get_db().execute('INSERT INTO entregas(evaluacion_id,estudiante_id,iniciada_en) VALUES(?,?,?)', (eid, g.usuario['id'], ahora().isoformat())).lastrowid
        get_db().commit()
        return redirect(url_for('evaluaciones.resolver', id=id))
    return render_template('evaluaciones/inicio.html', evaluacion=ev)

def entrega_propia(id):
    entrega = get_db().execute('SELECT * FROM entregas WHERE id=? AND estudiante_id=?', (id, g.usuario['id'])).fetchone()
    if entrega is None: abort(404)
    return entrega

def limite(entrega, ev):
    return min(fecha(entrega['iniciada_en']) + timedelta(minutes=ev['duracion_min']), fecha(ev['fecha_limite']))

def cerrar(entrega, ev, respuestas):
    preguntas = preguntas_de(ev['id'])
    for p in preguntas:
        elegida = respuestas.get(p['id'])
        if elegida not in [o['id'] for o in p['opciones']]: elegida = None
        correcta = elegida is not None and elegida == p['correcta']
        get_db().execute('INSERT INTO respuestas(entrega_id,pregunta_id,opcion_id,es_correcta,puntaje_obtenido) VALUES(?,?,?,?,?)', (entrega['id'], p['id'], elegida, int(correcta), p['puntaje'] if correcta else 0))
        respuestas[p['id']] = elegida
    nota = calcular_nota(preguntas, respuestas)
    get_db().execute("UPDATE entregas SET enviada_en=?,nota=?,estado='enviada' WHERE id=?", (ahora().isoformat(), nota, entrega['id']))
    get_db().commit()

@bp.get('/entregas/<int:id>')
@rol_requerido('estudiante')
def resolver(id):
    entrega = entrega_propia(id)
    if entrega['estado'] == 'enviada': return redirect(url_for('calificaciones.resultado', id=id))
    ev = obtener(entrega['evaluacion_id'])
    acceso(ev['curso_id'])
    restantes = max(0, int((limite(entrega, ev) - ahora()).total_seconds()))
    return render_template('evaluaciones/resolver.html', entrega=entrega, evaluacion=ev, preguntas=preguntas_de(ev['id']), restantes=restantes)

@bp.post('/entregas/<int:id>/enviar')
@rol_requerido('estudiante')
def enviar(id):
    get_db().execute('BEGIN IMMEDIATE')
    entrega = entrega_propia(id)
    if entrega['estado'] == 'enviada':
        get_db().commit()
        return redirect(url_for('calificaciones.resultado', id=id))
    ev = obtener(entrega['evaluacion_id'])
    acceso(ev['curso_id'])
    # Se acepta el envío tardío de lo respondido, como indica la guía 5.4.
    respuestas = {}
    for p in preguntas_de(ev['id']):
        valor = request.form.get('respuesta_' + str(p['id']), '')
        respuestas[p['id']] = int(valor) if valor.isdigit() else None
    cerrar(entrega, ev, respuestas)
    return redirect(url_for('calificaciones.resultado', id=id))
