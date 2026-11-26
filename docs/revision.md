# Revisión final contra el alcance

Se comparó la guía PDF y el texto adjunto con las nueve funcionalidades solicitadas. No había repositorio previo. Los documentos se usaron como especificación; las frases «espera mi primera instrucción» y las solicitudes con marcadores de ejemplo no sustituyeron las cuatro fases autorizadas en el chat.

## Cobertura y faltantes

| Área | Resultado |
|---|---|
| Base y acceso | Nueve tablas, claves foráneas, fábrica, roles, hash, errores, registro, bloqueo puro con hora inyectada, no-store y CSRF |
| Cursos | Catálogo activo, búsqueda y filtros combinados, detalle, inscripción única, cursos propios y creación validada |
| Materiales | Crear, modificar título/reemplazar PDF o editar enlace, eliminar con confirmación; firma, extensión, MIME y borde exacto; descarga privada |
| Evaluaciones | Crear borrador, editor de preguntas/opciones, publicar revalidando, bloqueo con entregas; iniciar inscrito/publicada/en fechas; un intento, temporizador y notas |
| Entrega | Seed, fixtures PDF/EXE, pruebas, README Windows, plan tabulado y guion |

No se identificó una funcionalidad del MVP pendiente de implementar. Falta ejecutar y registrar TODO el plan manual en el equipo de entrega, incluyendo el autoenvío real tras un minuto y la secuencia completa de aceptación en Chrome. La comprobación visual realizada aquí cubrió login y panel docente; pytest no ejecuta JavaScript. No se recibió el Excel original ni el Acta/DERS completos: las tablas de pruebas son una reconstrucción de los casos descritos en la guía y deben cotejarse con el plan del cliente.

## Qué sobra

No se añadieron módulos funcionales fuera de las nueve funciones. CSRF, encabezados de seguridad y almacenamiento local de tipografía son medidas de soporte. El TSV exporta documentación de pruebas, no es una función de informes/exportaciones de la plataforma. No hay administrador, correo, certificados, progreso, pagos ni puntuación de cursos.

## Correcciones concretas realizadas durante la revisión

| Archivo | Cambio exacto | Motivo / evidencia |
|---|---|---|
| app.py y templates/evaluaciones/formulario.html | Agregar filtro fecha_input y usarlo como valor datetime-local al editar | Precargar fechas en Colombia sin pedir que el usuario las vuelva a escribir |
| evaluaciones.py | Agregar recuperar_preguntas y devolver las preguntas ingresadas tras error | Conservar enunciados, opciones y puntajes inválidos para corregirlos |
| static/css/app.css y static/fonts/ | Sustituir @import remoto por @font-face local Inter.ttf; incluir OFL y licencia Lucide | Mantener identidad visual sin red |
| evaluaciones.py, auth.py | BEGIN IMMEDIATE en login, inicio, envío, edición y publicación/eliminación | Serializar modificaciones concurrentes; UNIQUE adicional impide segundo intento |
| tests/test_integracion.py | Validar opciones de otra pregunta, editor GET, fechas inválidas, puntajes no finitos y bloqueo por HTTP | Verificar límites que los casos unitarios aislados no comprueban |

## Auditoría de seguridad

| Archivo / zona | Comprobación | Resultado y corrección |
|---|---|---|
| auth.py, todas las rutas privadas | login_required / rol_requerido | Aplicados; registro y login públicos intencionalmente; / y static son públicos |
| cursos.py, propietario y acceso | Propiedad e inscripción | Dueño del curso o estudiante inscrito; 403 cuando corresponde |
| materiales.py, archivo y guardar | PDF ajeno por URL y modificación ajena | Verifica curso antes de enviar archivo o modificar; UUID fuera de static |
| evaluaciones.py, iniciar y entrega_propia | Borrador, inscripción y entrega ajena | Publicada e inscrito; entrega consultada por ID y estudiante; 404 ajeno |
| calificaciones.py | Notas ajenas | Todas las consultas filtran estudiante autenticado |
| cursos.py, catalogo | SQL dinámico | Solo identificadores fijos del código; valores de usuario con parámetros ? |
| Todos los módulos | SQL sin parametrizar | No se halló interpolación de valores del usuario |
| templates/ | Uso de safe | No se usa; escape Jinja habilitado |
| servicios/validaciones.py y materiales.py | Archivos y URL | Extension, MIME, firma, tamaño, http/https y host; ruta generada |
| app.py | Formularios y caché | Token CSRF de sesión en POST, no-store y nosniff |

