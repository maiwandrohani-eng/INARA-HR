"""Compensation - Schemas"""
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
import uuid
class SalaryAdjustmentCreate(BaseModel):
    employee_id: uuid.UUID
    effective_date: date
    salary: Decimal
