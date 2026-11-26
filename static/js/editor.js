const contenedor = document.getElementById('preguntas-editor');
let siguiente = contenedor.children.length;
function actualizarNumeros() {
  contenedor.querySelectorAll('fieldset').forEach((grupo, indice) => {
    grupo.querySelector('legend').textContent = `Pregunta ${indice + 1}`;
  });
}
function agregarOpcion(grupo) {
  const indice = grupo.dataset.pregunta;
  const numero = grupo.querySelectorAll('input[type=radio]').length;
  const etiqueta = document.createElement('label');
  const radio = document.createElement('input');
  radio.type = 'radio'; radio.name = `correcta_${indice}`; radio.value = numero; radio.required = true;
  const texto = document.createElement('input');
  texto.name = `opcion_${indice}`; texto.required = true; texto.setAttribute('aria-label', `Texto de opción ${numero+1}`);
  etiqueta.append(radio, document.createTextNode('Correcta '), texto);
  grupo.insertBefore(etiqueta, grupo.querySelector('button'));
}
document.getElementById('agregar-pregunta').addEventListener('click', () => {
  const indice = siguiente++;
  const grupo = document.createElement('fieldset'); grupo.dataset.pregunta = indice;
  grupo.innerHTML = `<legend>Pregunta ${indice+1}</legend><input type="hidden" name="pregunta_indice" value="${indice}"><label>Enunciado<input name="enunciado_${indice}" required></label><label>Puntaje<input name="puntaje_${indice}" required inputmode="decimal"></label><button type="button" data-agregar-opcion>Agregar opción</button><button type="button" data-quitar-pregunta>Quitar pregunta</button>`;
  contenedor.append(grupo); agregarOpcion(grupo); agregarOpcion(grupo); actualizarNumeros();
});
contenedor.addEventListener('click', event => {
  if (event.target.matches('[data-agregar-opcion]')) agregarOpcion(event.target.closest('fieldset'));
  if (event.target.matches('[data-quitar-pregunta]')) {
    event.target.closest('fieldset').remove();
    actualizarNumeros();
  }
});
if (!contenedor.children.length) document.getElementById('agregar-pregunta').click();
