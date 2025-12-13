"""Analytics - Schemas"""
from pydantic import BaseModel
class DashboardMetrics(BaseModel):
    total_employees: int
    active_employees: int
    pending_leave_requests: int
