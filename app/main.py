from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from app.risk_engine import evaluate_access_request


app = FastAPI(
    title="Secure Access Request API",
    description="A lightweight API that evaluates access requests using least-privilege rules.",
    version="1.0.0"
)


class AccessRequest(BaseModel):
    user: EmailStr
    system: str
    role: str
    justification: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/access-request")
def submit_access_request(request: AccessRequest):
    evaluation = evaluate_access_request(
        role=request.role,
        justification=request.justification
    )

    return {
        "user": request.user,
        "system": request.system,
        "role": request.role,
        "evaluation": evaluation
    }