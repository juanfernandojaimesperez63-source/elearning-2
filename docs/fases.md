# Entregables por fase

El código completo se entrega en los archivos del proyecto. Las fases están integradas, sin mantener cuatro copias incompatibles de la aplicación.

| Fase | Archivos principales creados | Comandos en cmd de Windows (desde elearning) | Checklist en Chrome |
|---|---|---|---|
| 1 · Base y acceso | config.py, db.py, schema.sql, app.py, auth.py, servicios/validaciones.py, templates/base.html, macros.html, auth/, errores/, static/css/app.css, seed.py, tests/conftest.py, test_unitarias.py | py -m venv .venv; .venv\Scripts\python.exe -m pip install -r requirements.txt; .venv\Scripts\python.exe seed.py; .venv\Scripts\python.exe -m flask --app app run; .venv\Scripts\python.exe -m pytest tests/test_unitarias.py -q (ejecutar cada comando por separado) | Registro válido/inválido/duplicado; login, quinto fallo, cuenta inactiva; menú por rol; logout y Atrás |
| 2 · Cursos | cursos.py, templates/cursos/, seed.py, tests/test_integracion.py | .venv\Scripts\python.exe seed.py; .venv\Scripts\python.exe -m pytest -q; .venv\Scripts\python.exe -m flask --app app run | Crear y repetir título; combinar búsqueda/categoría/nivel; limpiar sin resultados; inscribir dos veces; inactivo por URL; docente ajeno y estudiante en Crear |
| 3 · Contenidos y evaluación | materiales.py, evaluaciones.py, calificaciones.py, servicios/calificar.py, templates/materiales/, evaluaciones/, static/js/, seed.py, tests/ | .venv\Scripts\python.exe seed.py; .venv\Scripts\python.exe -m pytest -q; .venv\Scripts\python.exe -m flask --app app run | CRUD de material; PDFs 5/10/11 MB y EXE; PDF protegido; borrador/publicación; fechas, preguntas y 5,0; recarga, autoenvío, segundo intento y notas ajenas |
| 4 · Entrega | README.md, docs/revision.md, plan_manual.tsv, plan_manual.md, presentacion.md, fases.md; ampliaciones en tests/ | .venv\Scripts\python.exe -m pytest -q; .venv\Scripts\python.exe -m flask --app app run | Ejecutar cada fila de plan_manual.tsv y registrar resultados; reiniciar; ensayar demo de 3–5 minutos |

Todos los comandos de una celda son comandos independientes. El README ofrece bloques listos para copiar en la terminal.
