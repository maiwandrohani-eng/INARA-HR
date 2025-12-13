"""Grievance - Schemas"""
from pydantic import BaseModel
class GrievanceCreate(BaseModel):
    grievance_type: str
    description: str
