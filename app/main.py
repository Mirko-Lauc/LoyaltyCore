from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.database import get_db, engine, Base
from app.models import Business, Employee, Customer, Wallet, Transaction, Reward
from app.schemas import (
    BusinessCreate, BusinessResponse,
    EmployeeCreate, EmployeeResponse,
    EmployeeLoginRequest, EmployeeLoginResponse,
    CustomerCreate, CustomerResponse,
    TransactionRequest, RedemptionRequest
)

app = FastAPI(title="LoyaltyCore Enterprise Demo", version="3.0.0", debug=True)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Recrea tablas si faltan
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear datos base automáticamente si la tabla de negocios está vacía
    async with engine.connect() as conn:
        async_session = AsyncSession(conn)
        async with async_session as session:
            result = await session.execute(select(Business).where(Business.id == 1))
            biz = result.scalars().first()
            if not biz:
                default_biz = Business(
                    id=1,
                    name="Peluquería Estilo VIP",
                    loyalty_type="stamps",
                    primary_color="#10b981",
                    instagram_url="https://instagram.com/peluqueriaestilovip",
                    phone_number="+54 9 351 987 6543",
                    address="Av. Colón 450, Córdoba",
                    is_active=True
                )
                session.add(default_biz)
                
                default_emp = Employee(
                    business_id=1,
                    name="Carlos",
                    pin_hash="1234"
                )
                session.add(default_emp)
                
                r1 = Reward(business_id=1, title="Corte de Cabello Tradicional", cost_units=5)
                r2 = Reward(business_id=1, title="Perfilado de Barba + Lavado", cost_units=3)
                session.add_all([r1, r2])
                
                await session.commit()

@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")

# --- ESQUEMAS AUTH Y PREMIOS ---
class CustomerRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class CustomerLoginRequest(BaseModel):
    email: EmailStr
    password: str

class RewardCreateRequest(BaseModel):
    title: str
    cost_units: float

# --- AUTH CLIENTE (LOGIN / REGISTRO) ---
@app.post("/client-auth/register", status_code=status.HTTP_201_CREATED)
async def register_client(data: CustomerRegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Customer).where(Customer.email == data.email))).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Este correo ya se encuentra registrado.")

    new_cust = Customer(
        email=data.email,
        name=data.name or data.email.split("@")[0],
        password=data.password
    )
    db.add(new_cust)
    await db.commit()
    await db.refresh(new_cust)

    # Billetera para el comercio ID 1
    wallet = Wallet(customer_id=new_cust.id, business_id=1, balance=0.0)
    db.add(wallet)
    await db.commit()

    return {
        "status": "success",
        "customer_id": new_cust.id,
        "name": new_cust.name,
        "message": "Cuenta registrada correctamente."
    }

@app.post("/client-auth/login")
async def login_client(data: CustomerLoginRequest, db: AsyncSession = Depends(get_db)):
    cust = (await db.execute(select(Customer).where(Customer.email == data.email))).scalars().first()
    if not cust or cust.password != data.password:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    return {
        "status": "success",
        "customer_id": cust.id,
        "name": cust.name,
        "message": "Login exitoso."
    }

@app.get("/client-portal/{business_id}/{customer_id}")
async def get_client_portal_data(business_id: int, customer_id: str, db: AsyncSession = Depends(get_db)):
    biz = (await db.execute(select(Business).where(Business.id == business_id))).scalars().first()
    if not biz or not biz.is_active:
        raise HTTPException(status_code=404, detail="Comercio no encontrado.")

    # Si se pasa un dummy o id de prueba, busca todos los premios
    cust = None
    if customer_id != "dummy":
        cust = (await db.execute(select(Customer).where(Customer.id == customer_id))).scalars().first()

    balance = 0.0
    if cust:
        wallet = (await db.execute(
            select(Wallet).where(Wallet.customer_id == customer_id, Wallet.business_id == business_id)
        )).scalars().first()
        
        if not wallet:
            wallet = Wallet(customer_id=customer_id, business_id=business_id, balance=0.0)
            db.add(wallet)
            await db.commit()
        balance = wallet.balance

    rewards = (await db.execute(select(Reward).where(Reward.business_id == business_id))).scalars().all()
    rewards_list = [{"id": r.id, "title": r.title, "cost_units": r.cost_units} for r in rewards]

    return {
        "business": {
            "name": biz.name,
            "loyalty_type": biz.loyalty_type,
            "primary_color": biz.primary_color,
            "instagram_url": biz.instagram_url,
            "phone_number": biz.phone_number,
            "address": biz.address
        },
        "customer": {
            "id": cust.id if cust else "",
            "name": cust.name if cust else "Invitado",
            "email": cust.email if cust else ""
        },
        "balance": balance,
        "rewards": rewards_list
    }

