"""Pydantic schemas for LexSim API."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator


class SimulateRequest(BaseModel):
    """Request payload for simulation generation."""

    contexto: str = Field(..., min_length=10, description="Contexto del caso")
    jurisdiccion: Optional[str] = Field(
        None, description="Jurisdicción objetivo de la simulación"
    )
    materia: Literal["penal", "civil", "laboral", "administrativo", "otro"] = Field(
        "penal", description="Materia del caso"
    )
    nivel: Literal["basico", "intermedio", "avanzado"] = Field(
        "intermedio", description="Nivel de complejidad"
    )
    objetivo_didactico: str = Field(
        "practicar objeciones y contrainterrogatorio",
        description="Objetivo didáctico principal",
    )
    duracion_min: int = Field(90, ge=30, le=480, description="Duración estimada")
    restricciones: Optional[List[str]] = Field(
        None, description="Restricciones o notas adicionales"
    )

    @validator("contexto")
    def validate_context(cls, value: str) -> str:  # type: ignore[override]
        lines = [line for line in value.strip().splitlines() if line.strip()]
        if len(lines) < 3:
            raise ValueError("El contexto debe contener al menos 3 líneas.")
        if len(lines) > 10:
            raise ValueError("El contexto no debe exceder 10 líneas.")
        return value


class JSONMeta(BaseModel):
    titulo: str
    jurisdiccion: str
    materia: str
    nivel: Literal["basico", "intermedio", "avanzado"]
    objetivo_didactico: str
    duracion_minutos: int


class JSONPersonaje(BaseModel):
    nombre: str
    rol: Literal[
        "juez",
        "fiscal",
        "defensa",
        "demandante",
        "demandado",
        "testigo",
        "perito",
        "policia",
        "otro",
    ]
    bio: str
    objetivos: List[str]
    sesgos: List[str]


class JSONCronologia(BaseModel):
    t: str
    evento: str


class JSONPlanteamiento(BaseModel):
    tipo: Literal["penal", "civil", "laboral", "administrativo", "otro"]
    cargos_o_pretensiones: List[str]
    estandar_probatorio: str
    notas: str


class JSONPruebaDocumental(BaseModel):
    id: str
    descripcion: str
    origen: str
    autenticidad_custodia: str
    posibles_objeciones: List[str]


class JSONPruebaTestimonial(BaseModel):
    id: str
    testigo: str
    alcance: str
    riesgos_credibilidad: List[str]
    contrapreguntas_sugeridas: List[str]


class JSONPruebaPericial(BaseModel):
    id: str
    area: str
    metodo: str
    limites: str
    validez: str


class JSONPruebaDigitalFisica(BaseModel):
    id: str
    tipo: Literal["digital", "fisica"]
    descripcion: str
    hash: str
    metadatos: Dict[str, str]
    cadena_custodia: str


class JSONPruebas(BaseModel):
    documental: List[JSONPruebaDocumental]
    testimonial: List[JSONPruebaTestimonial]
    pericial: List[JSONPruebaPericial]
    digital_fisica: List[JSONPruebaDigitalFisica]


class JSONInterrogatorio(BaseModel):
    tipo: Literal["directo", "contrainterrogatorio"]
    a_quien: str
    preguntas: List[str]


class JSONObjecion(BaseModel):
    objecion: str
    fundamento: str


class JSONApertura(BaseModel):
    parte_1: str
    parte_2: str


class JSONCierre(BaseModel):
    parte_1: str
    parte_2: str


class JSONGuion(BaseModel):
    instrucciones_iniciales_juez: str
    apertura: JSONApertura
    interrogatorios: List[JSONInterrogatorio]
    objeciones_tipicas: List[JSONObjecion]
    cierre: JSONCierre
    instrucciones_finales_juez: str


class JSONMatrizVeredicto(BaseModel):
    criterio: str
    peso: float
    observaciones: str


class JSONResultadoAlternativo(BaseModel):
    escenario: str
    descripcion: str


class JSONDecision(BaseModel):
    criterios: List[str]
    matriz_veredicto: List[JSONMatrizVeredicto]
    resultados_alternativos: List[JSONResultadoAlternativo]


class JSONRubrica(BaseModel):
    criterio: str
    niveles: Dict[str, str]
    puntaje_max: int


class JSONGlosario(BaseModel):
    termino: str
    definicion: str


class SimulationJSON(BaseModel):
    meta: JSONMeta
    personajes: List[JSONPersonaje]
    cronologia: List[JSONCronologia]
    planteamiento_juridico: JSONPlanteamiento
    pruebas: JSONPruebas
    guion: JSONGuion
    decision: JSONDecision
    banco_preguntas: List[str]
    rubrica: List[JSONRubrica]
    variantes: List[str]
    glosario: List[JSONGlosario]


class SimulateResponse(BaseModel):
    """Response payload for simulation generation."""

    markdown: str
    json: Optional[SimulationJSON]
    warnings: List[str] = Field(default_factory=list)


__all__ = [
    "SimulateRequest",
    "SimulateResponse",
    "SimulationJSON",
]
