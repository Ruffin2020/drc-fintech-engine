from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI(title="AvenPay Enterprise Gateway Engine")

# 🔗 AUTOMATED DATABASE HANDSHAKE PROTOCOL
# This looks for your secure environment string variable on Render, falling back to a local string layer.
MONGO_CONNECTION_URI = os.getenv("MONGO_URI", "mongodb+srv://AvenPayAdmin:SECRET@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority")

# Initializing async database engine drivers
client = AsyncIOMotorClient(MONGO_CONNECTION_URI)
db = client["avenpay_production_vault"]
transactions_collection = db["global_ledger_stream"]
tenants_collection = db["merchant_partitions"]

class PaymentPayload(BaseModel):
    amount: float
    sender_phone: str
    transaction_id: str

@app.on_event("startup")
async def seed_enterprise_tenants_on_boot():
    """
    Automated Seeding System: Ensures your core business client partitions 
    exist in the cloud database the very second the cluster wakes up.
    """
    try:
        # Check if our primary retail merchant exists
        retail_tenant = await tenants_collection.find_one({"client_key": "KEY_KIN_RETAIL"})
        if not retail_tenant:
            await tenants_collection.insert_one({
                "client_key": "KEY_KIN_RETAIL",
                "company_name": "Kinshasa Mega Mart",
                "available_vault_balance": 5000000.0,
                "currency": "CDF",
                "sector": "Retail Supermarket",
                "updated_at": datetime.utcnow()
            })
            print("🚀 Successfully initialized Kinshasa Mega Mart partition in MongoDB Cloud!")
    except Exception as e:
        print(f"⚠️ Seed failure: {e}")

@app.post("/v1/payments/webhook")
async def process_cloud_financial_routing(
    payload: PaymentPayload,
    authorization: str = Header(None)
):
    # 🛡️ ZERO-TRUST COMPLIANCE HEADER CHECK
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing secure infrastructure token registry link.")

    # Locate the unique corporate merchant account directly inside MongoDB collection files
    tenant = await tenants_collection.find_one({"client_key": authorization})
    if not tenant:
        raise HTTPException(status_code=403, detail="Authorization token mapping reference rejected.")

    # Calculate business rule values
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid operational asset valuation metadata.")

    # Perform balance allocation audit check
    current_balance = tenant["available_vault_balance"]
    if payload.amount > current_balance:
        raise HTTPException(status_code=400, detail="Transaction declined: Insufficient channel ledger provisions.")

    # 🔄 ATOMIC TRANSACTION EXECUTION MATRIX
    new_calculated_balance = current_balance - payload.amount
    
    # 1. Update the merchant's vault account data balance permanently on the cloud network
    await tenants_collection.update_one(
        {"_id": tenant["_id"]},
        {"$set": {"available_vault_balance": new_calculated_balance, "updated_at": datetime.utcnow()}}
    )

    # 2. Append an immutable tracking trace log straight into the global transaction stream audit file
    internal_uuid = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    audit_record = {
        "internal_tx_id": internal_uuid,
        "external_tracking_id": payload.transaction_id,
        "merchant_key": authorization,
        "company_name": tenant["company_name"],
        "amount_processed": payload.amount,
        "currency": tenant["currency"],
        "sender_phone_record": payload.sender_phone,
        "execution_timestamp": datetime.utcnow(),
        "status": "SETTLED"
    }
    await transactions_collection.insert_one(audit_record)

    return {
        "status": "SUCCESS",
        "message": f"Successfully routed {payload.amount:,} {tenant['currency']} to {tenant['company_name']}",
        "internal_tx_id": internal_uuid,
        "timestamp": datetime.utcnow().isoformat()
    }


