"""
Employee Management Module - Service Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from modules.employees.repositories import EmployeeRepository
from modules.employees.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Service for employee operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
    
    async def get_employee(self, employee_id: uuid.UUID):
        """Get employee by ID"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        return employee
    
    async def list_employees(self, skip: int = 0, limit: int = 100):
        """List all employees"""
        return await self.employee_repo.get_all(skip=skip, limit=limit)
    
    async def create_employee(self, employee_data: EmployeeCreate):
        """Create new employee"""
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError
        from core.exceptions import AlreadyExistsException, ValidationException
        from modules.employees.models import Employee, Contract
        
        # Auto-generate employee number if not provided
        employee_dict = employee_data.model_dump()
        
        # Extract contract-related fields (not part of Employee model)
        contract_salary = employee_dict.pop("salary", None)
        contract_currency = employee_dict.pop("currency", "USD")
        contract_type = employee_dict.pop("contract_type", None)
        contract_start_date = employee_dict.pop("contract_start_date", None)
        contract_end_date = employee_dict.pop("contract_end_date", None)
        
        # Normalize enum-like fields to actual enum members accepted by SQLAlchemy.
        from modules.employees.models import EmploymentType, WorkType

        def _to_enum_member(value: str, enum_cls):
            token = value.strip().lower().replace("-", "_").replace(" ", "_")
            for member in enum_cls:
                if token in (member.value.lower(), member.name.lower()):
                    return member
            return None

        employment_type = employee_dict.get("employment_type")
        if employment_type:
            employment_type_member = _to_enum_member(employment_type, EmploymentType)
            if not employment_type_member:
                raise ValidationException(
                    message="Invalid employment_type",
                    details=f"Unsupported value: {employment_type}",
                )
            employee_dict["employment_type"] = employment_type_member

        work_type = employee_dict.get("work_type")
        if work_type:
            work_type_member = _to_enum_member(work_type, WorkType)
            if not work_type_member:
                raise ValidationException(
                    message="Invalid work_type",
                    details=f"Unsupported value: {work_type}",
                )
            employee_dict["work_type"] = work_type_member
        
        async def _generate_next_employee_number() -> str:
            """Generate the next sequential employee number EMP-xxx."""
            result = await self.db.execute(
                select(Employee.employee_number)
                .where(Employee.employee_number.like("EMP-%"))
            )
            employee_numbers = result.scalars().all()
            
            if employee_numbers:
                max_num = 0
                for emp_num in employee_numbers:
                    try:
                        num = int(emp_num.split("-")[1])
                        if num > max_num:
                            max_num = num
                    except (IndexError, ValueError):
                        continue
                return f"EMP-{max_num + 1:03d}"
            return "EMP-001"

        async def _generate_next_contract_number() -> str:
            """Generate the next sequential contract number CON-xxxx."""
            result = await self.db.execute(
                select(Contract.contract_number).where(
                    Contract.contract_number.like("CON-%")
                )
            )
            contract_numbers = result.scalars().all()

            if contract_numbers:
                max_num = 0
                for con_num in contract_numbers:
                    try:
                        num = int(con_num.split("-")[1])
                        if num > max_num:
                            max_num = num
                    except (IndexError, ValueError):
                        continue
                return f"CON-{max_num + 1:04d}"
            return "CON-0001"
        
        # Ensure we always have some employee number (auto-generated if missing)
        if not employee_dict.get("employee_number"):
            employee_dict["employee_number"] = await _generate_next_employee_number()
        
        # Try to create employee, retrying on employee_number conflicts by regenerating
        employee = None
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                async with self.db.begin():
                    employee = await self.employee_repo.create(employee_dict)

                    # Create contract in the same transaction if salary is provided.
                    if contract_salary and contract_salary > 0:
                        contract_number = await _generate_next_contract_number()

                        contract = Contract(
                            employee_id=employee.id,
                            contract_number=contract_number,
                            contract_type=contract_type or "Permanent",
                            start_date=contract_start_date or employee.hire_date,
                            end_date=contract_end_date,
                            salary=contract_salary,
                            currency=contract_currency,
                            salary_frequency="monthly",
                            is_active="true",
                            country_code=employee.country_code or "AF",
                        )
                        self.db.add(contract)

                await self.db.refresh(employee)
                break
            except IntegrityError as exc:
                await self.db.rollback()
                error_text = str(exc)
                
                # Unique violation on employee_number – regenerate and retry
                if "employees_employee_number_key" in error_text:
                    employee_dict["employee_number"] = await _generate_next_employee_number()
                    continue
                
                # Unique violation on work_email – surface clear error
                if "employees_work_email_key" in error_text:
                    raise AlreadyExistsException(
                        resource="Employee",
                        details="An employee with this work email already exists.",
                    ) from exc

                # Unique violation on contract_number – regenerate and retry.
                if "contracts_contract_number_key" in error_text:
                    continue
                
                # Other integrity errors
                raise ValidationException(
                    message="Failed to create employee due to database constraint",
                    details=error_text,
                ) from exc
            except Exception as exc:
                import logging, traceback
                logging.getLogger(__name__).error(
                    "create_employee unexpected error: %s\n%s",
                    exc,
                    traceback.format_exc()
                )
                await self.db.rollback()
                raise ValidationException(
                    message="Failed to create employee due to invalid data",
                    details=str(exc),
                ) from exc
        
        if employee is None:
            raise ValidationException(
                message="Could not generate a unique employee number after multiple attempts",
                details="Too many conflicts on employee_number",
            )
        
        return employee
    
    async def update_employee(self, employee_id: uuid.UUID, employee_data: EmployeeUpdate):
        """Update employee"""
        employee = await self.employee_repo.update(
            employee_id,
            employee_data.model_dump(exclude_unset=True)
        )
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        await self.db.commit()
        return employee
    
    async def delete_employee(self, employee_id: uuid.UUID):
        """Delete employee (soft delete)"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.is_deleted = True
        await self.db.commit()
        return None
    
    async def activate_employee(self, employee_id: uuid.UUID):
        """Activate employee - set status to ACTIVE"""
        from modules.employees.models import Employee
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.manager)
            )
            .where(Employee.id == employee_id)
            .where(Employee.is_deleted == False)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.status = 'ACTIVE'
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
    
    async def deactivate_employee(self, employee_id: uuid.UUID):
        """Deactivate employee - set status to TERMINATED"""
        from modules.employees.models import Employee
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.manager)
            )
            .where(Employee.id == employee_id)
            .where(Employee.is_deleted == False)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.status = 'TERMINATED'
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
