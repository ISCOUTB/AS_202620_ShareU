// ---------------------------------------------------------------
// Datos de ejemplo (para presentar sin depender del backend).
// Coinciden con la forma de los datos que devuelve /busqueda/documentos.
// ---------------------------------------------------------------
const DOCUMENTOS_EJEMPLO = [
  { titulo: "Taller de Python", universidad: "Universidad Nacional", carrera: "Ingeniería de Sistemas", materia: "Programación", tipo: "Taller", autor: "Ana", calificacion: 4.8 },
  { titulo: "Parcial de Bases de Datos", universidad: "Universidad Nacional", carrera: "Ingeniería de Sistemas", materia: "Bases de Datos", tipo: "Parcial", autor: "Carlos", calificacion: 4.5 },
  { titulo: "Apuntes de Arquitectura de Software", universidad: "Universidad Nacional", carrera: "Ingeniería de Sistemas", materia: "Arquitectura de Software", tipo: "Apuntes", autor: "María", calificacion: 4.7 },
  { titulo: "Ejercicios de Cálculo", universidad: "Universidad del Norte", carrera: "Ingeniería de Sistemas", materia: "Cálculo", tipo: "Ejercicios", autor: "Luis", calificacion: 4.2 },
  { titulo: "Guía de Redes", universidad: "Universidad del Norte", carrera: "Ingeniería de Telecomunicaciones", materia: "Redes", tipo: "Guía", autor: "Sofía", calificacion: 4.6 },
];

const BACKEND_URL = "http://127.0.0.1:8000";

let modoBackend = false;
let documentosActuales = DOCUMENTOS_EJEMPLO;

const form = document.getElementById("form-busqueda");
const input = document.getElementById("input-busqueda");
const filtroCarrera = document.getElementById("filtro-carrera");
const filtroTipo = document.getElementById("filtro-tipo");
const fichasEl = document.getElementById("fichas");
const contadorEl = document.getElementById("contador");
const modoBtn = document.getElementById("modo-btn");
const estadoBackendEl = document.getElementById("estado-backend");
const modulosEls = document.querySelectorAll("#modules li");

function poblarFiltros(documentos) {
  const carreras = [...new Set(documentos.map(d => d.carrera))].sort((a, b) => a.localeCompare(b));
  const tipos = [...new Set(documentos.map(d => d.tipo))].sort((a, b) => a.localeCompare(b));

  filtroCarrera.innerHTML = '<option value="">Todas las carreras</option>' +
    carreras.map(c => `<option value="${c}">${c}</option>`).join("");
  filtroTipo.innerHTML = '<option value="">Todos los tipos</option>' +
    tipos.map(t => `<option value="${t}">${t}</option>`).join("");
}

function renderFichas(documentos) {
  contadorEl.textContent = `${documentos.length} resultado${documentos.length === 1 ? "" : "s"}`;

  if (documentos.length === 0) {
    fichasEl.innerHTML = '<li class="vacio">Nada por aquí. Prueba otra palabra clave.</li>';
    return;
  }

  fichasEl.innerHTML = documentos.map(d => `
    <li class="ficha">
      <span class="tipo">${d.tipo}</span>
      <span class="titulo">${d.titulo}</span>
      <span class="ruta">${d.universidad} · ${d.carrera} · ${d.materia}</span>
      <span class="meta">
        <span class="autor">por ${d.autor}</span>
        <span class="rating">★ ${d.calificacion.toFixed(1)}</span>
      </span>
    </li>
  `).join("");
}

function aplicarFiltros() {
  const q = input.value.trim().toLowerCase();
  const carrera = filtroCarrera.value;
  const tipo = filtroTipo.value;

  const filtrados = documentosActuales.filter(d => {
    const coincideTexto = !q ||
      d.titulo.toLowerCase().includes(q) ||
      d.materia.toLowerCase().includes(q);
    const coincideCarrera = !carrera || d.carrera === carrera;
    const coincideTipo = !tipo || d.tipo === tipo;
    return coincideTexto && coincideCarrera && coincideTipo;
  }).sort((a, b) => b.calificacion - a.calificacion);

  renderFichas(filtrados);
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  aplicarFiltros();
});
input.addEventListener("input", aplicarFiltros);
filtroCarrera.addEventListener("change", aplicarFiltros);
filtroTipo.addEventListener("change", aplicarFiltros);

// ---------------------------------------------------------------
// Modo backend real (opcional): intenta hablar con uvicorn en
// 127.0.0.1:8000. Si no responde, se queda en modo ejemplo.
// ---------------------------------------------------------------
async function marcarModulos(activo) {
  for (const li of modulosEls) {
    const modulo = li.dataset.modulo;
    if (!activo) {
      li.classList.remove("activo", "caido");
      continue;
    }
    try {
      const res = await fetch(`${BACKEND_URL}/${modulo}/ping`);
      li.classList.toggle("activo", res.ok);
      li.classList.toggle("caido", !res.ok);
    } catch {
      li.classList.add("caido");
      li.classList.remove("activo");
    }
  }
}

async function intentarConectarBackend() {
  modoBtn.textContent = "conectando…";
  try {
    const res = await fetch(`${BACKEND_URL}/busqueda/documentos`);
    if (!res.ok) throw new Error("respuesta no ok");
    const data = await res.json();
    documentosActuales = data.resultados.length ? data.resultados : DOCUMENTOS_EJEMPLO;
    modoBackend = true;
    modoBtn.textContent = "modo: backend real";
    estadoBackendEl.textContent = "conectado a uvicorn (127.0.0.1:8000)";
    await marcarModulos(true);
  } catch {
    documentosActuales = DOCUMENTOS_EJEMPLO;
    modoBackend = false;
    modoBtn.textContent = "modo: ejemplo";
    estadoBackendEl.textContent = "datos de ejemplo (backend no disponible)";
    await marcarModulos(false);
  }
  poblarFiltros(documentosActuales);
  aplicarFiltros();
}

modoBtn.addEventListener("click", () => {
  if (modoBackend) {
    documentosActuales = DOCUMENTOS_EJEMPLO;
    modoBackend = false;
    modoBtn.textContent = "modo: ejemplo";
    estadoBackendEl.textContent = "datos de ejemplo (sin backend)";
    marcarModulos(false);
    poblarFiltros(documentosActuales);
    aplicarFiltros();
  } else {
    intentarConectarBackend();
  }
});

// Estado inicial: datos de ejemplo, sin tocar la red.
poblarFiltros(documentosActuales);
aplicarFiltros();
