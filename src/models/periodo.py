from pydantic import BaseModel, Field


class PeriodoLetivo(BaseModel):
    ano: int = Field(alias="anoLetivo")
    periodo: int = Field(alias="periodoLetivo")
    descricao: str
