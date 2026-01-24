from pydantic import BaseModel, Field


class Coeficiente(BaseModel):
    coeficiente_aluno: float = Field(alias="coeficienteRendimento")
    coeficiente_turma: float = Field(alias="coeficienteRendimentoTurma")
    maior_coeficiente_turma: float = Field(alias="maiorCoeficienteRendimentoTurma")
