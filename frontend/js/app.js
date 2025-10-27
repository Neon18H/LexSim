const form = document.getElementById('simulation-form');
const stepsPane = document.getElementById('steps-pane');
const summaryPane = document.getElementById('summary-pane');
const metadataPane = document.getElementById('metadata-pane');
const downloadButton = document.getElementById('download-result');
let lastResult = null;

const resolveApiBase = () => {
  const { protocol, hostname, port } = window.location;
  if (port === '8080') {
    return `${protocol}//${hostname}:8000`;
  }
  if (protocol.startsWith('http')) {
    return `${protocol}//${hostname}:8000`;
  }
  return 'http://localhost:8000';
};

const API_BASE = resolveApiBase();

const renderList = (container, items) => {
  if (!items || items.length === 0) {
    container.innerHTML = '<p class="text-muted">No hay datos disponibles.</p>';
    return;
  }

  const list = document.createElement('ul');
  list.className = 'list-unstyled';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    list.appendChild(li);
  });
  container.replaceChildren(list);
};

const renderMetadata = (container, metadata) => {
  if (!metadata || Object.keys(metadata).length === 0) {
    container.innerHTML = '<p class="text-muted">Sin metadatos.</p>';
    return;
  }

  const list = document.createElement('dl');
  list.className = 'row';
  Object.entries(metadata).forEach(([key, value]) => {
    const term = document.createElement('dt');
    term.className = 'col-sm-4 text-capitalize';
    term.textContent = key.replace(/_/g, ' ');
    const detail = document.createElement('dd');
    detail.className = 'col-sm-8';
    detail.textContent = value;
    list.appendChild(term);
    list.appendChild(detail);
  });
  container.replaceChildren(list);
};

const resetResults = () => {
  stepsPane.innerHTML = '<p class="text-muted">Aún no hay simulaciones.</p>';
  summaryPane.innerHTML = '';
  metadataPane.innerHTML = '';
  downloadButton.disabled = true;
  lastResult = null;
};

const showError = (message) => {
  const alert = document.createElement('div');
  alert.className = 'alert alert-danger';
  alert.textContent = message;
  stepsPane.replaceChildren(alert);
  summaryPane.innerHTML = '';
  metadataPane.innerHTML = '';
  downloadButton.disabled = true;
};

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  const temperatureValue = document.getElementById('temperature').value;
  const maxStepsValue = document.getElementById('max-steps').value;

  if (!prompt) {
    showError('El prompt no puede estar vacío.');
    return;
  }

  const payload = { prompt };
  const parameters = {};
  if (temperatureValue !== '') parameters.temperature = Number(temperatureValue);
  if (maxStepsValue !== '') parameters.max_steps = Number(maxStepsValue);
  if (Object.keys(parameters).length > 0) {
    payload.parameters = parameters;
  }

  stepsPane.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
  summaryPane.innerHTML = '';
  metadataPane.innerHTML = '';

  try {
    const response = await fetch(`${API_BASE}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('No se pudo completar la simulación.');
    }

    const result = await response.json();
    lastResult = result;
    renderList(stepsPane, result.steps);
    summaryPane.textContent = result.summary;
    renderMetadata(metadataPane, result.metadata);
    downloadButton.disabled = false;
  } catch (error) {
    console.error(error);
    showError(error.message || 'Error inesperado.');
  }
});

downloadButton.addEventListener('click', () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'lexsim-result.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

resetResults();
