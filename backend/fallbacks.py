"""Fallback content builders used when the LLM output is incomplete."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta

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


def _context_points(context: str) -> list[str]:
    """Break the context into short, didactic bullet points."""

    snippet = _normalize_context(context)
    if not snippet:
        return []

    fragments = re.split(r"(?<=[.!?])\s+", snippet)
    bullets = [fragment.strip("- ") for fragment in fragments if len(fragment.strip()) >= 8]
    return bullets[:5]


def _build_role_map(materia: str) -> list[str]:
    """Return tailored role guidance according to the legal area."""

    materia = materia.lower()
    if materia == "penal":
        return [
            "Juez(a): resalta garantías y controla objeciones sobre cadena de custodia.",
            "Fiscalía: enfatiza dolo o culpa con base en testimonios y peritajes viales.",
            "Defensa: instala duda razonable sobre causalidad, visibilidad y deber objetivo de cuidado.",
            "Perito en tránsito: explica recreación del siniestro y límites de su pericia.",
        ]
    if materia == "civil":
        return [
            "Juez(a): delimita la litis y verifica legitimación en la causa.",
            "Parte demandante: acredita daño y nexo causal con documentos y testigos técnicos.",
            "Parte demandada: cuestiona cuantificación y prueba pericial presentada.",
            "Perito contable o de daños: detalla metodología de tasación propuesta.",
        ]
    if materia == "laboral":
        return [
            "Juez(a) laboral: procura principio de primacía de la realidad y economía procesal.",
            "Trabajador(a): sostiene hechos mediante relato cronológico y documentos contractuales.",
            "Empleador(a): se enfoca en reglamentos internos y cumplimiento de obligaciones.",
            "Inspector(a) de trabajo: aporta criterios técnicos sobre condiciones y riesgos.",
        ]
    return [
        "Moderador(a) docente: marca ritmo de la simulación y enlaza con normativa aplicable.",
        "Parte actora: estructura relato coherente con la hipótesis jurídica principal.",
        "Parte opositora: plantea excepciones y objeciones estratégicas.",
        "Experto(a) invitado(a): entrega marco técnico o normativo que refuerza la discusión.",
    ]


def _risk_guidance(materia: str) -> list[str]:
    """Suggest key procedural risks based on the subject matter."""

    materia = materia.lower()
    mapping = {
        "penal": [
            "Cadena de custodia deficiente o discutible en evidencia material o digital.",
            "Confusión entre culpa y dolo al formular los cargos o solicitar la condena.",
            "Testigos presenciales con percepciones limitadas por ángulos o iluminación.",
        ],
        "civil": [
            "Documentos sin protocolizar que pueden recibir tacha de falsedad.",
            "Falta de peritaje actualizado que respalde cuantificación de perjuicios.",
            "Nexo causal débil entre la conducta imputada y el daño alegado.",
        ],
        "laboral": [
            "Insuficiente acreditación de subordinación o dependencia económica.",
            "Registros de jornada incompletos que dificultan probar horas extra.",
            "Testigos compañeros con posible sesgo por solidaridad laboral.",
        ],
    }
    return mapping.get(
        materia,
        [
            "Falta de delimitación clara de la litis y de los hechos controvertidos.",
            "Uso de objeciones improcedentes que entorpecen el flujo didáctico.",
            "Evidencia sin trazabilidad descrita que afecte la credibilidad del ejercicio.",
        ],
    )


def _learning_focus(nivel: str, objetivo: str) -> list[str]:
    """Craft learning focus bullets according to level and objective."""

    nivel = nivel.lower()
    base = [
        f"Conectar todas las intervenciones con el objetivo didáctico: {objetivo}.",
        "Registrar reflexiones posteriores para retroalimentación conjunta.",
    ]

    if nivel == "basico":
        base.insert(0, "Repasar estructura de audiencia y turnos procesales antes de iniciar.")
    elif nivel == "intermedio":
        base.insert(0, "Profundizar en técnicas de objeción y contrainterrogatorio planificado.")
    elif nivel == "avanzado":
        base.insert(0, "Promover improvisación estratégica respetando reglas probatorias.")
    else:
        base.insert(0, "Ajustar el ritmo del ejercicio al bagaje del grupo participante.")

    return base


def build_fallback_markdown(request: SimulateRequest) -> str:
    """Generate a didactic markdown fallback when the model fails."""

    contexto = _normalize_context(request.contexto)
    jurisdiccion = request.jurisdiccion or "Jurisdicción genérica"
    context_points = _context_points(request.contexto)
    if not context_points:
        context_points = [
            "El contexto proporcionado fue muy breve; se recomienda ampliarlo antes de la simulación.",
        ]

    role_map = _build_role_map(request.materia)
    risks = _risk_guidance(request.materia)
    learning_focus = _learning_focus(request.nivel, request.objetivo_didactico)

    lines = [
        "# Simulación de respaldo LexSim",
        "",
        "_Contenido generado automáticamente debido a un fallo del modelo._",
        "",
        "## Resumen del caso",
        f"- **Jurisdicción:** {jurisdiccion}",
        f"- **Materia:** {request.materia}",
        f"- **Nivel:** {request.nivel}",
        f"- **Objetivo didáctico:** {request.objetivo_didactico}",
        f"- **Duración estimada:** {request.duracion_min} minutos",
        "",
        "### Contexto sintetizado",
        contexto or "El contexto proporcionado fue muy breve, se recomienda revisarlo.",
        "",
        "#### Hechos clave a resaltar",
    ]

    lines.extend(f"- {point}" for point in context_points)

    lines.extend(
        [
            "",
            "## Plan mínimo de audiencia (90 minutos)",
            "1. **Apertura (15 min):** Presentar teoría del caso, delimitar hechos y normas aplicables.",
            "2. **Presentación de pruebas (40 min):** Introducir documentos, testimonios y pericias del bloque de respaldo.",
            "3. **Contrainterrogatorios (20 min):** Enfatizar objeciones frecuentes y control judicial activo.",
            "4. **Alegatos de cierre (10 min):** Vincular evidencias con estándares probatorios.",
            "5. **Retroalimentación docente (5 min):** Resaltar aprendizajes y puntos a reforzar.",
            "",
            "### Roles sugeridos",
        ]
    )

    lines.extend(f"- {role}" for role in role_map)

    lines.extend(
        [
            "",
            "### Riesgos procesales a monitorear",
        ]
    )

    lines.extend(f"- {risk}" for risk in risks)

    lines.extend(
        [
            "",
            "### Líneas argumentales iniciales",
            "- **Parte acusadora/actora:** Relaciona el contexto con normativa y estándares probatorios.",
            "- **Parte defensora/opositora:** Identifica vacíos fácticos o contradicciones derivadas del fallback.",
            "- **Testigos y peritos:** Preparan relatos breves centrados en hechos observables y límites metodológicos.",
            "",
            "### Enfoque pedagógico sugerido",
        ]
    )

    lines.extend(f"- {item}" for item in learning_focus)

    lines.extend(
        [
            "",
            "### Banco de preguntas rápidas",
            "- ¿Qué objeción sería más eficaz frente a cada prueba adversa?",
            "- ¿Cómo justificar la admisión de la evidencia con base en reglas locales?",
            "- ¿Qué variantes podrían explorar los estudiantes para fortalecer la simulación?",
            "",
            "### Próximos pasos recomendados",
            "1. Ajustar o ampliar el contexto antes de reutilizar el fallback.",
            "2. Preparar guiones individuales con base en los roles sugeridos.",
            "3. Registrar conclusiones en acta pedagógica para dar seguimiento.",
            "",
            "---",
            "_Este material de contingencia asegura que la práctica pedagógica pueda continuar aun sin la salida del modelo._",
        ]
    )

    return "\n".join(lines)


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
