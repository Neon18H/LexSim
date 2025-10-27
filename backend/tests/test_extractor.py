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


def test_extract_simulation_payload_nested_braces():
    nested_json = json.dumps(
        {
            "meta": {
                "titulo": "x",
                "jurisdiccion": "y",
                "materia": "penal",
                "nivel": "basico",
                "objetivo_didactico": "z",
                "duracion_minutos": 60,
            },
            "personajes": [
                {
                    "nombre": "Test",
                    "rol": "juez",
                    "bio": "Bio",
                    "objetivos": ["Objetivo"],
                    "sesgos": ["Sesgo"],
                }
            ],
            "cronologia": [{"t": "2030-01-01 09:00", "evento": "Inicio"}],
            "planteamiento_juridico": {
                "tipo": "penal",
                "cargos_o_pretensiones": ["Cargo"],
                "estandar_probatorio": "Estandar",
                "notas": "Notas",
            },
            "pruebas": {
                "documental": [
                    {
                        "id": "DOC-1",
                        "descripcion": "Desc",
                        "origen": "Origen",
                        "autenticidad_custodia": "Cadena",
                        "posibles_objeciones": ["Objecion"],
                    }
                ],
                "testimonial": [
                    {
                        "id": "TES-1",
                        "testigo": "Testigo",
                        "alcance": "Alcance",
                        "riesgos_credibilidad": ["Riesgo"],
                        "contrapreguntas_sugeridas": ["Pregunta"],
                    }
                ],
                "pericial": [
                    {
                        "id": "PER-1",
                        "area": "Area",
                        "metodo": "Metodo",
                        "limites": "Limites",
                        "validez": "Validez",
                    }
                ],
                "digital_fisica": [
                    {
                        "id": "DIG-1",
                        "tipo": "digital",
                        "descripcion": "Descripcion",
                        "hash": "abc123",
                        "metadatos": {"duracion": "1m"},
                        "cadena_custodia": "Cadena",
                    }
                ],
            },
            "guion": {
                "instrucciones_iniciales_juez": "Inicio",
                "apertura": {"parte_1": "Parte1", "parte_2": "Parte2"},
                "interrogatorios": [
                    {
                        "tipo": "directo",
                        "a_quien": "Testigo",
                        "preguntas": ["¿Qué sucedió?"],
                    }
                ],
                "objeciones_tipicas": [
                    {"objecion": "leading", "fundamento": "Sugiere respuesta"}
                ],
                "cierre": {"parte_1": "Cierre1", "parte_2": "Cierre2"},
                "instrucciones_finales_juez": "Final",
            },
            "decision": {
                "criterios": ["Criterio"],
                "matriz_veredicto": [
                    {"criterio": "Criterio", "peso": 0.5, "observaciones": "Obs"}
                ],
                "resultados_alternativos": [
                    {"escenario": "A", "descripcion": "Descripcion"}
                ],
            },
            "banco_preguntas": ["Pregunta"],
            "rubrica": [
                {
                    "criterio": "Dominio",
                    "niveles": {
                        "excelente": "Excelente",
                        "bueno": "Bueno",
                        "basico": "Basico",
                    },
                    "puntaje_max": 10,
                }
            ],
            "variantes": ["Variante"],
            "glosario": [{"termino": "Termino", "definicion": "Definicion"}],
        }
    )
    raw_response = f"Contenido introductorio\n```json\n{nested_json}\n```\nConclusión"

    markdown, simulation_json, warnings = extract_simulation_payload(raw_response)

    assert "Contenido introductorio" in markdown
    assert "Conclusión" in markdown
    assert simulation_json is not None
    assert not any("No se detectó un bloque JSON válido" in warning for warning in warnings)


def test_extract_simulation_payload_recovers_trailing_commas():
    json_payload = _build_valid_json().replace(
        '"variantes": ["Cambiar a materia civil"]',
        '"variantes": ["Cambiar a materia civil",]'
    )
    raw_response = f"Intro\n```json\n{json_payload}\n```"

    markdown, simulation_json, warnings = extract_simulation_payload(raw_response)

    assert "Intro" in markdown
    assert simulation_json is not None
    assert warnings == []


def test_extract_simulation_payload_strips_json_comments():
    json_payload = _build_valid_json()
    json_with_comment = json_payload[:-1] + "\n// comentario extra del modelo\n}"
    raw_response = f"```json\n{json_with_comment}\n```"

    markdown, simulation_json, warnings = extract_simulation_payload(raw_response)

    assert markdown == ""
    assert simulation_json is not None
    assert warnings == [
        "El modelo no devolvió contenido en Markdown. Se entrega solo el JSON estructurado disponible."
    ]
