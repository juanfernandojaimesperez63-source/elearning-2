from functools import wraps
import sqlite3
from datetime import datetime, timezone
from flask import Blueprint, request, session, g, redirect, url_for, render_template, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from servicios.validaciones import clave_valida, correo_valido, estado_login
bp = Blueprint('auth', __name__)

def ahora():
    return datetime.now(timezone.utc)

def login_required(vista):
    @wraps(vista)
    def protegida(*args, **kwargs):
        if g.usuario is None:
            return redirect(url_for('auth.login'))
        return vista(*args, **kwargs)
    return protegida

def rol_requerido(rol):
    def decorar(vista):
        @wraps(vista)
        @login_required
        def protegida(*args, **kwargs):
            if g.usuario['rol'] != rol:
                abort(403)
            return vista(*args, **kwargs)
        return protegida
    return decorar

@bp.before_app_request
def cargar_usuario():
    g.usuario = get_db().execute('SELECT * FROM usuarios WHERE id=? AND activo=1', (session.get('uid'),)).fetchone()

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    errores = {}
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        clave = request.form.get('clave', '')
        if not nombre: errores['nombre'] = 'El nombre es obligatorio.'
        if not correo_valido(correo): errores['correo'] = 'Ingrese un correo válido.'
        if not clave_valida(clave): errores['clave'] = 'Mínimo 8 caracteres, una mayúscula, un número y un símbolo.'
        if clave != request.form.get('confirmacion'): errores['confirmacion'] = 'Las contraseñas no coinciden.'
        if not errores:
            try:
                get_db().execute('INSERT INTO usuarios(nombre,correo,password_hash,rol) VALUES(?,?,?,?)', (nombre, correo, generate_password_hash(clave), 'estudiante'))
                get_db().commit()
                flash('Registro exitoso. Inicie sesión.', 'exito')
                return redirect(url_for('auth.login'))
            except sqlite3.IntegrityError:
                errores['correo'] = 'El correo ya está registrado.'
    return render_template('auth/registro.html', errores=errores), 400 if errores else 200

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conexion = get_db()
        conexion.execute('BEGIN IMMEDIATE')
        usuario = conexion.execute('SELECT * FROM usuarios WHERE correo=?', (request.form.get('correo', '').strip().lower(),)).fetchone()
        mensaje = 'Credenciales incorrectas.'
        if usuario:
            ok, intentos, hasta, mensaje = estado_login(usuario['activo'], usuario['intentos_fallidos'], usuario['bloqueado_hasta'], check_password_hash(usuario['password_hash'], request.form.get('clave', '')), ahora())
            conexion.execute('UPDATE usuarios SET intentos_fallidos=?, bloqueado_hasta=? WHERE id=?', (intentos, hasta, usuario['id']))
            conexion.commit()
            if ok:
                session.clear()
                session['uid'] = usuario['id']
                return redirect(url_for('panel.inicio'))
        else:
            conexion.commit()
        flash(mensaje, 'error')
    return render_template('auth/login.html')

@bp.post('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

