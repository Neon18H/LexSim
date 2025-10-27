"""Tests for the simulate endpoint."""
from __future__ import annotations

import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.service_llm import SYSTEM_PROMPT

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_call_openrouter(monkeypatch):
    async def _fake_call(system_prompt: str, user_prompt: str) -> str:
        assert system_prompt == SYSTEM_PROMPT
        assert "Genera una simulación de juicio" in user_prompt
        sample_json = {
            "meta": {
                "titulo": "Caso de prueba LexSim",
                "jurisdiccion": "Penal acusatorio hispano genérico",
                "materia": "penal",
                "nivel": "intermedio",
                "objetivo_didactico": "practicar objeciones y contrainterrogatorio",
                "duracion_minutos": 90,
            },
            "personajes": [
                {
                    "nombre": "Juez Marta Robles",
                    "rol": "juez",
                    "bio": "Magistrada ficticia con años de experiencia en audiencias orales.",
                    "objetivos": ["Garantizar un proceso justo"],
                    "sesgos": ["Respeto estricto por la cadena de custodia"],
                }
            ],
            "cronologia": [{"t": "2034-05-01 09:00", "evento": "Apertura de la audiencia"}],
            "planteamiento_juridico": {
                "tipo": "penal",
                "cargos_o_pretensiones": ["Robo agravado"],
                "estandar_probatorio": "Más allá de duda razonable",
                "notas": "Caso diseñado para práctica académica",
            },
            "pruebas": {
                "documental": [
                    {
                        "id": "DOC-01",
                        "descripcion": "Informe policial narrativo",
                        "origen": "Policía didáctica de Ciudad Prisma",
                        "autenticidad_custodia": "Sellado ficticio sin rupturas",
                        "posibles_objeciones": ["Hearsay"],
                    }
                ],
                "testimonial": [
                    {
                        "id": "TES-01",
                        "testigo": "Diego Luna",
                        "alcance": "Observó parcialmente los hechos",
                        "riesgos_credibilidad": ["Memoria limitada"],
                        "contrapreguntas_sugeridas": ["Aclara el ángulo de visión"],
                    }
                ],
                "pericial": [
                    {
                        "id": "PER-01",
                        "area": "Balística",
                        "metodo": "Análisis comparativo básico",
                        "limites": "Datos parciales",
                        "validez": "Procedimiento estándar documentado",
                    }
                ],
                "digital_fisica": [
                    {
                        "id": "DIG-01",
                        "tipo": "digital",
                        "descripcion": "Video de cámara de seguridad",
                        "hash": "abc123def456",
                        "metadatos": {"duracion": "00:02:30"},
                        "cadena_custodia": "Transferencia supervisada continua",
                    }
                ],
            },
            "guion": {
                "instrucciones_iniciales_juez": "Recordatorio de roles y etiqueta.",
                "apertura": {
                    "parte_1": "Narrativa de la fiscalía ficticia.",
                    "parte_2": "Respuesta de la defensa académica.",
                },
                "interrogatorios": [
                    {
                        "tipo": "directo",
                        "a_quien": "Testigo TES-01",
                        "preguntas": ["Relata lo que observaste"],
                    }
                ],
                "objeciones_tipicas": [
                    {"objecion": "leading", "fundamento": "Pregunta sugiere respuesta"}
                ],
                "cierre": {
                    "parte_1": "Resumen fiscal con énfasis en pruebas digitales.",
                    "parte_2": "Cierre defensivo resaltando dudas razonables.",
                },
                "instrucciones_finales_juez": "Deliberación simulada y reflexión académica.",
            },
            "decision": {
                "criterios": ["Credibilidad testimonial"],
                "matriz_veredicto": [
                    {
                        "criterio": "Evidencia digital",
                        "peso": 0.2,
                        "observaciones": "Revisar integridad del hash",
                    }
                ],
                "resultados_alternativos": [
                    {
                        "escenario": "A",
                        "descripcion": "Condena simulada si la evidencia es convincente",
                    }
                ],
            },
            "banco_preguntas": ["¿Qué objeción aplica a la pregunta X?"],
            "rubrica": [
                {
                    "criterio": "Dominio normativo",
                    "niveles": {
                        "excelente": "Identifica correctamente objeciones complejas",
                        "bueno": "Reconoce objeciones básicas",
                        "basico": "Requiere guía constante",
                    },
                    "puntaje_max": 10,
                }
            ],
            "variantes": ["Transformar el caso a materia civil"],
            "glosario": [
                {"termino": "Cadena de custodia", "definicion": "Registro de control de evidencia"}
            ],
        }
        markdown = "# Simulación LexSim\n\nContenido pedagógico ficticio."
        json_block = json.dumps(sample_json)
        return f"{markdown}\n\n```json\n{json_block}\n```"

    monkeypatch.setattr("backend.router.call_openrouter", _fake_call)
    yield
    monkeypatch.delattr("backend.router", "call_openrouter")


def test_simulate_returns_expected_payload():
    payload: Dict[str, Any] = {
        "contexto": "Linea 1\nLinea 2\nLinea 3",
        "materia": "penal",
        "nivel": "intermedio",
        "duracion_min": 90,
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "markdown" in data and data["markdown"].startswith("# Simulación LexSim")
    assert data["json"]["meta"]["titulo"] == "Caso de prueba LexSim"
    assert data["warnings"] == []
