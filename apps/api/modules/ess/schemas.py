"""ESS - Schemas"""
from pydantic import BaseModel
class ProfileUpdate(BaseModel):
    phone: str = None
    address: str = None
