import secrets
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, session, request, abort
from config import Config
from db import init_db, cerrar_db

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config: app.config.update(config)
    Path(app.config['UPLOAD_DIR']).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(cerrar_db)
    from auth import bp as auth
    from cursos import bp as cursos, portada_curso
    from navegacion import destino_volver
    from materiales import bp as materiales
    from evaluaciones import bp as evaluaciones, fecha, ZONA_LOCAL
    from calificaciones import bp as calificaciones
    from panel import bp as panel
    for bp in (auth, cursos, materiales, evaluaciones, calificaciones, panel): app.register_blueprint(bp)
    with app.app_context(): init_db()

    @app.before_request
    def csrf():
        if request.method == 'POST' and not secrets.compare_digest(session.get('csrf', ''), request.form.get('csrf', '')):
            abort(403)
        if request.method == 'POST' and not session.get('csrf'): abort(403)

    @app.context_processor
    def contexto():
        if 'csrf' not in session: session['csrf'] = secrets.token_hex(24)
        return {'csrf': session['csrf'], 'portada_curso': portada_curso, 'volver': destino_volver()}

    @app.after_request
    def cabeceras(respuesta):
        if request.endpoint != 'static': respuesta.headers['Cache-Control'] = 'no-store'
        respuesta.headers['X-Content-Type-Options'] = 'nosniff'
        respuesta.headers['X-Frame-Options'] = 'DENY'
        return respuesta

    @app.get('/')
    def inicio(): return redirect(url_for('auth.login'))

    def error(codigo):
        def mostrar(error): return render_template(f'errores/{codigo}.html'), codigo
        return mostrar
    for codigo in (403, 404, 413): app.register_error_handler(codigo, error(codigo))
    app.jinja_env.filters['nota'] = lambda n: f'{n / 100:.1f}'.replace('.', ',')
    app.jinja_env.filters['fecha_input'] = lambda f: fecha(f).astimezone(ZONA_LOCAL).strftime('%Y-%m-%dT%H:%M')
    app.jinja_env.filters['fecha_local'] = lambda f: fecha(f).astimezone(ZONA_LOCAL).strftime('%d/%m/%Y %H:%M')
    return app
