"""Carga reproducible sin borrar usuarios, inscripciones ni resultados existentes."""
from datetime import timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import create_app
from auth import ahora
from db import get_db
from evaluaciones import guardar_preguntas
CLAVE = 'Abcdef1!'

def cargar():
    db = get_db()
    for nombre, correo, rol, activo in [('Carlos Ramírez','carlos@demo.local','docente',1),('Ana Torres','ana@demo.local','docente',1),('Sofía Pérez','sofia@demo.local','estudiante',1),('Cuenta desactivada','inactiva@demo.local','estudiante',0)]:
        db.execute('INSERT OR IGNORE INTO usuarios(nombre,correo,password_hash,rol,activo) VALUES(?,?,?,?,?)', (nombre, correo, generate_password_hash(CLAVE), rol, activo))
    carlos = db.execute('SELECT id FROM usuarios WHERE correo=?', ('carlos@demo.local',)).fetchone()['id']
    ana = db.execute('SELECT id FROM usuarios WHERE correo=?', ('ana@demo.local',)).fetchone()['id']
    for docente, titulo, categoria, nivel, estado in [(carlos,'Python desde cero','Programación','Básico','activo'),(carlos,'Diseño avanzado','Diseño','Avanzado','inactivo'),(ana,'Inglés conversacional','Idiomas','Intermedio','activo')]:
        db.execute('INSERT OR IGNORE INTO cursos(docente_id,titulo,descripcion,categoria,nivel,estado) VALUES(?,?,?,?,?,?)', (docente,titulo,'Curso práctico de demostración.',categoria,nivel,estado))
    curso = db.execute('SELECT id FROM cursos WHERE docente_id=? AND titulo=?', (carlos,'Python desde cero')).fetchone()['id']
    for titulo, inicio, fin in [('Evaluación de Python', ahora()-timedelta(days=1), ahora()+timedelta(days=30)),('Evaluación vencida', ahora()-timedelta(days=3), ahora()-timedelta(days=2))]:
        if not db.execute('SELECT id FROM evaluaciones WHERE curso_id=? AND titulo=?', (curso,titulo)).fetchone():
            eid = db.execute("INSERT INTO evaluaciones(curso_id,titulo,fecha_inicio,fecha_limite,duracion_min,estado) VALUES(?,?,?,?,30,'publicada')", (curso,titulo,inicio.isoformat(),fin.isoformat())).lastrowid
            guardar_preguntas(eid, [{'enunciado': texto,'puntaje': puntaje,'opciones':[{'texto': correcta,'es_correcta':1},{'texto': incorrecta,'es_correcta':0}]} for texto,puntaje,correcta,incorrecta in [('¿Cuál es un lenguaje de programación?',200,'Python','HTML'),('¿Cuánto es 2 + 2?',200,'4','5'),('¿Qué imprime print(1)?',100,'1','2')]])
    db.commit()

def archivos_demo():
    carpeta = Path(__file__).parent / 'datos_prueba'
    carpeta.mkdir(exist_ok=True)
    # PDF mínimo con tabla xref válida, rellenado con comentarios hasta el tamaño exacto.
    cabecera = b'%PDF-1.4\n'
    objetos = [b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n', b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n', b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n']
    contenido = cabecera
    posiciones = []
    for objeto in objetos:
        posiciones.append(len(contenido)); contenido += objeto
    inicio_xref = len(contenido)
    contenido += b'xref\n0 4\n0000000000 65535 f \n' + b''.join(f'{p:010} 00000 n \n'.encode() for p in posiciones)
    final = f'trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n'.encode()
    for mb in (5,10,11):
        relleno = mb*1024*1024-len(contenido)-len(final)
        (carpeta/f'ejemplo_{mb}MB.pdf').write_bytes(contenido+b'%' + b' '*(relleno-2)+b'\n'+final)
    (carpeta/'rechazar.exe').write_bytes(b'MZ-demo-no-ejecutable')

if __name__ == '__main__':
    app = create_app()
    with app.app_context(): cargar()
    archivos_demo()
    print('Datos listos. Contraseña de demostración: ' + CLAVE)
