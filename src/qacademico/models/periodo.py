from pydantic import BaseModel, Field, ConfigDict


class PeriodoLetivo(BaseModel):
    ano: int = Field(alias="anoLetivo")
    periodo: int = Field(alias="periodoLetivo")
    descricao: str | None = Field(default=None, exclude=True)
    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)
