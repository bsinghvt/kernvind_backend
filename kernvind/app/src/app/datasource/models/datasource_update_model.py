from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class DataSourceUpdate(BaseModel):
    datasource_id: int
    datasource_description: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=1024)
