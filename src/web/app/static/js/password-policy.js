/**
 * Validación de contraseña segura, en JS -- espejo EXACTO de
 * backend/app/core/password_policy.py (misma lista negra, mismas 4
 * reglas, mismos mensajes). El backend sigue siendo la autoridad final
 * (nunca confíes solo en JS), esto es solo para dar retroalimentación
 * inmediata sin esperar un viaje al servidor.
 *
 * Si algún día cambia la política en el backend, hay que actualizar
 * este archivo también a mano -- no hay generación automática entre
 * los dos lados.
 */
const CONTRASENAS_COMUNES = new Set([
  '12345678', '123456789', '1234567890', 'password', 'password1',
  'contraseña', 'contrasena', 'contrasena1', 'qwerty123', 'qwertyuiop',
  '11111111', '00000000', 'administrador', 'admin1234', 'admin12345',
  'letmein123', 'welcome123', 'iloveyou1', 'abc123456', '123123123',
  '1q2w3e4r5t', 'passw0rd1', 'trustno1', 'football1', 'monkey123',
  'dragon123', 'master123', 'shadow123', 'superman1', 'batman123',
  'princess1', 'sunshine1', 'aaaaaaaa', 'zxcvbnm12', 'changeme1',
  'temporal1', 'bienvenido1', 'usuario123', 'cambiar123',
  'recolector1', 'administrador1', 'guest1234', 'test12345',
  'demo12345', 'root12345', '12345678a', 'a12345678', 'qazwsxedc',
]);

const REQUISITOS_PASSWORD = [
  { clave: 'longitud', texto: 'Al menos 8 caracteres', prueba: (v) => v.length >= 8 },
  { clave: 'comun', texto: 'No es una contraseña común', prueba: (v) => v.length > 0 && !CONTRASENAS_COMUNES.has(v.toLowerCase()) },
  { clave: 'mayuscula', texto: 'Al menos una mayúscula', prueba: (v) => /[A-Z]/.test(v) },
  { clave: 'numero', texto: 'Al menos un número', prueba: (v) => /[0-9]/.test(v) },
  { clave: 'simbolo', texto: 'Al menos un símbolo (ej. !@#$%&*)', prueba: (v) => /[^A-Za-z0-9]/.test(v) },
];

/**
 * Devuelve el primer mensaje de error (mismo texto que el backend), o
 * null si la contraseña cumple todo.
 */
function validarPasswordFuerte(valor) {
  if (valor.length < 8) return 'La contraseña debe tener al menos 8 caracteres.';
  if (CONTRASENAS_COMUNES.has(valor.toLowerCase())) return 'Esa contraseña es demasiado común/insegura. Elige una distinta.';
  if (!/[A-Z]/.test(valor)) return 'La contraseña debe incluir al menos una letra mayúscula.';
  if (!/[0-9]/.test(valor)) return 'La contraseña debe incluir al menos un número.';
  if (!/[^A-Za-z0-9]/.test(valor)) return 'La contraseña debe incluir al menos un símbolo (ej. !@#$%&*).';
  return null;
}

/**
 * Dibuja la lista de requisitos dentro de contenedorId, y la conecta al
 * input de contraseña (passId) para que se marquen en vivo mientras se
 * escribe. Si opcional=true (caso "Editar usuario": dejar en blanco =
 * no cambiar), un campo vacío no se marca como error de nada.
 */
function montarChecklistPassword(passId, contenedorId, opcional) {
  const passInput = document.getElementById(passId);
  const contenedor = document.getElementById(contenedorId);
  if (!passInput || !contenedor) return;

  contenedor.innerHTML = REQUISITOS_PASSWORD.map((r) => `
    <div class="password-requisito" data-clave="${r.clave}">
      <i class="bi bi-circle"></i> <span>${r.texto}</span>
    </div>
  `).join('');

  function actualizar() {
    const valor = passInput.value;
    const vacioYOpcional = opcional && valor.length === 0;

    REQUISITOS_PASSWORD.forEach((r) => {
      const fila = contenedor.querySelector(`[data-clave="${r.clave}"]`);
      const icono = fila.querySelector('i');
      const cumplido = !vacioYOpcional && r.prueba(valor);
      fila.classList.toggle('password-requisito--ok', cumplido);
      icono.className = cumplido ? 'bi bi-check-circle-fill' : 'bi bi-circle';
    });

    passInput.setCustomValidity(vacioYOpcional ? '' : (validarPasswordFuerte(valor) || ''));
  }

  passInput.addEventListener('input', actualizar);
  actualizar();
}