# --- GESTIÓN DE PREMIOS DEL DUEÑO ---
@app.post("/businesses/{business_id}/rewards", status_code=status.HTTP_201_CREATED)
async def create_reward(business_id: int, reward_data: RewardCreateRequest, db: AsyncSession = Depends(get_db)):
    biz = (await db.execute(select(Business).where(Business.id == business_id))).scalars().first()
    if not biz:
        raise HTTPException(status_code=404, detail="Comercio no encontrado.")

    new_reward = Reward(
        business_id=business_id,
        title=reward_data.title,
        cost_units=reward_data.cost_units
    )
    db.add(new_reward)
    await db.commit()
    await db.refresh(new_reward)

    return {
        "status": "success",
        "message": "Premio agregado con éxito al catálogo",
        "reward": {
            "id": new_reward.id,
            "title": new_reward.title,
            "cost_units": new_reward.cost_units
        }
    }

@app.delete("/businesses/{business_id}/rewards/{reward_id}")
async def delete_reward(business_id: int, reward_id: int, db: AsyncSession = Depends(get_db)):
    reward = (await db.execute(
        select(Reward).where(Reward.id == reward_id, Reward.business_id == business_id)
    )).scalars().first()

    if not reward:
        raise HTTPException(status_code=404, detail="Premio no encontrado en este local.")

    await db.delete(reward)
    await db.commit()

    return {
        "status": "success",
        "message": "Premio eliminado correctamente del catálogo"
    }

# --- LOGIN EMPLEADO ---
@app.post("/employee-login/", response_model=EmployeeLoginResponse)
async def employee_login(login_data: EmployeeLoginRequest, db: AsyncSession = Depends(get_db)):
    query = (
        select(Employee, Business)
        .join(Business, Employee.business_id == Business.id)
        .where(Employee.business_id == login_data.business_id)
        .where(Employee.name == login_data.name)
    )
    result = (await db.execute(query)).first()

    if not result:
        raise HTTPException(status_code=401, detail="Empleado no encontrado.")

    employee, business = result
    if employee.pin_hash != login_data.pin_hash:
        raise HTTPException(status_code=401, detail="PIN de seguridad incorrecto.")

    return {
        "employee_id": employee.id,
        "name": employee.name,
        "business_id": business.id,
        "business_name": business.name,
        "loyalty_type": business.loyalty_type,
        "primary_color": business.primary_color,
        "message": "Login exitoso"
    }

# --- OPERACIONES CAJA ---
@app.post("/transactions/earn", status_code=status.HTTP_201_CREATED)
async def earn_units(tx_data: TransactionRequest, db: AsyncSession = Depends(get_db)):
    emp_query = (
        select(Employee, Business)
        .join(Business, Employee.business_id == Business.id)
        .where(Employee.id == tx_data.employee_id)
    )
    res = (await db.execute(emp_query)).first()
    if not res:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")

    employee, business = res
    if employee.pin_hash != tx_data.employee_pin:
        raise HTTPException(status_code=401, detail="PIN incorrecto.")

    customer = (await db.execute(select(Customer).where(Customer.id == tx_data.customer_id))).scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado con ese código QR.")

    wallet = (await db.execute(
        select(Wallet).where(Wallet.customer_id == customer.id, Wallet.business_id == business.id)
    )).scalars().first()

    if not wallet:
        wallet = Wallet(customer_id=customer.id, business_id=business.id, balance=0.0)
        db.add(wallet)
        await db.flush()

    added_amount = 1.0 if business.loyalty_type == "stamps" else tx_data.amount_or_units
    wallet.balance += added_amount

    new_tx = Transaction(wallet_id=wallet.id, employee_id=employee.id, units_changed=added_amount)
    db.add(new_tx)
    await db.commit()

    return {
        "status": "success",
        "message": f"{'Sello otorgado' if business.loyalty_type == 'stamps' else 'Puntos sumados'} correctamente",
        "new_balance": wallet.balance
    }

