from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import smtplib
from email.message import EmailMessage
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime
import uuid
import os

from passlib.context import CryptContext
from dotenv import load_dotenv
load_dotenv()

# -------------------------------
# Password hashing setup
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ----------------------------
# App setup
# ----------------------------
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------
# Database setup
# ----------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)

# ----------------------------
# Models
# ----------------------------
class Review(SQLModel, table=True):
    __tablename__ = "review"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    rating: int
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Order(SQLModel, table=True):
    __tablename__ = "order"
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True, unique=True)
    product_name: str
    expected_amount: int
    customer_name: str
    customer_phone: str
    customer_address: str = Field(default="")
    payment_method: str = Field(default="UPI")
    transaction_id: str = Field(default="")
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: datetime | None = None

# ✅ FIXED: renamed table from "user" to "appuser" — "user" is reserved in PostgreSQL
class User(SQLModel, table=True):
    __tablename__ = "appuser"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

SQLModel.metadata.create_all(engine)

# ----------------------------
# Static page routes
# ----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/privacy-policy", response_class=HTMLResponse)
def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy-policy.html", {"request": request})

@app.get("/terms-of-service", response_class=HTMLResponse)
def terms_of_service(request: Request):
    return templates.TemplateResponse("terms-of-service.html", {"request": request})

@app.get("/flats", response_class=HTMLResponse)
def flats(request: Request):
    return templates.TemplateResponse("flats.html", {"request": request})

@app.get("/heels", response_class=HTMLResponse)
def heels(request: Request):
    return templates.TemplateResponse("heels.html", {"request": request})

@app.get("/wedges", response_class=HTMLResponse)
def wedges(request: Request):
    return templates.TemplateResponse("wedges.html", {"request": request})

@app.get("/bridal", response_class=HTMLResponse)
def bridal(request: Request):
    return templates.TemplateResponse("bridal.html", {"request": request})

@app.get("/shoes", response_class=HTMLResponse)
def shoes(request: Request):
    return templates.TemplateResponse("shoes.html", {"request": request})

@app.get("/casualwear", response_class=HTMLResponse)
async def casualwear(request: Request):
    return templates.TemplateResponse("casualwear.html", {"request": request})

@app.get("/pay", response_class=HTMLResponse)
async def pay_page(request: Request):
    return templates.TemplateResponse("pay.html", {"request": request})

# ----------------------------
# Save order
# ----------------------------
@app.post("/api/save-order")
async def save_order(request: Request):
    try:
        data = await request.json()
        with Session(engine) as session:
            order = Order(
                product_name=data.get("orderItems", "Multiple Items"),
                expected_amount=int(float(data.get("amount", 0))),
                customer_name=data.get("name", ""),
                customer_phone=data.get("phone", ""),
                customer_address=data.get("address", ""),
                payment_method=data.get("paymentMethod", "UPI"),
                transaction_id=data.get("transactionId", ""),
                status="pending"
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            return JSONResponse({"ok": True, "order_id": order.order_id})
    except Exception as e:
        print("Save order error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# ----------------------------
# Contact form
# ----------------------------
@app.post("/contact", response_class=HTMLResponse)
async def contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    gmail_user = os.getenv("GMAIL_USER", "farhanuddin0516@gmail.com")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "")

    msg = EmailMessage()
    msg["Subject"] = "New Contact Form Submission - Madam Choice"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.set_content(
        f"New message from Madam Choice Contact Form:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Message:\n{message}\n"
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_app_password)
            server.send_message(msg)
        success = True
    except Exception as e:
        print("Email sending failed:", e)
        success = False

    return templates.TemplateResponse("contact.html", {"request": request, "success": success})

# ----------------------------
# Reviews
# ----------------------------
@app.post("/reviews")
async def add_review(name: str = Form(...), rating: int = Form(...), text: str = Form(...)):
    with Session(engine) as session:
        review = Review(name=name, rating=rating, text=text)
        session.add(review)
        session.commit()
        session.refresh(review)
        return {"ok": True, "id": review.id}

@app.get("/reviews")
async def list_reviews():
    with Session(engine) as session:
        reviews = session.exec(select(Review).order_by(Review.created_at.desc())).all()
        return reviews

# ----------------------------
# Orders
# ----------------------------
@app.post("/orders")
async def create_order(
    product_name: str = Form(...),
    expected_amount: int = Form(...),
    customer_name: str = Form(...),
    customer_phone: str = Form(...)
):
    with Session(engine) as session:
        order = Order(
            product_name=product_name,
            expected_amount=expected_amount,
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return {"order_id": order.order_id, "status": order.status}

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.order_id == order_id)).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

# ----------------------------
# Coupon
# ----------------------------
@app.post("/apply-coupon")
async def apply_coupon(
    total_amount: float = Form(...),
    coupon: str = Form(...)
):
    coupon = coupon.strip().lower()
    discount = 0
    if coupon == "madamchoice10":
        if total_amount >= 900:
            discount = 0.10
        elif total_amount >= 500:
            discount = 0.08
        else:
            discount = 0.05

    discounted_total = round(total_amount - (total_amount * discount), 2)
    return {
        "original_total": total_amount,
        "discount_percent": int(discount * 100),
        "discounted_total": discounted_total
    }

# ----------------------------
# Signup & Login
# ----------------------------
@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        with Session(engine) as session:
            existing = session.exec(select(User).where(User.email == email)).first()
            if existing:
                return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered!"})
            user = User(name=name, email=email, password_hash=hash_password(password))
            session.add(user)
            session.commit()
            return templates.TemplateResponse("signup.html", {"request": request, "success": f"Account created for {name}! You can now log in."})
    except Exception as e:
        print("Signup error:", e)
        return templates.TemplateResponse("signup.html", {"request": request, "error": f"Something went wrong: {str(e)}"})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user or not verify_password(password, user.password_hash):
                return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password!"})
            # ✅ Redirect to homepage after successful login
            return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print("Login error:", e)
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Something went wrong: {str(e)}"})