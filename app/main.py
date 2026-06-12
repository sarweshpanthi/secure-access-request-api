from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.auth import authenticate_user, create_access_token, get_current_user
from app.risk_engine import evaluate_access_request


app = FastAPI(
    title="Secure Access Request API",
    description="A lightweight API that evaluates access requests using least-privilege rules.",
    version="1.0.0"
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AccessRequest(BaseModel):
    system: str
    role: str
    justification: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/login")
def login(request: LoginRequest):
    is_valid_user = authenticate_user(
        email=str(request.email),
        password=request.password
    )

    if not is_valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(str(request.email))

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/access-request")
def submit_access_request(
    request: AccessRequest,
    current_user: str = Depends(get_current_user)
):
    evaluation = evaluate_access_request(
        role=request.role,
        justification=request.justification
    )

    return {
        "requested_by": current_user,
        "system": request.system,
        "role": request.role,
        "evaluation": evaluation
    }