"""Fallback content builders used when the LLM output is incomplete."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from textwrap import dedent

from .schemas import (
    JSONApertura,
    JSONCierre,
    JSONCronologia,
    JSONDecision,
    JSONGlosario,
    JSONGuion,
    JSONInterrogatorio,
    JSONMeta,
    JSONObjecion,
    JSONPersonaje,
    JSONPlanteamiento,
    JSONPruebaDigitalFisica,
    JSONPruebaDocumental,
    JSONPruebaPericial,
    JSONPruebaTestimonial,
    JSONPruebas,
    JSONRubrica,
    JSONResultadoAlternativo,
    JSONMatrizVeredicto,
    SimulationJSON,
    SimulateRequest,
)


_FALLBACK_BASE_TIME = datetime(2035, 1, 1, 9, 0)


def _normalize_context(context: str) -> str:
    snippet = " ".join(context.split())
    return snippet[:280].strip()


def build_fallback_markdown(request: SimulateRequest) -> str:
    """Generate a didactic markdown fallback when the model fails."""

    contexto = _normalize_context(request.contexto)
    jurisdiccion = request.jurisdiccion or "Jurisdicción genérica"
    header = "# Simulación de respaldo LexSim"
    body = dedent(
        f"""
        _Contenido generado automáticamente debido a un fallo del modelo._

        ## Resumen del caso
        - **Jurisdicción:** {jurisdiccion}
        - **Materia:** {request.materia}
        - **Nivel:** {request.nivel}
        - **Objetivo didáctico:** {request.objetivo_didactico}
        - **Duración estimada:** {request.duracion_min} minutos

        ### Contexto sintetizado
        {contexto or "El contexto proporcionado fue muy breve, se recomienda revisarlo."}

        ### Actividades sugeridas
        1. Analizar los roles propuestos en la estructura JSON de respaldo.
        2. Discutir los riesgos procesales principales y las medidas de mitigación.
        3. Elaborar argumentos introductorios y de cierre para fiscalía y defensa.

        ---
        _Este material de contingencia asegura que la práctica pedagógica pueda continuar aun sin la salida del modelo._
        """
    ).strip()

    return f"{header}\n\n{body}"


def _build_timeline(base_time: datetime) -> list[JSONCronologia]:
    events = [
        ("Inicio de audiencia de acusación", 0),
        ("Presentación de pruebas y objeciones", 30),
        ("Deliberación y conclusiones pedagógicas", 90),
    ]
    timeline = []
    for description, offset in events:
        moment = base_time + timedelta(minutes=offset)
        timeline.append(
            JSONCronologia(t=moment.strftime("%Y-%m-%d %H:%M"), evento=description)
        )
    return timeline


def _hash_context(context: str) -> str:
    digest = hashlib.sha256(context.encode("utf-8")).hexdigest()
    return digest[:16]


def build_fallback_simulation_json(request: SimulateRequest) -> SimulationJSON:
    """Generate a deterministic JSON structure to keep the workflow running."""

    jurisdiccion = request.jurisdiccion or "Jurisdicción genérica"
    context_snippet = _normalize_context(request.contexto) or "Contexto resumido no disponible"
    context_hash = _hash_context(context_snippet or request.contexto)

    meta = JSONMeta(
        titulo=f"Simulación de contingencia: {request.materia.title()}",
        jurisdiccion=jurisdiccion,
        materia=request.materia,
        nivel=request.nivel,
        objetivo_didactico=request.objetivo_didactico,
        duracion_minutos=request.duracion_min,
    )

    personajes = [
        JSONPersonaje(
            nombre="Juez(a) de Control LexSim",
            rol="juez",
            bio="Facilitador ficticio que modera el ejercicio cuando el modelo falla.",
            objetivos=["Garantizar continuidad de la práctica", "Modelar decisiones imparciales"],
            sesgos=["Preferencia por material estructurado"],
        ),
        JSONPersonaje(
            nombre="Fiscal sustituto",
            rol="fiscal",
            bio="Representación académica que usa el contexto proporcionado para sustentar cargos.",
            objetivos=["Vincular hechos a la teoría del caso", "Aprovechar el material de respaldo"],
            sesgos=["Confianza en informes escritos"],
        ),
        JSONPersonaje(
            nombre="Defensor(a) de oficio académico",
            rol="defensa",
            bio="Profesional ficticio encargado de impugnar la versión acusatoria usando solo el contexto.",
            objetivos=["Resaltar dudas razonables", "Proteger el debido proceso"],
            sesgos=["Estrategias prudentes"],
        ),
        JSONPersonaje(
            nombre="Testigo contextual",
            rol="testigo",
            bio="Figura creada para narrar los hechos descritos en el contexto proporcionado.",
            objetivos=["Describir hechos relevantes", "Responder a contrainterrogatorios"],
            sesgos=["Recuerdos influenciados por el estrés"],
        ),
    ]

    cronologia = _build_timeline(_FALLBACK_BASE_TIME)

    planteamiento = JSONPlanteamiento(
        tipo=request.materia if request.materia in {"penal", "civil", "laboral", "administrativo"} else "otro",
        cargos_o_pretensiones=[f"Análisis de responsabilidad según contexto: {context_snippet[:60]}",],
        estandar_probatorio="Determinable según normatividad aplicable",
        notas="Escenario generado automáticamente por ausencia de salida del modelo.",
    )

    pruebas = JSONPruebas(
        documental=[
            JSONPruebaDocumental(
                id="DOC-FB-01",
                descripcion="Resumen documental construido con la información disponible en el contexto.",
                origen="Archivo de respaldo LexSim",
                autenticidad_custodia="Cadena hipotética verificada para fines académicos",
                posibles_objeciones=["Pertinencia", "Fundamento insuficiente"],
            )
        ],
        testimonial=[
            JSONPruebaTestimonial(
                id="TES-FB-01",
                testigo="Testigo contextual",
                alcance="Relata los hechos descritos en el contexto de la solicitud.",
                riesgos_credibilidad=["Memoria dependiente de notas de respaldo"],
                contrapreguntas_sugeridas=[
                    "Precise circunstancias observadas",
                    "Indique fuentes de su conocimiento",
                ],
            )
        ],
        pericial=[
            JSONPruebaPericial(
                id="PER-FB-01",
                area="Reconstrucción de hechos",
                metodo="Análisis de consistencia del contexto",
                limites="Datos incompletos al provenir de un fallback",
                validez="Únicamente para práctica académica",
            )
        ],
        digital_fisica=[
            JSONPruebaDigitalFisica(
                id="DIG-FB-01",
                tipo="digital",
                descripcion="Archivo simulado que resume el contexto aportado.",
                hash=context_hash,
                metadatos={"generado_por": "LexSim fallback", "fiabilidad": "moderada"},
                cadena_custodia="Registro automático interno (uso educativo)",
            )
        ],
    )

    guion = JSONGuion(
        instrucciones_iniciales_juez="Se informa a los participantes que se utiliza material de respaldo debido a un error del modelo.",
        apertura=JSONApertura(
            parte_1="La fiscalía describe los hechos apoyándose en el contexto y los documentos de respaldo.",
            parte_2="La defensa señala posibles fallas en la cadena causal y enfatiza la necesidad de mayor corroboración.",
        ),
        interrogatorios=[
            JSONInterrogatorio(
                tipo="directo",
                a_quien="Testigo contextual",
                preguntas=[
                    "Detalle qué observó según el contexto proporcionado",
                    "Explique cómo reaccionaron los involucrados",
                ],
            ),
            JSONInterrogatorio(
                tipo="contrainterrogatorio",
                a_quien="Testigo contextual",
                preguntas=[
                    "Confirme las limitaciones de su recuerdo",
                    "Señale si recibió instrucciones previas al testimonio",
                ],
            ),
        ],
        objeciones_tipicas=[
            JSONObjecion(
                objecion="leading",
                fundamento="Se sugiere la respuesta al testigo durante el fallback",
            ),
            JSONObjecion(
                objecion="hearsay",
                fundamento="La declaración depende de información secundaria compilada en el fallback",
            ),
        ],
        cierre=JSONCierre(
            parte_1="La fiscalía solicita valorar la coherencia del contexto y la simulación de pruebas.",
            parte_2="La defensa pide absolver ante la ausencia de corroboración directa del modelo.",
        ),
        instrucciones_finales_juez="Los estudiantes deliberarán considerando las limitaciones de este material de respaldo.",
    )

    decision = JSONDecision(
        criterios=[
            "Coherencia interna del contexto",
            "Consistencia de testimonios simulados",
            "Respeto por garantías procesales en el ejercicio",
        ],
        matriz_veredicto=[
            JSONMatrizVeredicto(
                criterio="Análisis del contexto",
                peso=0.4,
                observaciones="Evaluar qué elementos faltan por ausencia del modelo",
            ),
            JSONMatrizVeredicto(
                criterio="Calidad de los interrogatorios",
                peso=0.3,
                observaciones="Considerar si las preguntas cubren todos los hechos",
            ),
            JSONMatrizVeredicto(
                criterio="Argumentación final",
                peso=0.3,
                observaciones="Valorar la incorporación crítica del material de respaldo",
            ),
        ],
        resultados_alternativos=[
            JSONResultadoAlternativo(
                escenario="A",
                descripcion="Se dicta responsabilidad simbólica con base en el material de respaldo",
            ),
            JSONResultadoAlternativo(
                escenario="B",
                descripcion="Se absuelve ante las limitaciones derivadas del uso del fallback",
            ),
        ],
    )

    rubrica = [
        JSONRubrica(
            criterio="Dominio del caso de respaldo",
            niveles={
                "excelente": "Integra críticamente el fallback con referencias normativas.",
                "bueno": "Utiliza adecuadamente el fallback identificando riesgos.",
                "basico": "Depende casi exclusivamente del material entregado sin análisis crítico.",
            },
            puntaje_max=10,
        )
    ]

    glosario = [
        JSONGlosario(
            termino="Fallback pedagógico",
            definicion="Material generado automáticamente para continuar la simulación cuando falla el modelo.",
        ),
        JSONGlosario(
            termino="Cadena de custodia simulada",
            definicion="Registro ficticio que preserva trazabilidad en ejercicios académicos.",
        ),
    ]

    return SimulationJSON(
        meta=meta,
        personajes=personajes,
        cronologia=cronologia,
        planteamiento_juridico=planteamiento,
        pruebas=pruebas,
        guion=guion,
        decision=decision,
        banco_preguntas=[
            "¿Cómo se adaptan los roles cuando se trabaja con un fallback?",
            "¿Qué riesgos probatorios emergen al no contar con evidencia completa?",
            "¿Qué estrategias de objeción son prioritarias en este escenario?",
        ],
        rubrica=rubrica,
        variantes=[
            "Reformular el caso a materia administrativa usando el mismo fallback.",
            "Solicitar a los estudiantes generar pruebas adicionales para reforzar la simulación.",
        ],
        glosario=glosario,
    )


__all__ = [
    "build_fallback_markdown",
    "build_fallback_simulation_json",
]
