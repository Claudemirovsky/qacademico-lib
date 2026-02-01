from pydantic import BaseModel, Field, BeforeValidator
from typing import Any, Annotated


def br_float_parser(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, int):
        return float(val)
    if isinstance(val, float):
        return val
    if not isinstance(val, str):
        raise ValueError(f"{val} is not a string.")
    return float(val.replace(",", "."))


class BoletimSemestreEtapas(BaseModel):
    sigla: str
    descricao: str
    nota: Annotated[float, BeforeValidator(br_float_parser)] | None
    tipo_media: str = Field(alias="tipoMedia")


class BoletimItem(BaseModel):
    id_diario: int = Field(alias="idDiario")
    sigla: str
    descricao: str
    carga_horaria: int = Field(alias="cargaHoraria")
    semestre: int | None = Field(alias="periodoTurma")
    turma: str
    professor: str
    avaliacao: Annotated[float, BeforeValidator(br_float_parser)] | None
    aulas_dadas: int = Field(alias="totalAulasDadas")
    faltas: int = Field(alias="totalFaltas")
    frequencia: str = Field(alias="percentualFrequencia")
    creditos: int
    situacao: str = Field(alias="situacaoDisciplina")
    etapas: list[BoletimSemestreEtapas]
