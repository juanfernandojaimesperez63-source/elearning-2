from pathlib import Path
from uuid import uuid4
from flask import Blueprint, request, g, current_app, render_template, redirect, url_for, flash, abort, send_from_directory
from werkzeug.utils import secure_filename
from auth import login_required, rol_requerido
from cursos import acceso, propietario
from db import get_db
from servicios.validaciones import video_valido, pdf_valido
bp = Blueprint('materiales', __name__)

@bp.get('/cursos/<int:id>/materiales')
@login_required
def lista(id):
    curso = acceso(id)
    evaluaciones = get_db().execute('SELECT * FROM evaluaciones WHERE curso_id=?' + (" AND estado='publicada'" if g.usuario['rol'] == 'estudiante' else ''), (id,)).fetchall()
    return render_template('materiales/lista.html', curso=curso, materiales=get_db().execute('SELECT * FROM materiales WHERE curso_id=?', (id,)).fetchall(), evaluaciones=evaluaciones)

@bp.get('/materiales/<int:mid>/archivo')
@login_required
def archivo(mid):
    material = get_db().execute("SELECT * FROM materiales WHERE id=? AND tipo='pdf'", (mid,)).fetchone()
    if material is None: abort(404)
    acceso(material['curso_id'])
    return send_from_directory(current_app.config['UPLOAD_DIR'], material['archivo_ruta'], as_attachment=True, download_name=secure_filename(material['titulo']) + '.pdf', mimetype='application/pdf')

@bp.post('/docente/cursos/<int:id>/materiales')
@rol_requerido('docente')
def guardar(id):
    propietario(id)
    accion = request.form.get('accion', 'nuevo')
    material = None
    if accion in ('editar', 'eliminar'):
        material = get_db().execute('SELECT * FROM materiales WHERE id=? AND curso_id=?', (request.form.get('mid'), id)).fetchone()
        if material is None: abort(404)
    elif accion != 'nuevo': abort(400)
    if accion == 'eliminar':
        if request.form.get('confirmar') != 'si':
            flash('Confirme la eliminación.', 'advertencia')
        else:
            get_db().execute('DELETE FROM materiales WHERE id=?', (material['id'],))
            get_db().commit()
            if material['archivo_ruta']: Path(current_app.config['UPLOAD_DIR'], material['archivo_ruta']).unlink(missing_ok=True)
            flash('Material eliminado.', 'exito')
        return redirect(url_for('materiales.lista', id=id))
    titulo = request.form.get('titulo', '').strip()
    tipo = request.form.get('tipo', '')
    ruta, tamano, url = None, None, None
    nuevo_archivo = False
    try:
        if not titulo: raise ValueError('El título es obligatorio.')
        if tipo == 'video':
            url = request.form.get('url', '').strip()
            if not video_valido(url): raise ValueError('El enlace debe ser una URL http o https válida.')
        elif tipo == 'pdf':
            subido = request.files.get('archivo')
            if subido and subido.filename:
                contenido = subido.stream.read(10485761)
                if not pdf_valido(subido.filename, subido.mimetype, contenido):
                    raise ValueError('Use un PDF válido (firma %PDF y tipo application/pdf), de máximo 10 MB inclusive.')
                ruta = secure_filename(uuid4().hex + '.pdf')
                tamano = len(contenido)
                Path(current_app.config['UPLOAD_DIR'], ruta).write_bytes(contenido)
                nuevo_archivo = True
            elif material and material['tipo'] == 'pdf':
                ruta, tamano = material['archivo_ruta'], material['tamano_bytes']
            else: raise ValueError('Seleccione un archivo PDF.')
        else: raise ValueError('Tipo de material inválido.')
        if material:
            get_db().execute('UPDATE materiales SET titulo=?,tipo=?,archivo_ruta=?,tamano_bytes=?,url=? WHERE id=?', (titulo, tipo, ruta, tamano, url, material['id']))
        else:
            get_db().execute('INSERT INTO materiales(curso_id,titulo,tipo,archivo_ruta,tamano_bytes,url) VALUES(?,?,?,?,?,?)', (id, titulo, tipo, ruta, tamano, url))
        get_db().commit()
        if material and material['archivo_ruta'] and material['archivo_ruta'] != ruta:
            Path(current_app.config['UPLOAD_DIR'], material['archivo_ruta']).unlink(missing_ok=True)
        flash('Material guardado.', 'exito')
    except ValueError as error:
        flash(str(error), 'error')
    except Exception:
        get_db().rollback()
        if nuevo_archivo: Path(current_app.config['UPLOAD_DIR'], ruta).unlink(missing_ok=True)
        raise
    return redirect(url_for('materiales.lista', id=id))
