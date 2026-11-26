import sqlite3
from pathlib import Path
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DB_PATH'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

def init_db():
    get_db().executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
    # Las bases existentes reciben la columna de portada al arrancar.
    conexion = get_db()
    conexion.execute('BEGIN IMMEDIATE')
    columnas = {fila['name'] for fila in conexion.execute('PRAGMA table_info(cursos)')}
    if 'imagen_portada' not in columnas:
        conexion.execute('ALTER TABLE cursos ADD COLUMN imagen_portada TEXT')
    conexion.commit()

def cerrar_db(error=None):
    conexion = g.pop('db', None)
    if conexion is not None:
        conexion.close()
