from pydantic import BaseModel, Field


class Disciplina(BaseModel):
    id: int = Field(alias="idDisciplina")
    id_habilitacao: int = Field(alias="idHabilitacao")
    habilitacao: str
    disciplina: str
    numero_periodo: int = Field(alias="numeroPeriodo")
    carga_horaria: int = Field(alias="cargaHoraria")
    carga_horaria_pratica_profissional: int = Field(
        alias="cargaHorariaPraticaProfissional"
    )
    credito: int
    sigla: str
    credito_requisito: int = Field(alias="creditoRequisito")
    optativa: bool
    tipo: int
    pre_requisitos_lista: list[str] = Field(alias="preRequisitosLista")
    pre_requisitos: str = Field(alias="preRequisitos")
    co_requisitos_lista: list[str] = Field(alias="coRequisitosLista")
    co_requisitos: str = Field(alias="coRequisitos")
