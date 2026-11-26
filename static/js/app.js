// Confirmación explícita antes de eliminar y sincronización de títulos editados.
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', event => {
  if (form.dataset.confirmar && !window.confirm(form.dataset.confirmar)) event.preventDefault();
  form.querySelectorAll('[data-copia]').forEach(input => { input.value = document.getElementById(input.dataset.copia).value; });
}));
window.addEventListener('pageshow', event => { if (event.persisted) window.location.reload(); });

// Accesibilidad del control de visibilidad de contraseña.
document.querySelectorAll('[data-ver-clave]').forEach(boton => boton.addEventListener('click', () => {
  const campo = document.getElementById(boton.dataset.verClave);
  const mostrar = campo.type === 'password';
  campo.type = mostrar ? 'text' : 'password';
  boton.textContent = mostrar ? 'Ocultar' : 'Mostrar';
  boton.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
}));

// Solo el campo del tipo elegido participa en el envío.
document.querySelectorAll('[data-tipo-material]').forEach(selector => {
  const form = selector.closest('form');
  const pdf = form.querySelector('[data-material-pdf]');
  const video = form.querySelector('[data-material-video]');
  function actualizarTipo() {
    const esVideo = selector.value === 'video';
    pdf.hidden = esVideo;
    video.hidden = !esVideo;
    pdf.querySelector('input').disabled = esVideo;
    pdf.querySelector('input').required = !esVideo;
    video.querySelector('input').disabled = !esVideo;
    video.querySelector('input').required = esVideo;
  }
  selector.addEventListener('change', actualizarTipo);
  actualizarTipo();
});
