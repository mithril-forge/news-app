from pydantic import BaseModel, EmailStr


class PickGenerationResponse(BaseModel):
    hash: str
    message: str


class AccountDeletionRequest(BaseModel):
    """Request model for account deletion"""

    email: EmailStr


class AccountDeletionExecuteRequest(BaseModel):
    """Request model for executing account deletion"""

    token: str


class AccountDeletionResponse(BaseModel):
    """Response model for deletion operations"""

    message: str
