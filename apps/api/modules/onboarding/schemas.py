"""Onboarding - Schemas"""
from pydantic import BaseModel
class OnboardingTaskCreate(BaseModel):
    task_name: str
