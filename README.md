# Aula · MVP E-Learning

Aplicación local multipágina con Flask, Jinja y SQLite. Incluye registro de estudiantes, acceso por rol, cursos e inscripciones, materiales PDF/video, evaluaciones de selección única y notas privadas. Las cuatro fases están integradas en este directorio.

## Requisitos e instalación en Windows con VS Code

Instale Python 3.11 o superior (marque **Add Python to PATH**), VS Code y su extensión Python. Abra la carpeta `elearning` en VS Code y use una terminal **Símbolo del sistema / Command Prompt**:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python seed.py
python -m flask --app app run --debug
```

Seleccione `.venv\Scripts\python.exe` con **Python: Select Interpreter**. Abra http://localhost:5000 en Chrome. Para detener, Ctrl+C. En PowerShell puede ejecutar directamente `.venv\Scripts\python.exe` sin activar el entorno; así no necesita cambiar su política de ejecución.

Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/python -m flask --app app run
```

La aplicación crea las tablas con `IF NOT EXISTS`; reiniciarla no borra datos. `seed.py` agrega datos faltantes sin borrar registros ni cambiar fechas de evaluaciones ya existentes. Para una demo posterior, cree una nueva evaluación con fechas vigentes desde la interfaz. Los archivos de borde se generan en `datos_prueba/`.

## Cuentas de demostración

Todas usan `Abcdef1!` como contraseña. Son cuentas ficticias para localhost.

| Nombre | Correo | Rol / estado |
|---|---|---|
| Carlos Ramírez | carlos@demo.local | Docente activo |
| Ana Torres | ana@demo.local | Docente activo, curso propio |
| Sofía Pérez | sofia@demo.local | Estudiante activa |
| Cuenta desactivada | inactiva@demo.local | Estudiante inactiva |

Laura Gómez se registra durante la demo con `laura@example.com` y `Abcdef1!`; no viene precargada. El seed incluye Python desde cero (activo/Básico/Programación), Diseño avanzado (inactivo/Avanzado/Diseño), Inglés conversacional (activo/Intermedio/Idiomas), una evaluación vigente por 30 días desde la primera carga y otra vencida. Las respuestas correctas de las tres preguntas de demo son las primeras opciones: Python, 4 y 1. Puntajes 2,0 + 2,0 + 1,0; duración 30 minutos.

## Ejecución de pruebas

```bat
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pytest tests\test_unitarias.py -q
```

Las pruebas usan bases y uploads temporales; no alteran la demo. La suite cubre UNI-01/02/03, registro, filtros combinados, duplicados, roles y propiedad, PDF exacto de 10 MB, rechazo de 11 MB/tipos/firma/MIME, CRUD, borradores, publicación, intentos, recarga, envío tardío, notas ajenas, CSRF y persistencia. El navegador y el autoenvío JS se verifican con el plan manual, no con pytest.

## Estructura

```text
elearning/
  app.py, config.py, db.py, schema.sql
  auth.py, cursos.py, materiales.py, evaluaciones.py, calificaciones.py
  seed.py, requirements.txt
  servicios/validaciones.py, servicios/calificar.py
  templates/base.html, macros.html
  templates/auth/, cursos/, materiales/, evaluaciones/, errores/
  static/css/app.css
  static/js/app.js, editor.js, temporizador.js
  static/fonts/Inter.ttf, OFL.txt
  uploads/                   PDFs privados con nombres UUID
  tests/                     pruebas aisladas
  docs/                      revisión, plan manual, presentación y fases
  datos_prueba/              generado por seed.py
  elearning.db               generado al arrancar
```

## Decisiones de implementación

- Fechas del formulario en Colombia (UTC−5); almacenamiento ISO en UTC. El servidor fija inicio y límite del intento. Recargar no reinicia su duración. Las selecciones se conservan en sessionStorage para una recarga en la misma pestaña.
- El servidor acepta envíos tardíos y califica sus respuestas, según la guía §5.4. No hay guardado periódico en servidor. Cerrar el navegador no genera un envío mientras la aplicación está cerrada; al reabrir un intento vencido el temporizador envía a cero.
- Para guardar un borrador se exige que las preguntas estén completas y sumen 5,0; publicar vuelve a validar. El editor permite agregar preguntas y opciones, quitar preguntas y cambiar la correcta. Editar una evaluación la devuelve a borrador. Cualquier entrega, incluso en curso, bloquea edición y eliminación.
- Categorías permitidas: Programación, Diseño, Ciencias e Idiomas. Niveles: Básico, Intermedio, Avanzado. El docente gestiona contenido del curso propio; no se añadió edición general de cursos fuera de la creación solicitada.
- PDF: límite real del archivo 10 485 760 bytes, extensión, MIME y firma `%PDF`; límite de la solicitud 12 MiB para admitir el multipart de un PDF de exactamente 10 MiB. 11 MiB se rechazan con mensaje; solicitudes mayores reciben 413.
- Contraseñas con hash; SQL parametrizado; CSRF en formularios; descargas con permisos; sin `|safe`. `SECRET_KEY` se puede configurar por variable de entorno. Sin variable se genera al arrancar: las sesiones dejan de servir tras reiniciar, los datos persisten. Para conservar sesiones en reinicios configure una clave estable antes de ejecutar (`set SECRET_KEY=...` en cmd).
- Inter se sirve localmente con su licencia OFL. Iconos SVG Lucide Book y ListChecks de 24×24, sin dependencia JS ni red. Colores semánticos acompañados por texto.

## Validación manual y entrega

Abra `docs/plan_manual.tsv` en Excel como UTF-8 delimitado por tabulaciones, o copie su contenido. Contiene los 12 casos divididos en pasos con datos, resultado esperado y columnas vacías para resultado real y aprobar/reprobar. `docs/plan_manual.md` permite leer la misma tabla. Los casos se reconstruyen de la guía: no se recibió el Excel original y debe cotejarse con él.

Revise también `docs/revision.md`, `docs/fases.md` y `docs/presentacion.md`. El checklist manual no está marcado como aprobado: debe completarse en Chrome en el equipo de entrega.

Fuera de alcance: certificados, progreso, foros, informes/exportaciones funcionales, administrador, correos/recuperación de contraseña, calificación de cursos, preguntas abiertas, corrección manual, retroalimentación, pagos, alojamiento de videos y despliegue en producción.


## Actualización de mockups

Consulta `docs/actualizacion_mockups.md` para la correspondencia con los diseños y los pasos de actualización en macOS conservando la base, los PDFs y el entorno virtual. Inicio y Evaluaciones son vistas de los datos del MVP; no incluyen funciones excluidas. El inicio de sesión redirige a `/inicio`. Las imágenes decorativas proceden del DERS adjunto y están servidas localmente.


## Consultar la base de datos desde Visual Studio Code

El archivo SQLite es `elearning.db`, en la misma carpeta que `app.py`.
`schema.sql` define las tablas y `db.py` gestiona la conexión.
Abre `ver_base_datos.py` en Visual Studio Code y ejecútalo con Python, o usa la terminal:

```sh
python ver_base_datos.py
python ver_base_datos.py usuarios
python ver_base_datos.py cursos
```

El script imprime la ubicación exacta del archivo, sus tablas y sus registros.
Para consultar más filas, agrega `--pagina 2`. Lee la base en modo de solo lectura.
