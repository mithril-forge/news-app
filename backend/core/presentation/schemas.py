from core.models import BaseModel


class PickGenerationResponse(BaseModel):
    hash: str
    message: str
