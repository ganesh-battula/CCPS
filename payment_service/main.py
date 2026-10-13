import os
import pymysql
import jwt
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load the root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-ccps-jwt-secret-key-prod-2026-secure!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Ganesh@1234"),
        database=os.getenv("DB_NAME", "ccps_db"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

app = FastAPI(title="Payment Processing Service", version="1.0.0")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PaymentRequest(BaseModel):
    card_id: int
    amount: float = Field(..., gt=0, description="Amount must be positive")
    merchant_name: str = Field(..., min_length=1)

def verify_token(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header"
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Payment Processing Service"}

@app.post("/api/payments/process/", status_code=status.HTTP_201_CREATED)
def process_payment(payload: PaymentRequest, authorization: str = Header(None)):
    user_id = verify_token(authorization)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, card_type, last_four_digits FROM card_management_card WHERE id = %s AND user_id = %s",
                (payload.card_id, user_id)
            )
            card = cursor.fetchone()
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Card not found or does not belong to this user"
                )

            now = datetime.now()
            insert_query = """
                INSERT INTO transactions_transaction 
                (amount, currency, status, description, card_id, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_query,
                (payload.amount, "INR", "SUCCESS", f"Payment to {payload.merchant_name}", card["id"], user_id, now)
            )
            tx_id = cursor.lastrowid
            connection.commit()

            return {
                "transaction_id": tx_id,
                "amount": payload.amount,
                "currency": "INR",
                "merchant_name": payload.merchant_name,
                "card_last_four": card["last_four_digits"],
                "status": "SUCCESS",
                "message": "Payment processed successfully!"
            }
    finally:
        connection.close()

@app.get("/api/payments/history/", status_code=status.HTTP_200_OK)
def get_transaction_history(authorization: str = Header(None)):
    user_id = verify_token(authorization)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    t.id,
                    t.amount,
                    t.currency,
                    t.status,
                    t.description,
                    t.created_at,
                    c.card_type,
                    c.last_four_digits
                FROM transactions_transaction t
                JOIN card_management_card c ON t.card_id = c.id
                WHERE t.user_id = %s
                ORDER BY t.created_at DESC
            """
            cursor.execute(query, (user_id,))
            transactions = cursor.fetchall()

            for tx in transactions:
                if isinstance(tx.get("created_at"), datetime):
                    tx["created_at"] = tx["created_at"].isoformat()

            return {
                "count": len(transactions),
                "transactions": transactions
            }
    finally:
        connection.close()