No se detectaron hallazgos abiertos en esas categorías después de las correcciones. No es una auditoría de producción.

## Diferencias visuales corregidas

| Referencia | Aplicación final |
|---|---|
| HEX obligatorios | Tokens exactos en :root para fondo, superficies, textos, bordes, deshabilitados y cuatro semánticos |
| Inter y escala | Fuente local; H1 28/600, H2 20/600, H3 16/600, cuerpo 14, pequeño 12, etiquetas 14/500 |
| Lucide 24×24 | SVG lineales Book y ListChecks; licencia incluida |
| Estados de componentes | Hover, focus-visible, active, disabled y campo inválido; macros para campo, botón, tarjeta, badge, alerta |
| Señales además de color | Alertas con prefijo Error/Atención/Éxito/Información; badges con texto de estado; sección activa con aria-current |

## Riesgos y decisiones visibles

1. Las fechas y el esquema ampliado son propuestas de la guía. La aceptación de Flask/SQLite frente al DERS y las firmas del Acta corresponden al equipo/cliente, no se simularon aprobaciones.
2. El requisito acepta calificar envíos tardíos con las respuestas enviadas (§5.4). El sistema no impide que un cliente manipulado prepare respuestas después del tiempo; no es una plataforma de exámenes de alta seguridad. El reloj JS autoenvía en una pestaña abierta. Sin navegador abierto no hay envío en segundo plano ni tarea de servidor; al volver se envía a cero.
3. Las selecciones se conservan solo en sessionStorage en la misma pestaña. No existe guardado periódico en servidor; cambiar de navegador o cerrar la pestaña puede perder respuestas aún no enviadas.
4. El borrador exige preguntas válidas al guardarlo. Publicar las revalida. No se implementó guardado de una evaluación parcialmente incompleta.
5. PDF se valida según la especificación, no con un analizador completo ni antivirus. Se descarga como adjunto con nosniff.
6. Con SECRET_KEY ausente se genera una clave nueva por proceso. Reiniciar invalida sesiones; configurar una clave estable permite conservarlas. La base persiste siempre. Uso previsto: localhost con un proceso Flask.
7. MAX_CONTENT_LENGTH limita la petición a 12 MiB, reservando espacio multipart; el límite de archivo es 10 MiB. Un PDF 11 MiB recibe mensaje de validación, una petición enorme recibe 413.
8. No hay eliminación general de cursos ni usuarios. Los cursos inactivos de seed no aparecen en catálogo ni admiten nuevas inscripciones; una inscripción preexistente puede seguir consultando su contenido.
9. No se han ejecutado pruebas en Windows real ni todos los pasos manuales de aceptación. Los comandos se documentaron para cmd y Python 3.11+; el entorno de verificación fue Linux/Python 3.12.

## Referencias de código (tabla de revisión)

| Archivo | Línea | Problema revisado | Corrección aplicada |
|---|---:|---|---|
| auth.py | 13 | Acceso privado | Decorador central y rol_requerido en módulos. |
| cursos.py | 14 | Curso ajeno | Comparar docente_id con usuario autenticado. |
| cursos.py | 19 | Estudiante no inscrito | Consultar inscripciones antes de entregar contenido. |
| materiales.py | 20 | PDF por URL | Aplicar acceso antes de send_from_directory. |
| evaluaciones.py | 155 | Entrega por ID | Filtrar por id y estudiante_id. |
| calificaciones.py | 9 | Notas ajenas | Filtrar estudiante_id en listado y resultado. |
| cursos.py | 35 | SQL dinámico | Identificadores de lista fija; valores mediante ?. |
| servicios/validaciones.py | 45 | Carga inválida | Extensión, MIME, firma y tamaño inclusive. |
| app.py | 22 | POST falsificado | Comparar token con secrets.compare_digest. |
| templates/macros.html | 1 | HTML de usuario | Escape automático de Jinja; sin safe. |
