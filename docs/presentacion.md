# Guion de presentación · aproximadamente 4 minutos

Preparación: ejecutar seed y servidor; abrir dos ventanas de Chrome (normal e incógnito), disponer de `datos_prueba/ejemplo_5MB.pdf`. Si Laura ya existe, usar un correo nuevo. Preparar preguntas y seleccionar fechas de hoy que incluyan la demo. No gastar la presentación escribiendo párrafos largos.

| Tiempo | Acción visible | Guion |
|---|---|---|
| 0:00–0:25 | Inicio de sesión de Carlos | «Esta plataforma local conecta a docentes y estudiantes mediante nueve funciones acordadas. Usa Python, Flask y SQLite, con dos roles y permisos comprobados en el servidor.» |
| 0:25–0:55 | Crear curso «Demo WEB», descripción «Fundamentos prácticos», Programación, Básico | «El docente crea su curso. El título es único para ese docente y los campos son obligatorios. Solo él podrá gestionar sus materiales y evaluaciones.» |
| 0:55–1:20 | Gestionar curso, agregar PDF de 5 MB | «Agregamos un PDF. Se comprueba extensión, tipo, firma y tamaño de hasta 10 MB inclusive. El archivo se conserva fuera de la carpeta pública. Los videos se añaden como enlaces.» |
| 1:20–2:00 | Crear evaluación «Conceptos WEB», inicio anterior a ahora y límite posterior, 30 minutos; tres preguntas con dos opciones cada una y puntajes 2, 2, 1; guardar y publicar | «Primero guardamos en borrador. Al publicar se verifican las fechas, la duración, una única opción correcta por pregunta y la suma exacta de cinco puntos. Si hay entregas, ya no se puede editar ni eliminar.» |
| 2:00–2:25 | En incógnito registrar Laura y entrar | «El registro público crea solamente estudiantes. La contraseña requiere ocho caracteres, una mayúscula, un número y un símbolo. Cinco fallos bloquean la cuenta por quince minutos.» |
| 2:25–2:55 | Buscar Demo WEB, combinar categoría y nivel, inscribirse, descargar PDF | «Laura encuentra cursos activos, se inscribe una sola vez y obtiene acceso al material. Abrir directamente el PDF sin inscripción devuelve acceso denegado.» |
| 2:55–3:35 | Abrir evaluación, iniciar, seleccionar respuestas, recargar brevemente, enviar | «El intento es único. El servidor guarda su hora de inicio, de modo que recargar no reinicia el reloj. A cero se envía automáticamente. Una pregunta sin responder vale cero y se pide confirmación antes del envío manual.» |
| 3:35–4:00 | Resultado y Mis calificaciones, cerrar sesión | «La nota se calcula en centésimas y se presenta de cero a cinco con coma decimal. Cada estudiante consulta solo sus notas. Quedaron fuera certificados, progreso, foros, correos, administrador, pagos e informes. La entrega es para demostración local.» |

Ensayar antes de presentar. La parte del autoenvío se explica; su prueba con una evaluación de un minuto se ejecuta aparte con SIS-02. No afirmar que se realizó una prueba manual si no quedó registrada.
