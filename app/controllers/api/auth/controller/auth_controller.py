import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.analytics.analytics_service import login

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    telephone: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    type_user: str
    nom: str
    prenom: str


@auth_router.post("/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest):
    try:
        result = login(payload.telephone, payload.password)
        return result
    except ValueError as e:
        raise HTTPException(401, str(e))
