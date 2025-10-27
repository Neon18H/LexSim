# LexSim

LexSim es un agente pedagógico de simulación de juicios que genera un guion completo en Markdown y un bloque JSON estructurado a partir de un contexto breve. El proyecto se entrega como solución full-stack (FastAPI + frontend estático con Bootstrap) y está listo para ejecutarse localmente o con Docker Compose.

## Arquitectura

- **Backend (`backend/`)**: API FastAPI que expone los endpoints `GET /health` y `POST /api/simulate`. Integra modelos gratuitos de OpenRouter, realiza validación de JSON y aplica un rate limit simple.
- **Frontend (`frontend/`)**: Página HTML5 responsiva desarrollada con Bootstrap 5 y JavaScript puro. Consume la API y permite descargar los resultados.
- **Infraestructura**: Dockerfiles independientes y `docker-compose.yml` para levantar ambos servicios. Variables de entorno gestionadas con `.env`.

## Requisitos previos

- Python 3.11+
- Node.js no es necesario (frontend estático)
- Docker y Docker Compose (opcional)

## Variables de entorno

Copia `.env.example` a `.env` en la raíz del proyecto y completa los valores:

```
cp .env.example .env
```

Variables principales:

- `OPENROUTER_API_KEY`: clave personal de OpenRouter (no compartir).
- `OPENROUTER_MODEL`: modelo gratuito principal. Valor por defecto `mistralai/mistral-7b-instruct:free`.
- `OPENROUTER_FALLBACKS`: lista separada por comas con modelos de respaldo gratuitos.
- `CORS_ORIGINS`: orígenes permitidos para el frontend (por defecto `http://localhost:8080`).
- `RATE_LIMIT_PER_MINUTE`: número máximo de solicitudes por minuto e IP (30 por defecto).

## Ejecución local (sin Docker)

1. Instala dependencias del backend:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # En Windows usa .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. Arranca el servidor FastAPI:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. Levanta el frontend con un servidor estático, por ejemplo:

   ```bash
   cd ../frontend
   python -m http.server 8080
   ```

4. Abre `http://localhost:8080` en tu navegador. Ingresa el contexto del caso (3 a 10 líneas) y genera la simulación. El mensaje “Demo académica (no asesoría legal)” recuerda que el contenido es ficticio.

## Ejecución con Docker Compose

1. Copia `.env.example` a `.env` y define tu `OPENROUTER_API_KEY`.
2. Desde la raíz del proyecto ejecuta:

   ```bash
   docker compose up --build
   ```

3. El backend quedará disponible en `http://localhost:8000` y el frontend en `http://localhost:8080`.

## Pruebas automatizadas

El backend cuenta con pruebas mínimas usando `pytest`.

```bash
cd backend
pytest
```

## Seguridad y buenas prácticas

- La clave de OpenRouter se mantiene en el backend y nunca se expone en el frontend.
- Se aplica un rate limit en memoria (30 solicitudes por minuto por IP) para `/api/simulate`.
- El frontend presenta el Markdown como texto preformateado sin ejecutar HTML para evitar inyecciones.
- Todos los nombres y lugares generados son ficticios.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
