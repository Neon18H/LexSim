# LexSim

LexSim es una demostración minimalista de una aplicación full-stack que simula narrativas a partir de un prompt. El proyecto está dividido en un backend basado en FastAPI y un frontend estático elaborado con Bootstrap 5.

## Estructura del proyecto

```
backend/
  Dockerfile
  extractor.py
  main.py
  requirements.txt
  service_llm.py
  settings.py
  tests/
frontend/
  Dockerfile
  css/
    styles.css
  index.html
  js/
    app.js
.env.example
LICENSE
docker-compose.yml
README.md
```

## Requisitos

* Python 3.11+
* NodeJS no es necesario (el frontend es estático)
* Docker (opcional) para ejecutar los servicios en contenedores

## Configuración del backend

1. Cree un entorno virtual e instale las dependencias:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. Copie `.env.example` a `.env` y ajuste los valores según sea necesario.

3. Inicie el servidor de desarrollo:

   ```bash
   uvicorn backend.main:app --reload
   ```

El backend expone los siguientes endpoints:

* `GET /health`: verificación de estado.
* `POST /api/simulate`: recibe un JSON con el `prompt` y parámetros opcionales (`temperature`, `max_steps`). Devuelve los pasos generados y metadatos del proceso.

## Pruebas

Ejecute la suite de pruebas de FastAPI con:

```bash
pytest backend/tests
```

## Frontend

Abra `frontend/index.html` en su navegador. La interfaz permite:

* Introducir un prompt y parámetros opcionales.
* Visualizar los resultados en pestañas.
* Descargar un archivo JSON con la simulación.

Para servir el frontend de forma local puede utilizar cualquier servidor estático, por ejemplo:

```bash
python -m http.server --directory frontend 8000
```

## Ejecución con Docker Compose

1. Construya las imágenes y levante los servicios:

   ```bash
   docker-compose up --build
   ```

2. El backend estará disponible en `http://localhost:8000` y el frontend en `http://localhost:8080`.

## Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT, disponible en `LICENSE`.
