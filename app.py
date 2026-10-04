from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from human_engine import run_human_engine
from anti_engine import run_anti_engine
from orchestrator import run_self_correcting_engine
from ast_verifier import verify_constraints_and_logic, FORBIDDEN_NODE_MAP
import orchestrator

app = FastAPI(
    title="HumaniX Enterprise Verification Gateway",
    description="Secure SaaS Verification & Dynamic Engine Router Service",
    version="2.0.0"
)

# Enterprise API Key configuration
API_KEY_NAME = "X-API-Key"
# In production, this would be loaded securely from a database or environment variable
VALID_API_KEYS = {"humanix-enterprise-secret-key-2026"}

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing Enterprise API Key. Access denied."
    )

class VerificationRequest(BaseModel):
    task: str
    constraint: str
    blocked_nodes: Optional[List[str]] = []
    test_assertion: Optional[str] = None

class VerificationResponse(BaseModel):
    status: str
    winning_engine: Optional[str]
    human_score: float
    anti_score: float
    verified_code: Optional[str]

@app.post("/verify", response_model=VerificationResponse)
def verify_code(req: VerificationRequest, api_key: str = Security(verify_api_key)):
    invalid_nodes = [node for node in req.blocked_nodes if node not in FORBIDDEN_NODE_MAP]
    if invalid_nodes:
        raise HTTPException(status_code=400, detail=f"Invalid nodes: {invalid_nodes}")

    def custom_verifier(response):
        return verify_constraints_and_logic(
            response, 
            forbidden_keys=req.blocked_nodes,
            test_assertion=req.test_assertion
        )

    orchestrator.verify_constraints_and_logic = custom_verifier

    h_code, h_score = run_self_correcting_engine(run_human_engine, req.task, req.constraint, "HUMAN ENGINE")
    a_code, a_score = run_self_correcting_engine(run_anti_engine, req.task, req.constraint, "ANTI ENGINE")

    winning_code = h_code if h_score == 1.0 else a_code if a_score == 1.0 else None
    winning_engine = "HUMAN ENGINE" if h_score == 1.0 else "ANTI-INTELLIGENCE ENGINE" if a_score == 1.0 else None

    return VerificationResponse(
        status="SUCCESS" if winning_code else "FAILED",
        winning_engine=winning_engine,
        human_score=h_score,
        anti_score=a_score,
        verified_code=winning_code
    )

@app.get("/")
def health_check():
    return {"service": "HumaniX Enterprise Engine", "status": "ONLINE", "security": "ACTIVE"}