from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True, unique=True)
    product_id: int
    product_name: str
    expected_amount: int  # rupees (or use paise consistently)
    customer_name: str
    customer_phone: str
    status: str = Field(default="pending")  # pending, paid, failed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: datetime | None = None

class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(index=True)
    gateway: str  # e.g., "razorpay", "phonepe"
    gateway_order_id: str | None = None
    gateway_payment_id: str | None = None
    amount: int
    currency: str = "INR"
    status: str = "created"  # created, success, failed
    signature_valid: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    rating: int
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 🔹 New User model for login/signup
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)