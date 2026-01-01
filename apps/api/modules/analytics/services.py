"""Analytics - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import Dict
from datetime import date, datetime, timedelta
from decimal import Decimal

from modules.employees.models import Employee
from modules.leave.models import LeaveRequest
from modules.timesheets.models import Timesheet
from modules.performance.models import PerformanceReviewCycle
from modules.recruitment.models import JobPosting
from modules.leave.models import LeaveBalance


class AnalyticsService:
    """Service for HR analytics and metrics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_metrics(self) -> Dict:
        """Get HR dashboard metrics"""
        # Total employees
        total_result = await self.db.execute(
            select(func.count(Employee.id)).where(Employee.is_deleted == False)
        )
        total_employees = total_result.scalar() or 0
        
        # Active employees
        active_result = await self.db.execute(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.is_deleted == False,
                    Employee.status == "active"
                )
            )
        )
        active_employees = active_result.scalar() or 0
        
        # Pending leave requests
        pending_leave_result = await self.db.execute(
            select(func.count(LeaveRequest.id)).where(
                and_(
                    LeaveRequest.is_deleted == False,
                    LeaveRequest.status == "pending"
                )
            )
        )
        pending_leave_requests = pending_leave_result.scalar() or 0
        
        # Pending timesheets
        pending_timesheet_result = await self.db.execute(
            select(func.count(Timesheet.id)).where(
                and_(
                    Timesheet.is_deleted == False,
                    Timesheet.status == "submitted"
                )
            )
        )
        pending_timesheets = pending_timesheet_result.scalar() or 0
        
        # Upcoming reviews (next 30 days)
        upcoming_reviews_result = await self.db.execute(
            select(func.count(PerformanceReviewCycle.id)).where(
                and_(
                    PerformanceReviewCycle.is_deleted == False,
                    PerformanceReviewCycle.review_period_end >= date.today(),
                    PerformanceReviewCycle.review_period_end <= date.today() + timedelta(days=30)
                )
            )
        )
        upcoming_reviews = upcoming_reviews_result.scalar() or 0
        
        # Open positions
        open_positions_result = await self.db.execute(
            select(func.count(JobPosting.id)).where(
                and_(
                    JobPosting.is_deleted == False,
                    JobPosting.status == "open"
                )
            )
        )
        open_positions = open_positions_result.scalar() or 0
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "pending_leave_requests": pending_leave_requests,
            "pending_timesheets": pending_timesheets,
            "upcoming_reviews": upcoming_reviews,
            "open_positions": open_positions
        }
    
    async def get_headcount_report(self, group_by: str = "department") -> Dict:
        """Get headcount by department or location"""
        if group_by == "department":
            result = await self.db.execute(
                select(
                    func.count(Employee.id).label('count'),
                    Employee.department_id
                )
                .where(and_(Employee.is_deleted == False, Employee.status == "active"))
                .group_by(Employee.department_id)
            )
            
            from modules.employees.models import Department
            departments_result = await self.db.execute(
                select(Department)
            )
            departments = {d.id: d.name for d in departments_result.scalars().all()}
            
            headcount = []
            for row in result:
                headcount.append({
                    "group": departments.get(row.department_id, "Unassigned"),
                    "count": row.count
                })
        else:  # location/country
            result = await self.db.execute(
                select(
                    func.count(Employee.id).label('count'),
                    Employee.country_code
                )
                .where(and_(Employee.is_deleted == False, Employee.status == "active"))
                .group_by(Employee.country_code)
            )
            
            headcount = []
            for row in result:
                headcount.append({
                    "group": row.country_code or "Unknown",
                    "count": row.count
                })
        
        return {"headcount": headcount}
    
    async def get_turnover_rate(self, year: int = None) -> Dict:
        """Get employee turnover rate"""
        if not year:
            year = datetime.now().year
        
        # Total employees at start of year
        start_of_year = date(year, 1, 1)
        
        # Employees who were active at start of year
        active_at_start_result = await self.db.execute(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.is_deleted == False,
                    Employee.hire_date <= start_of_year,
                    (Employee.termination_date >= start_of_year) | (Employee.termination_date.is_(None))
                )
            )
        )
        employees_at_start = active_at_start_result.scalar() or 0
        
        # Terminations during the year
        terminations_result = await self.db.execute(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.is_deleted == False,
                    extract('year', Employee.termination_date) == year,
                    Employee.termination_date.isnot(None)
                )
            )
        )
        terminations = terminations_result.scalar() or 0
        
        # Calculate turnover rate
        if employees_at_start > 0:
            turnover_rate = (terminations / employees_at_start) * 100
        else:
            turnover_rate = 0.0
        
        return {
            "year": year,
            "employees_at_start": employees_at_start,
            "terminations": terminations,
            "turnover_rate": round(turnover_rate, 2)
        }
    
    async def get_leave_utilization(self, year: int = None) -> Dict:
        """Get leave utilization statistics"""
        if not year:
            year = datetime.now().year
        
        year_str = str(year)
        
        # Get all leave balances for the year
        result = await self.db.execute(
            select(
                LeaveBalance.leave_type,
                func.sum(LeaveBalance.total_days).label('total_days'),
                func.sum(LeaveBalance.used_days).label('used_days'),
                func.sum(LeaveBalance.pending_days).label('pending_days'),
                func.sum(LeaveBalance.available_days).label('available_days')
            )
            .where(
                and_(
                    LeaveBalance.year == year_str,
                    LeaveBalance.is_deleted == False
                )
            )
            .group_by(LeaveBalance.leave_type)
        )
        
        utilization_by_type = []
        total_allocated = Decimal('0')
        total_used = Decimal('0')
        
        for row in result:
            utilization_pct = 0.0
            if row.total_days and row.total_days > 0:
                utilization_pct = float((row.used_days / row.total_days) * 100)
            
            utilization_by_type.append({
                "leave_type": row.leave_type,
                "total_days": float(row.total_days or 0),
                "used_days": float(row.used_days or 0),
                "pending_days": float(row.pending_days or 0),
                "available_days": float(row.available_days or 0),
                "utilization_percentage": round(utilization_pct, 2)
            })
            
            total_allocated += row.total_days or Decimal('0')
            total_used += row.used_days or Decimal('0')
        
        overall_utilization = 0.0
        if total_allocated > 0:
            overall_utilization = float((total_used / total_allocated) * 100)
        
        return {
            "year": year,
            "overall_utilization_percentage": round(overall_utilization, 2),
            "total_allocated_days": float(total_allocated),
            "total_used_days": float(total_used),
            "by_leave_type": utilization_by_type
        }