@app.post("/transactions/redeem", status_code=status.HTTP_201_CREATED)
async def redeem_units(red_data: RedemptionRequest, db: AsyncSession = Depends(get_db)):
    emp_query = (
        select(Employee, Business)
        .join(Business, Employee.business_id == Business.id)
        .where(Employee.id == red_data.employee_id)
    )
    res = (await db.execute(emp_query)).first()
    if not res:
        raise HTTPException(status_code=404, detail="Empleado no encontrado.")

    employee, business = res
    if employee.pin_hash != red_data.employee_pin:
        raise HTTPException(status_code=401, detail="PIN incorrecto.")

    wallet = (await db.execute(
        select(Wallet).where(Wallet.customer_id == red_data.customer_id, Wallet.business_id == business.id)
    )).scalars().first()

    if not wallet or wallet.balance < red_data.units_to_redeem:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para realizar el canje.")

    wallet.balance -= red_data.units_to_redeem

    new_tx = Transaction(wallet_id=wallet.id, employee_id=employee.id, units_changed=-red_data.units_to_redeem)
    db.add(new_tx)
    await db.commit()

    return {
        "status": "success",
        "message": "Canje realizado con éxito",
        "remaining_balance": wallet.balance
    }

# --- AUDITORÍA DUEÑO ---
@app.get("/businesses/{business_id}/audit-log")
async def get_business_audit_log(business_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Transaction, Employee, Customer)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .join(Employee, Transaction.employee_id == Employee.id)
        .join(Customer, Wallet.customer_id == Customer.id)
        .where(Wallet.business_id == business_id)
        .order_by(Transaction.created_at.desc())
    )
    result = (await db.execute(query)).all()

    audit_logs = []
    for tx, emp, cust in result:
        audit_logs.append({
            "transaction_id": tx.id,
            "employee_name": emp.name,
            "customer_email": cust.email,
            "units_changed": tx.units_changed,
            "operation_type": "Acumulación" if tx.units_changed > 0 else "Canje",
            "timestamp": tx.created_at.isoformat()
        })

    return {"status": "success", "total_operations": len(audit_logs), "logs": audit_logs}

# --- CAMPAÑA CRM ---
@app.post("/businesses/{business_id}/crm/rescue-campaign")
async def rescue_inactive_customers(business_id: int, db: AsyncSession = Depends(get_db)):
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    query = select(Customer, Wallet).join(Wallet, Customer.id == Wallet.customer_id).where(Wallet.business_id == business_id)
    result = (await db.execute(query)).all()

    rescued_count = 0
    campaign_log = []

    for customer, wallet in result:
        tx_query = select(Transaction).where(Transaction.wallet_id == wallet.id).order_by(Transaction.created_at.desc())
        last_tx = (await db.execute(tx_query)).scalars().first()

        is_inactive = False
        if last_tx:
            if last_tx.created_at < fourteen_days_ago:
                is_inactive = True
        else:
            is_inactive = True

        if is_inactive:
            rescued_count += 1
            campaign_log.append({
                "to": customer.email,
                "subject": "¡Te extrañamos! Vuelve con un 10% de descuento"
            })

    return {
        "status": "success",
        "message": f"Campaña ejecutada. Se enviaron {rescued_count} correos de rescate.",
        "simulated_emails": campaign_log
    }