
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
const filtroUniversidad = document.getElementById("filtro-universidad");
const filtroCarrera = document.getElementById("filtro-carrera");
const filtroMateria = document.getElementById("filtro-materia");
const filtroTipo = document.getElementById("filtro-tipo");
const fichasEl = document.getElementById("fichas");
const contadorEl = document.getElementById("contador");
const modoBtn = document.getElementById("modo-btn");
const estadoBackendEl = document.getElementById("estado-backend");
const modulosEls = document.querySelectorAll("#modules li");

function poblarFiltros(documentos) {
  const universidades = [...new Set(documentos.map(d => d.universidad))].sort();
  const carreras = [...new Set(documentos.map(d => d.carrera))].sort();
  const materias = [...new Set(documentos.map(d => d.materia))].sort();
  const tipos = [...new Set(documentos.map(d => d.tipo))].sort();

  filtroUniversidad.innerHTML = '<option value="">Todas las universidades</option>' +
    universidades.map(v => `<option value="${v}">${v}</option>`).join("");
  filtroCarrera.innerHTML = '<option value="">Todas las carreras</option>' +
    carreras.map(v => `<option value="${v}">${v}</option>`).join("");
  filtroMateria.innerHTML = '<option value="">Todas las materias</option>' +
    materias.map(v => `<option value="${v}">${v}</option>`).join("");
  filtroTipo.innerHTML = '<option value="">Todos los tipos</option>' +
    tipos.map(v => `<option value="${v}">${v}</option>`).join("");
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

async function aplicarFiltros() {
  const q = input.value.trim();
  const universidad = filtroUniversidad.value;
  const carrera = filtroCarrera.value;
  const materia = filtroMateria.value;
  const tipo = filtroTipo.value;

  if (modoBackend) {
    const params = new URLSearchParams();
    if (universidad) params.set("universidad", universidad);
    if (carrera) params.set("carrera", carrera);
    if (materia) params.set("materia", materia);
    if (tipo) params.set("tipo", tipo);
    if (q) params.set("palabra_clave", q);

    try {
      const res = await fetch(`${BACKEND_URL}/busqueda/documentos?${params.toString()}`);
      if (!res.ok) throw new Error("respuesta no ok");
      const data = await res.json();
      renderFichas(data.resultados);
      return;
    } catch {
      estadoBackendEl.textContent = "backend no disponible durante la búsqueda";
      return;
    }
  }

  const qLower = q.toLowerCase();
  const filtrados = documentosActuales.filter(d => {
    const coincideTexto = !qLower ||
      d.titulo.toLowerCase().includes(qLower) ||
      d.materia.toLowerCase().includes(qLower) ||
      d.palabras_clave?.toLowerCase().includes(qLower);
    const coincideUniversidad = !universidad || d.universidad === universidad;
    const coincideCarrera = !carrera || d.carrera === carrera;
    const coincideMateria = !materia || d.materia === materia;
    const coincideTipo = !tipo || d.tipo === tipo;
    return coincideTexto && coincideUniversidad && coincideCarrera && coincideMateria && coincideTipo;
  }).sort((a, b) => b.calificacion - a.calificacion);

  renderFichas(filtrados);
}


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


poblarFiltros(documentosActuales);
aplicarFiltros();
