"""Timesheets Module - Schemas"""
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
import uuid

class TimesheetCreate(BaseModel):
    period_start: date
    period_end: date

class TimesheetEntryCreate(BaseModel):
    project_id: uuid.UUID
    date: date
    hours: Decimal
    activity_description: str = None
