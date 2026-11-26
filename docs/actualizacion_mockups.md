# Actualización visual basada en los mockups

## Referencias y alcance

Se leyeron el DERS DOCX y las ocho copias idénticas de la guía de estilos adjunta. El DOCX contiene los mockups originales en color, con acentos violeta, aunque las capturas del chat se ven en escala de grises. Los HEX obligatorios para fondos, texto, bordes, deshabilitados y estados se conservan. El violeta se usa como acento y acción primaria de la referencia.

La entrega aproxima la composición de los mockups con interfaz HTML real; no es una reproducción píxel a píxel. La cantidad de datos, las funciones excluidas y la ausencia de los archivos originales de Figma y fotografías por separado hacen que algunas secciones difieran.

## Archivos

- `templates/base.html`: sidebar, perfil por inicial, encabezado con búsqueda funcional para estudiantes, navegación y sección activa.
- `templates/macros.html`: iconos, tarjetas con portada/docente/nivel, indicadores, hero y badges semánticos.
- `templates/auth/login.html` y `registro.html`: fotografía lateral, formulario HTML, contraseña visible/oculta y navegación entre acceso y registro.
- `templates/panel.html` y `panel.py`: Inicio por rol con cursos, evaluaciones y notas reales del usuario.
- `templates/evaluaciones/lista.html`: navegación a evaluaciones existentes; oculta borradores a estudiantes y cursos ajenos a docentes.
- `templates/cursos/`: catálogo, categorías combinables con los filtros existentes y detalle.
- `templates/materiales/lista.html`: contenido central y columna lateral de curso; conserva CRUD y permisos.
- `templates/evaluaciones/formulario.html`: información general, preguntas, configuración y barra inferior de acciones.
- `templates/evaluaciones/notas.html`: tabla privada y resumen de los resultados mostrados.
- `static/css/componentes.css`: componentes base y tokens de la guía original.
- `static/css/app.css`: composición de los mockups, acento violeta y adaptación responsive.
- `static/img/`: imágenes del documento proporcionado, usadas como fondos delimitados para la fotografía y elementos decorativos, sin enlaces externos. Algunas portadas tienen resolución limitada por el archivo original. La imagen de Inicio queda disponible como referencia, sin uso funcional.
- `static/js/app.js`: se conserva confirmación de eliminación y se añade visibilidad de contraseña.
- `auth.py` y `app.py`: acceso redirige a Inicio y registra el blueprint del panel.
- `cursos.py`: incorpora el nombre real del docente en tarjetas.
- `tests/test_panel.py`: acceso por sesión, contenido propio, ocultación de borradores y recursos locales.

## Diferencias intencionales

No se incorporaron Google/institución, recuperar contraseña, administrador, foros, certificados, informes, progreso del curso, horas de aprendizaje, calificación del curso, corrección manual ni comentarios de docente. No hay notificaciones o paginación ficticias. Los avatares usan iniciales porque no existe perfil con foto. Las estadísticas del panel se calculan con datos reales; un estudiante nuevo ve cero cursos y notas sin promedio, en vez de los números ilustrativos del mockup. Se ocultó el contador promocional de 12.000 usuarios de la imagen de acceso porque no corresponde a datos reales.

La nota máxima se mantiene en 5,0, un intento y preguntas de selección única. Guardar sigue creando borrador y la publicación se hace desde la gestión del curso. El docente no recibe una pantalla de calificación manual porque la corrección es automática según el alcance.

Para fidelidad exacta en imágenes, tamaños y espaciados se requieren los frames originales de Figma y los recursos gráficos separados. En esta entrega las referencias del Word sirven para la composición y los recortes decorativos se delimitan mediante CSS.

## Verificación realizada

53 pruebas pytest aprobadas (49 existentes y 4 adicionales). Comprobados visualmente en Chrome del entorno: login, Inicio de Sofía, catálogo y detalle del curso. La revisión visual no incluyó inscripción ni presentación de un intento. Los permisos, evaluaciones y CRUD están verificados por la suite automatizada. No se afirma verificación píxel a píxel ni ejecución del plan manual completo en macOS.

## Actualizar en el Mac sin perder datos

1. Detener Flask con Ctrl+C en la terminal de VS Code.
2. Hacer una copia de seguridad de la carpeta `elearning` del Mac.
3. Extraer `elearning_mockups.zip`. Copiar su contenido de `elearning` sobre la carpeta del proyecto existente, reemplazando los archivos de código. El ZIP no incluye `elearning.db`, `uploads` con PDFs ni entornos virtuales, así que no sustituye los datos existentes.
4. Mantener la base `elearning.db`, la carpeta `uploads` y el entorno `.venv-1` del Mac. No borrar esos archivos.
5. Desde VS Code, con la carpeta del proyecto abierta y su entorno activo, ejecutar:

```bash
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

6. Escribir `http://127.0.0.1:5000` directamente en la barra del navegador. Recargar con Cmd+Shift+R para actualizar el CSS.
7. Ingresar con una cuenta existente. No hace falta ejecutar seed para conservar los datos y las contraseñas existentes.

Esta actualización está hecha en el entorno compartido; no modifica automáticamente la copia en Downloads del Mac.
