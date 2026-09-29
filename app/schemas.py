from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class BusinessCreate(BaseModel):
    name: str
    loyalty_type: str = "stamps"  # "stamps" (sellos) o "points" (puntos)
    primary_color: str = "#10b981"

class BusinessResponse(BaseModel):
    id: int
    name: str
    loyalty_type: str
    primary_color: str
    is_active: bool

    class Config:
        from_attributes = True

class EmployeeCreate(BaseModel):
    business_id: int
    name: str
    pin_hash: str = "1234"

class EmployeeResponse(BaseModel):
    id: int
    business_id: int
    name: str

    class Config:
        from_attributes = True

class EmployeeLoginRequest(BaseModel):
    business_id: int
    name: str
    pin_hash: str

class EmployeeLoginResponse(BaseModel):
    employee_id: int
    name: str
    business_id: int
    business_name: str
    loyalty_type: str
    primary_color: str
    message: str

class CustomerCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionRequest(BaseModel):
    customer_id: str
    employee_id: int
    employee_pin: str
    amount_or_units: float = 1.0  # Si es sellos suele ser 1, si es puntos es el valor o monto

class RedemptionRequest(BaseModel):
    customer_id: str
    employee_id: int
    employee_pin: str
    units_to_redeem: float