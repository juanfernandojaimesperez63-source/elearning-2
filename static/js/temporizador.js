const reloj = document.getElementById('temporizador');
const formulario = document.getElementById('resolucion');
const vence = Date.now() + Number(reloj.dataset.segundos) * 1000;
const clave = `entrega:${location.pathname}`;
// Conserva la selección ante una recarga; la duración procede siempre del servidor.
try {
  const guardadas = JSON.parse(sessionStorage.getItem(clave) || '{}');
  formulario.querySelectorAll('input[type=radio]').forEach(radio => { radio.checked = guardadas[radio.name] === radio.value; });
} catch (_) { /* El formulario funciona sin almacenamiento del navegador. */ }
formulario.addEventListener('change', () => {
  const selecciones = {};
  formulario.querySelectorAll('input[type=radio]:checked').forEach(radio => { selecciones[radio.name] = radio.value; });
  try { sessionStorage.setItem(clave, JSON.stringify(selecciones)); } catch (_) {}
});
let enviado = false;
function enviarAutomatico() {
  if (enviado) return;
  enviado = true;
  formulario.submit();
}
function actualizar() {
  const segundos = Math.max(0, Math.ceil((vence-Date.now())/1000));
  reloj.textContent = `${Math.floor(segundos/60)}:${String(segundos%60).padStart(2,'0')}`;
  if (!segundos) enviarAutomatico();
}
formulario.addEventListener('submit', event => {
  const faltan = [...formulario.querySelectorAll('[data-pregunta]')].some(grupo => !grupo.querySelector('input:checked'));
  if (faltan && !confirm('Hay preguntas sin responder. Valdrán cero. ¿Enviar de todas formas?')) event.preventDefault();
});
actualizar(); setInterval(actualizar, 250);
