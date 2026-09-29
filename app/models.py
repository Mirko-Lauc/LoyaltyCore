from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    loyalty_type = Column(String(20), default="stamps")  # "stamps" o "points"
    primary_color = Column(String(7), default="#10b981")
    is_active = Column(Boolean, default=True)
    
    # NUEVOS CAMPOS DE CONTACTO PARA EL CLIENTE
    instagram_url = Column(String(255), nullable=True, default="https://instagram.com")
    phone_number = Column(String(50), nullable=True, default="+54 9 351 000 0000")
    address = Column(String(255), nullable=True, default="Av. Principal 123, Córdoba")

    employees = relationship("Employee", back_populates="business", cascade="all, delete-orphan")
    wallets = relationship("Wallet", back_populates="business", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="business", cascade="all, delete-orphan")

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    title = Column(String(150), nullable=False)
    cost_units = Column(Float, nullable=False)  # Cuántos sellos o puntos cuesta

    business = relationship("Business", back_populates="rewards")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    pin_hash = Column(String(4), nullable=False)  # PIN de 4 dígitos

    business = relationship("Business", back_populates="employees")
    transactions = relationship("Transaction", back_populates="employee")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(150), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    password = Column(String(100), nullable=False, default="123456")  # Contraseña del cliente
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    wallets = relationship("Wallet", back_populates="customer", cascade="all, delete-orphan")
    
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    balance = Column(Float, default=0.0)

    customer = relationship("Customer", back_populates="wallets")
    business = relationship("Business", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    units_changed = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    wallet = relationship("Wallet", back_populates="transactions")
    employee = relationship("Employee", back_populates="transactions")