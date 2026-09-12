from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uuid
from datetime import datetime

# Initialize the API Application
app = FastAPI(title="DRC FinTech Engine API")

# SIMULATED CLOUD DATABASE (Multi-Tenant Ledger)
TENANT_DATABASE = {
    "KEY_KIN_RETAIL": {"company": "Kinshasa Mega Mart", "currency": "CDF", "ledger": []},
    "KEY_GOMA_COFFEE": {"company": "Kivu Premium Coffee", "currency": "USD", "ledger": []}
}

# Define the data structure for incoming mobile money webhooks
class MobileMoneyWebhook(BaseModel):
    amount: float
    sender_phone: str
    transaction_id: str = None

@app.post("/v1/payments/webhook")
async def receive_payment(payload: MobileMoneyWebhook, authorization: str = Header(None)):
    """
    This endpoint acts like an internet-facing payment gateway.
    It authenticates the tenant, checks security, and routes funds.
    """
    # 1. Security Check: Authenticate the client using the request header
    if not authorization or authorization not in TENANT_DATABASE:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Client API Key.")
    
    tenant_profile = TENANT_DATABASE[authorization]
    tx_id = payload.transaction_id or f"TX-{str(uuid.uuid4())[:8].upper()}"
    
    # 2. Process and write to isolated database partition
    record = {
        "timestamp": datetime.now().isoformat(),
        "tx_id": tx_id,
        "amount": payload.amount,
        "currency": tenant_profile["currency"],
        "sender": payload.sender_phone,
        "status": "SETTLED"
    }
    tenant_profile["ledger"].append(record)
    
    return {
        "status": "SUCCESS",
        "message": f"Successfully routed {payload.amount} {tenant_profile['currency']} to {tenant_profile['company']}",
        "internal_tx_id": tx_id
    }

@app.get("/v1/merchant/ledger")
async def get_ledger(authorization: str = Header(None)):
    """Secured portal allowing a single merchant to pull their private data."""
    if not authorization or authorization not in TENANT_DATABASE:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return TENANT_DATABASE[authorization]

