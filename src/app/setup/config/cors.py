from pydantic import BaseModel, Field


class CorsSettings(BaseModel):
    origins: list[str] = Field(alias="ORIGINS")
