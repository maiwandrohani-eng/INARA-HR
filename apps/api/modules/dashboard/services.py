"""
Dashboard Module - Service Layer
Business logic for dashboard data aggregation
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

from modules.employees.models import Employee
from modules.auth.models import User
from modules.approvals.services import ApprovalService


class DashboardService:
    """Service for dashboard operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_service = ApprovalService(db)
    
    async def check_if_supervisor(self, user_id: uuid.UUID) -> bool:
        """
        Check if user has any direct reports (is a supervisor)
        """
        # Get employee record from user_id
        result = await self.db.execute(
            select(Employee).where(Employee.user_id == user_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            return False
        
        # Check if this employee has any direct reports
        result = await self.db.execute(
            select(func.count(Employee.id)).where(Employee.manager_id == employee.id)
        )
        count = result.scalar_one()
        
        return count > 0
    
    async def get_employee_dashboard(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get employee personal dashboard data
        """
        # Get employee record
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.position),
                selectinload(Employee.department)
            )
            .where(Employee.user_id == user_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            return self._get_empty_employee_dashboard()
        
        # Try to get approval stats, but handle errors gracefully
        try:
            approval_stats = await self.approval_service.get_approval_stats(employee.id)
            approvals_data = {
                "total_pending": approval_stats.total_pending,
                "leave_pending": approval_stats.leave_pending,
                "travel_pending": approval_stats.travel_pending,
                "timesheet_pending": approval_stats.timesheet_pending,
                "performance_pending": approval_stats.performance_pending
            }
        except Exception as e:
            # If approval service fails, return zeros
            approvals_data = {
                "total_pending": 0,
                "leave_pending": 0,
                "travel_pending": 0,
                "timesheet_pending": 0,
                "performance_pending": 0
            }
        
        return {
            "employee": {
                "id": str(employee.id),
                "name": f"{employee.first_name} {employee.last_name}",
                "position": employee.position.title if employee.position else "N/A",
                "department": employee.department.name if employee.department else "N/A",
                "employee_number": employee.employee_number
            },
            "leaveBalance": {
                "annual": 15,
                "sick": 10,
                "total": 25
            },
            "recentLeaveRequests": [],
            "recentTravelRequests": [],
            "recentPayslips": [],
            "attendance": {
                "present": 20,
                "absent": 1,
                "late": 2,
                "total": 23
            },
            "grievances": {
                "total": 0,
                "resolved": 0,
                "pending": 0
            },
            "performance": {
                "lastReviewDate": None,
                "rating": "N/A",
                "nextReviewDate": None
            },
            "approvals": approvals_data
        }
    
    async def get_supervisor_dashboard(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get supervisor dashboard with team data and pending approvals
        """
        # Get supervisor's employee record
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.position))
            .where(Employee.user_id == user_id)
        )
        supervisor = result.scalar_one_or_none()
        
        if not supervisor:
            return self._get_empty_supervisor_dashboard()
        
        # Get team members (direct reports)
        result = await self.db.execute(
            select(Employee)
            .options(selectinload(Employee.position))
            .where(Employee.manager_id == supervisor.id)
        )
        team_members = result.scalars().all()
        
        team_data = []
        for member in team_members:
            team_data.append({
                "id": str(member.id),
                "name": f"{member.first_name} {member.last_name}",
                "position": member.position.title if member.position else "N/A",
                "attendance_rate": 95,
                "leave_balance": 20,
                "status": member.status.value
            })
        
        active_members = sum(1 for m in team_members if m.status.value == "active")
        on_leave = sum(1 for m in team_members if m.status.value == "on_leave")
        
        # Get approval statistics
        approval_stats = await self.approval_service.get_approval_stats(supervisor.id)
        
        # Get pending approval requests
        pending_approvals = await self.approval_service.get_pending_approvals(supervisor.id)
        
        return {
            "supervisor": {
                "id": str(supervisor.id),
                "name": f"{supervisor.first_name} {supervisor.last_name}",
                "position": supervisor.position.title if supervisor.position else "Supervisor",
                "team_size": len(team_members)
            },
            "approvalStats": {
                "total_pending": approval_stats.total_pending,
                "leave_pending": approval_stats.leave_pending,
                "travel_pending": approval_stats.travel_pending,
                "timesheet_pending": approval_stats.timesheet_pending,
                "performance_pending": approval_stats.performance_pending
            },
            "pendingApprovals": [
                {
                    "id": str(approval.id),
                    "type": approval.request_type.value,
                    "employee_id": str(approval.employee_id),
                    "submitted_at": approval.submitted_at.isoformat(),
                    "comments": approval.comments
                }
                for approval in pending_approvals[:10]  # Show latest 10
            ],
            "teamMembers": team_data,
            "teamStats": {
                "totalMembers": len(team_members),
                "activeMembers": active_members,
                "onLeave": on_leave,
                "avgAttendance": 92
            },
            "complianceItems": {
                "pending": 0,
                "overdue": 0
            }
        }
    
    def _get_empty_employee_dashboard(self) -> Dict[str, Any]:
        """Return empty employee dashboard structure"""
        return {
            "employee": {
                "id": "",
                "name": "Unknown",
                "position": "N/A",
                "department": "N/A",
                "employee_number": "N/A"
            },
            "leaveBalance": {"annual": 0, "sick": 0, "total": 0},
            "recentLeaveRequests": [],
            "recentTravelRequests": [],
            "recentPayslips": [],
            "attendance": {"present": 0, "absent": 0, "late": 0, "total": 0},
            "grievances": {"total": 0, "resolved": 0, "pending": 0},
            "performance": {"lastReviewDate": None, "rating": "N/A", "nextReviewDate": None},
            "approvals": None
        }
    
    def _get_empty_supervisor_dashboard(self) -> Dict[str, Any]:
        """Return empty supervisor dashboard structure"""
        return {
            "supervisor": {"id": "", "name": "Unknown", "position": "N/A", "team_size": 0},
            "approvalStats": {
                "total_pending": 0,
                "leave_pending": 0,
                "travel_pending": 0,
                "timesheet_pending": 0,
                "performance_pending": 0
            },
            "pendingApprovals": [],
            "teamMembers": [],
            "teamStats": {"totalMembers": 0, "activeMembers": 0, "onLeave": 0, "avgAttendance": 0},
            "complianceItems": {"pending": 0, "overdue": 0}
        }
