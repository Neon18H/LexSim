"""Unit tests for the extractor utilities."""
from __future__ import annotations

import json

from backend.extractor import extract_simulation_payload


def _build_valid_json() -> str:
    payload = {
        "meta": {
            "titulo": "Caso sin markdown",
            "jurisdiccion": "Penal acusatorio hispano genérico",
            "materia": "penal",
            "nivel": "intermedio",
            "objetivo_didactico": "analizar respuestas solo estructuradas",
            "duracion_minutos": 90,
        },
        "personajes": [
            {
                "nombre": "Juez Ficticio",
                "rol": "juez",
                "bio": "Perfil breve ficticio",
                "objetivos": ["Asegurar orden"],
                "sesgos": ["Formalismo"],
            }
        ],
        "cronologia": [{"t": "2030-01-01 10:00", "evento": "Inicio"}],
        "planteamiento_juridico": {
            "tipo": "penal",
            "cargos_o_pretensiones": ["Falta de markdown"],
            "estandar_probatorio": "Más allá de duda razonable",
            "notas": "Escenario de prueba",
        },
        "pruebas": {
            "documental": [
                {
                    "id": "DOC-01",
                    "descripcion": "Documento de ejemplo",
                    "origen": "Archivo académico",
                    "autenticidad_custodia": "Sin rupturas",
                    "posibles_objeciones": ["Pertinencia"],
                }
            ],
            "testimonial": [
                {
                    "id": "TES-01",
                    "testigo": "Persona Test",
                    "alcance": "Observó parcialmente",
                    "riesgos_credibilidad": ["Memoria limitada"],
                    "contrapreguntas_sugeridas": ["Precisa detalles"],
                }
            ],
            "pericial": [
                {
                    "id": "PER-01",
                    "area": "Forense",
                    "metodo": "Revisión básica",
                    "limites": "Datos hipotéticos",
                    "validez": "Estandarizada",
                }
            ],
            "digital_fisica": [
                {
                    "id": "DIG-01",
                    "tipo": "digital",
                    "descripcion": "Evidencia multimedia",
                    "hash": "abc123",
                    "metadatos": {"duracion": "00:01:00"},
                    "cadena_custodia": "Custodia simulada",
                }
            ],
        },
        "guion": {
            "instrucciones_iniciales_juez": "Saludo introductorio",
            "apertura": {"parte_1": "Versión fiscal", "parte_2": "Versión defensa"},
            "interrogatorios": [
                {
                    "tipo": "directo",
                    "a_quien": "Testigo TES-01",
                    "preguntas": ["¿Qué observó?"],
                }
            ],
            "objeciones_tipicas": [
                {"objecion": "leading", "fundamento": "Pregunta sugiere respuesta"}
            ],
            "cierre": {"parte_1": "Conclusión fiscal", "parte_2": "Conclusión defensa"},
            "instrucciones_finales_juez": "Reflexión final",
        },
        "decision": {
            "criterios": ["Calidad de la evidencia"],
            "matriz_veredicto": [
                {
                    "criterio": "Cadena de custodia",
                    "peso": 0.3,
                    "observaciones": "Sin anomalías",
                }
            ],
            "resultados_alternativos": [
                {"escenario": "A", "descripcion": "Resultado alterno"}
            ],
        },
        "banco_preguntas": ["¿Qué objeción aplica?"],
        "rubrica": [
            {
                "criterio": "Dominio probatorio",
                "niveles": {
                    "excelente": "Identifica objeciones complejas",
                    "bueno": "Reconoce objeciones básicas",
                    "basico": "Requiere guía",
                },
                "puntaje_max": 10,
            }
        ],
        "variantes": ["Cambiar a materia civil"],
        "glosario": [
            {"termino": "Objeción", "definicion": "Impugnación a una pregunta"}
        ],
    }
    return json.dumps(payload)


def test_extract_simulation_payload_without_markdown():
    json_payload = _build_valid_json()
    raw_response = f"```json\n{json_payload}\n```"

    markdown, simulation_json, warnings = extract_simulation_payload(raw_response)

    assert markdown == ""
    assert simulation_json is not None
    assert any("Markdown" in warning for warning in warnings)
