const form = document.getElementById('simulation-form');
const markdownOutput = document.getElementById('markdown-output');
const jsonOutput = document.getElementById('json-output');
const downloadMd = document.getElementById('download-md');
const downloadJson = document.getElementById('download-json');
const loadingSpinner = document.getElementById('loading');
const loadingText = document.getElementById('loading-text');
const submitBtn = document.getElementById('submit-btn');
const alertsContainer = document.getElementById('alerts');

let latestMarkdown = '';
let latestJson = null;

function showLoading(isLoading) {
  if (isLoading) {
    loadingSpinner.classList.remove('d-none');
    loadingText.classList.remove('visually-hidden');
    submitBtn.disabled = true;
  } else {
    loadingSpinner.classList.add('d-none');
    loadingText.classList.add('visually-hidden');
    submitBtn.disabled = false;
  }
}

function clearAlerts() {
  alertsContainer.innerHTML = '';
}

function showError(message) {
  clearAlerts();
  if (!message) return;
  const alert = document.createElement('div');
  alert.className = 'alert alert-danger';
  alert.setAttribute('role', 'alert');
  alert.textContent = message;
  alertsContainer.appendChild(alert);
}

function validateContext(value) {
  const normalized = value.trim();
  if (normalized.length < 10) {
    return 'El contexto debe contener al menos 10 caracteres relevantes.';
  }

  const lines = normalized
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  if (lines.length > 10) {
    return 'El contexto no debe exceder 10 líneas.';
  }

  if (lines.length >= 3) {
    return null;
  }

  const sentences = normalized
    .split(/[.!?]+/)
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 0);

  if (sentences.length < 3) {
    return 'El contexto debe contener al menos 3 oraciones o líneas informativas.';
  }

  return null;
}

function resetResults() {
  latestMarkdown = '';
  latestJson = null;
  markdownOutput.textContent = 'Aún no hay resultados.';
  jsonOutput.textContent = 'Aún no hay resultados.';
  downloadMd.disabled = true;
  downloadJson.disabled = true;
  clearAlerts();
}

function buildPayload(formData) {
  const restriccionesRaw = formData.get('restricciones') || '';
  const restricciones = restriccionesRaw
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  return {
    contexto: formData.get('contexto') || '',
    materia: formData.get('materia') || 'penal',
    nivel: formData.get('nivel') || 'intermedio',
    jurisdiccion: formData.get('jurisdiccion') || undefined,
    objetivo_didactico: formData.get('objetivo_didactico') || 'practicar objeciones y contrainterrogatorio',
    duracion_min: Number(formData.get('duracion_min')) || 90,
    restricciones: restricciones.length ? restricciones : undefined,
  };
}

function renderWarnings(warnings) {
  clearAlerts();
  if (!warnings || warnings.length === 0) {
    return;
  }
  const alert = document.createElement('div');
  alert.className = 'alert alert-warning';
  alert.setAttribute('role', 'alert');
  alert.innerHTML = warnings.map(warning => `<div>${warning}</div>`).join('');
  alertsContainer.appendChild(alert);
}

function enableDownloads() {
  downloadMd.disabled = !latestMarkdown;
  downloadJson.disabled = latestJson === null;
}

function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

downloadMd.addEventListener('click', () => {
  if (!latestMarkdown) return;
  downloadFile('lexsim_simulacion.md', latestMarkdown, 'text/markdown;charset=utf-8');
});

downloadJson.addEventListener('click', () => {
  if (!latestJson) return;
  downloadFile('lexsim_simulacion.json', JSON.stringify(latestJson, null, 2), 'application/json;charset=utf-8');
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const formData = new FormData(form);
  const rawContext = formData.get('contexto') || '';
  const contextError = validateContext(rawContext);
  if (contextError) {
    showError(contextError);
    return;
  }

  showLoading(true);
  resetResults();

  try {
    const payload = buildPayload(formData);
    const response = await fetch('http://localhost:8000/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Error inesperado del servidor');
    }

    const data = await response.json();
    latestMarkdown = data.markdown || '';
    latestJson = data.json || null;

    markdownOutput.textContent = latestMarkdown || 'El modelo no devolvió contenido en Markdown.';
    jsonOutput.textContent = latestJson
      ? JSON.stringify(latestJson, null, 2)
      : 'No se recibió un bloque JSON válido.';

    renderWarnings(data.warnings);
    enableDownloads();
  } catch (error) {
    markdownOutput.textContent = 'Ocurrió un error al generar la simulación.';
    jsonOutput.textContent = String(error.message || error);
  } finally {
    showLoading(false);
  }
});
