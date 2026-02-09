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
import asyncio
import logging

from modules.employees.models import Employee
from modules.auth.models import User
from modules.approvals.services import ApprovalService
from core.cache import cache, build_dashboard_key, invalidate_cache

logger = logging.getLogger(__name__)


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
        Get employee personal dashboard data with caching and parallel queries
        """
        # Check cache first (5 minute TTL)
        cache_key = build_dashboard_key(str(user_id), "employee")
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache hit for dashboard: {cache_key}")
            return cached_data
        
        try:
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
            
            # Extract employee data before any potential transaction issues
            employee_id = employee.id
            employee_first_name = employee.first_name
            employee_last_name = employee.last_name
            employee_number = employee.employee_number
            employee_position = employee.position.title if employee.position else "N/A"
            employee_department = employee.department.name if employee.department else "N/A"
            
            # Parallelize all independent queries for better performance
            # Run all data fetching queries concurrently
            try:
                approval_stats_task = self.approval_service.get_approval_stats(employee_id)
                payslips_task = self._get_employee_payslips(employee_id)
                leave_requests_task = self._get_employee_leave_requests(employee_id)
                travel_requests_task = self._get_employee_travel_requests(employee_id)
                grievance_stats_task = self._get_employee_grievances(employee_id)
                leave_balance_task = self._get_employee_leave_balance(employee_id)
                
                # Wait for all queries to complete in parallel
                results = await asyncio.gather(
                    approval_stats_task,
                    payslips_task,
                    leave_requests_task,
                    travel_requests_task,
                    grievance_stats_task,
                    leave_balance_task,
                    return_exceptions=True
                )
                
                # Handle approval stats (first result)
                if isinstance(results[0], Exception):
                    logger.warning(f"Error fetching approval stats: {results[0]}")
                    approvals_data = {
                        "total_pending": 0,
                        "leave_pending": 0,
                        "travel_pending": 0,
                        "timesheet_pending": 0,
                        "performance_pending": 0
                    }
                else:
                    approval_stats = results[0]
                    approvals_data = {
                        "total_pending": approval_stats.total_pending,
                        "leave_pending": approval_stats.leave_pending,
                        "travel_pending": approval_stats.travel_pending,
                        "timesheet_pending": approval_stats.timesheet_pending,
                        "performance_pending": approval_stats.performance_pending
                    }
                
                # Extract other results (handle exceptions gracefully)
                recent_payslips = results[1] if not isinstance(results[1], Exception) else []
                recent_leave_requests = results[2] if not isinstance(results[2], Exception) else []
                recent_travel_requests = results[3] if not isinstance(results[3], Exception) else []
                grievance_stats = results[4] if not isinstance(results[4], Exception) else {"total": 0, "resolved": 0, "pending": 0}
                leave_balance = results[5] if not isinstance(results[5], Exception) else {"annual": 0, "sick": 0, "total": 0}
                
            except Exception as e:
                logger.error(f"Error in parallel queries: {e}")
                # Fallback to empty data if parallel queries fail
                approvals_data = {
                    "total_pending": 0,
                    "leave_pending": 0,
                    "travel_pending": 0,
                    "timesheet_pending": 0,
                    "performance_pending": 0
                }
                recent_payslips = []
                recent_leave_requests = []
                recent_travel_requests = []
                grievance_stats = {"total": 0, "resolved": 0, "pending": 0}
                leave_balance = {"annual": 0, "sick": 0, "total": 0}
            
            dashboard_data = {
                "employee": {
                    "id": str(employee_id),
                    "name": f"{employee_first_name} {employee_last_name}",
                    "position": employee_position,
                    "department": employee_department,
                    "employee_number": employee_number
                },
                "leaveBalance": leave_balance,
                "recentLeaveRequests": recent_leave_requests,
                "recentTravelRequests": recent_travel_requests,
                "recentPayslips": recent_payslips,
                "attendance": {
                    "present": 20,
                    "absent": 1,
                    "late": 2,
                    "total": 23
                },
                "grievances": grievance_stats,
                "performance": {
                    "lastReviewDate": None,
                    "rating": "N/A",
                    "nextReviewDate": None
                },
                "approvals": approvals_data
            }
            
            # Cache the result for 5 minutes (300 seconds)
            cache.set(cache_key, dashboard_data, ttl=300)
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Error in get_employee_dashboard: {e}")
            # Rollback on error
            await self.db.rollback()
            return self._get_empty_employee_dashboard()
    
    async def _get_employee_payslips(self, employee_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get recent approved/processed payslips for an employee"""
        try:
            from modules.payroll.models import Payroll, PayrollEntry, PayrollStatus
            
            # Get payroll entries for this employee from approved/processed payrolls
            result = await self.db.execute(
                select(PayrollEntry, Payroll)
                .join(Payroll, PayrollEntry.payroll_id == Payroll.id)
                .where(
                    and_(
                        PayrollEntry.employee_id == employee_id,
                        Payroll.status.in_([PayrollStatus.APPROVED, PayrollStatus.PROCESSED]),
                        Payroll.is_deleted == False
                    )
                )
                .order_by(Payroll.year.desc(), Payroll.month.desc())
                .limit(5)
            )
            entries_with_payroll = result.all()
            
            payslips = []
            for entry, payroll in entries_with_payroll:
                payslips.append({
                    "id": str(entry.id),
                    "payroll_id": str(payroll.id),
                    "period": f"{payroll.year}-{payroll.month:02d}",
                    "amount": float(entry.net_salary),
                    "currency": entry.currency,
                    "status": payroll.status.value if hasattr(payroll.status, 'value') else payroll.status
                })
            
            return payslips
        except Exception as e:
            # If there's an error, rollback and return empty list
            await self.db.rollback()
            print(f"Error fetching payslips: {e}")
            return []
    
    async def _get_employee_leave_requests(self, employee_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get recent leave requests for an employee"""
        try:
            from modules.leave.models import LeaveRequest
            
            result = await self.db.execute(
                select(LeaveRequest)
                .where(
                    and_(
                        LeaveRequest.employee_id == employee_id,
                        LeaveRequest.is_deleted == False
                    )
                )
                .order_by(LeaveRequest.created_at.desc())
                .limit(5)
            )
            leave_requests = result.scalars().all()
            
            requests = []
            for req in leave_requests:
                # Calculate days
                days = (req.end_date - req.start_date).days + 1 if req.start_date and req.end_date else 0
                requests.append({
                    "id": str(req.id),
                    "leave_type": req.leave_type,
                    "start_date": req.start_date.isoformat() if req.start_date else None,
                    "end_date": req.end_date.isoformat() if req.end_date else None,
                    "status": req.status,
                    "days": days
                })
            
            return requests
        except Exception as e:
            await self.db.rollback()
            print(f"Error fetching leave requests: {e}")
            return []
    
    async def _get_employee_travel_requests(self, employee_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get recent travel requests for an employee"""
        try:
            from modules.travel.models import TravelRequest
            
            result = await self.db.execute(
                select(TravelRequest)
                .where(
                    and_(
                        TravelRequest.employee_id == employee_id,
                        TravelRequest.is_deleted == False
                    )
                )
                .order_by(TravelRequest.created_at.desc())
                .limit(5)
            )
            travel_requests = result.scalars().all()
            
            requests = []
            for req in travel_requests:
                requests.append({
                    "id": str(req.id),
                    "destination": req.destination,
                    "start_date": req.departure_date.isoformat() if req.departure_date else None,
                    "end_date": req.return_date.isoformat() if req.return_date else None,
                    "status": req.status
                })
            
            return requests
        except Exception as e:
            await self.db.rollback()
            print(f"Error fetching travel requests: {e}")
            return []
    
    async def _get_employee_grievances(self, employee_id: uuid.UUID) -> Dict[str, int]:
        """Get grievance statistics for an employee"""
        try:
            from modules.grievance.models import Grievance
            
            # Get all grievances
            result = await self.db.execute(
                select(Grievance)
                .where(
                    and_(
                        Grievance.employee_id == employee_id,
                        Grievance.is_deleted == False
                    )
                )
            )
            grievances = result.scalars().all()
            
            total = len(grievances)
            resolved = sum(1 for g in grievances if g.status in ['resolved', 'closed'])
            pending = sum(1 for g in grievances if g.status in ['open', 'pending', 'investigating'])
            
            return {
                "total": total,
                "resolved": resolved,
                "pending": pending
            }
        except Exception as e:
            await self.db.rollback()
            print(f"Error fetching grievances: {e}")
            return {
                "total": 0,
                "resolved": 0,
                "pending": 0
            }
    
    async def _get_employee_leave_balance(self, employee_id: uuid.UUID) -> Dict[str, Any]:
        """Get leave balance for an employee"""
        try:
            from modules.leave.models import LeaveBalance
            from decimal import Decimal
            
            # Get current year
            current_year = str(datetime.now().year)
            
            # Get all leave balances for current year
            result = await self.db.execute(
                select(LeaveBalance)
                .where(
                    and_(
                        LeaveBalance.employee_id == employee_id,
                        LeaveBalance.year == current_year,
                        LeaveBalance.is_deleted == False
                    )
                )
            )
            balances = result.scalars().all()
            
            # Calculate totals by leave type
            annual_balance = Decimal("0")
            sick_balance = Decimal("0")
            
            for balance in balances:
                if balance.leave_type.lower() in ['annual', 'annual_leave']:
                    annual_balance += balance.available_days
                elif balance.leave_type.lower() in ['sick', 'sick_leave']:
                    sick_balance += balance.available_days
            
            total_balance = annual_balance + sick_balance
            
            return {
                "annual": float(annual_balance),
                "sick": float(sick_balance),
                "total": float(total_balance)
            }
        except Exception as e:
            await self.db.rollback()
            print(f"Error fetching leave balance: {e}")
            return {
                "annual": 0,
                "sick": 0,
                "total": 0
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
    
    @staticmethod
    def invalidate_dashboard_cache(user_id: str):
        """
        Invalidate dashboard cache for a specific user
        Useful when dashboard data changes (e.g., approvals, leave requests, etc.)
        """
        cache_key = build_dashboard_key(user_id, "employee")
        cache.delete(cache_key)
        logger.debug(f"Invalidated dashboard cache for user: {user_id}")