"""
Employee Management Module - API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user, require_hr_read, require_hr_write
from core.pdf_generator import create_organization_chart_pdf
from modules.employees.services import EmployeeService
from modules.employees.schemas import (
    EmployeeCreate, 
    EmployeeUpdate, 
    EmployeeResponse,
    EmployeeHierarchyUpdate,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    PositionCreate,
    PositionUpdate,
    PositionResponse
)
from modules.employees.models import Employee, Department, Position

router = APIRouter()


# ============================================
# SPECIFIC ROUTES (must come before /{employee_id})
# ============================================

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get all departments"""
    result = await db.execute(select(Department).where(Department.is_deleted == False))
    departments = result.scalars().all()
    return [DepartmentResponse.model_validate(dept) for dept in departments]


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Create a new department"""
    department = Department(**department_data.model_dump())
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return DepartmentResponse.model_validate(department)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Update a department"""
    result = await db.execute(
        select(Department).where(
            Department.id == uuid.UUID(department_id),
            Department.is_deleted == False
        )
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Update fields
    update_data = department_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(department, key):
            setattr(department, key, value)
    
    await db.commit()
    await db.refresh(department)
    return DepartmentResponse.model_validate(department)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Delete a department (soft delete)"""
    result = await db.execute(
        select(Department).where(
            Department.id == uuid.UUID(department_id),
            Department.is_deleted == False
        )
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if any employees are assigned to this department
    emp_result = await db.execute(
        select(Employee).where(
            Employee.department_id == uuid.UUID(department_id),
            Employee.is_deleted == False
        )
    )
    if emp_result.first():
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete department with assigned employees"
        )
    
    department.is_deleted = True
    await db.commit()
    return None


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get all positions"""
    result = await db.execute(select(Position).where(Position.is_deleted == False))
    positions = result.scalars().all()
    return [PositionResponse.model_validate(pos) for pos in positions]


@router.post("/positions", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Create a new position"""
    position = Position(**position_data.model_dump())
    db.add(position)
    await db.commit()
    await db.refresh(position)
    return PositionResponse.model_validate(position)


@router.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: str,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Update a position"""
    result = await db.execute(
        select(Position).where(
            Position.id == uuid.UUID(position_id),
            Position.is_deleted == False
        )
    )
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Update fields
    update_data = position_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(position, key):
            setattr(position, key, value)
    
    await db.commit()
    await db.refresh(position)
    return PositionResponse.model_validate(position)


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """Delete a position (soft delete)"""
    result = await db.execute(
        select(Position).where(
            Position.id == uuid.UUID(position_id),
            Position.is_deleted == False
        )
    )
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Check if any employees are assigned to this position
    emp_result = await db.execute(
        select(Employee).where(
            Employee.position_id == uuid.UUID(position_id),
            Employee.is_deleted == False
        )
    )
    if emp_result.first():
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete position with assigned employees"
        )
    
    position.is_deleted = True
    await db.commit()
    return None


@router.get("/organization-chart", response_model=List[EmployeeResponse])
async def get_organization_chart(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all employees with hierarchical relationships for org chart
    
    Requires: Authentication
    """
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.position),
        selectinload(Employee.manager)
    ).where(
        Employee.is_deleted == False,
        Employee.status == 'ACTIVE'
    )
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    return [EmployeeResponse.model_validate(emp) for emp in employees]


@router.get("/organization-chart/export")
async def export_organization_chart_pdf(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Export organization chart as PDF
    
    Requires: Authentication
    """
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.position),
        selectinload(Employee.manager)
    ).where(
        Employee.is_deleted == False,
        Employee.status == 'ACTIVE'
    )
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Convert to dict for PDF generation
    employees_data = [EmployeeResponse.model_validate(emp).model_dump() for emp in employees]
    
    # Generate PDF
    pdf_buffer = create_organization_chart_pdf(employees_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=organization_chart.pdf"
        }
    )


# ============================================
# MAIN EMPLOYEE ROUTES
# ============================================

@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """
    List all employees
    
    Requires permission: hr:read
    """
    # Query with eager loading of relationships
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        )
        .where(Employee.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    employees = result.scalars().all()
    return employees


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Create new employee
    
    Requires permission: hr:write
    """
    service = EmployeeService(db)
    employee = await service.create_employee(employee_data)
    
    # Reload with relationships to avoid detached instance errors
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        )
        .where(Employee.id == employee.id)
    )
    employee = result.scalar_one_or_none()
    
    return employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """
    Get employee by ID
    
    Requires permission: hr:read
    """
    # Query with eager loading of relationships
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        )
        .where(Employee.id == uuid.UUID(employee_id))
        .where(Employee.is_deleted == False)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="Employee")
    
    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Update employee
    
    Requires permission: hr:write
    """
    # Get employee with eager loading
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        )
        .where(Employee.id == uuid.UUID(employee_id))
        .where(Employee.is_deleted == False)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="Employee")
    
    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    
    # Check if work_email is being updated and sync with user record
    work_email_updated = 'work_email' in update_data
    new_work_email = update_data.get('work_email')
    
    for key, value in update_data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)
    
    # If work email was updated and employee has a user account, update the user email too
    if work_email_updated and new_work_email and employee.user_id:
        from core.models import User
        user_result = await db.execute(
            select(User).where(User.id == employee.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.email = new_work_email
    
    await db.commit()
    await db.refresh(employee)
    
    # Reload with relationships
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        )
        .where(Employee.id == uuid.UUID(employee_id))
    )
    employee = result.scalar_one_or_none()
    
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Delete employee (soft delete)
    
    Requires permission: hr:write
    """
    service = EmployeeService(db)
    await service.delete_employee(employee_id)
    return None


@router.post("/{employee_id}/activate", response_model=EmployeeResponse)
async def activate_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Activate employee - set status to ACTIVE
    
    Requires permission: hr:write
    """
    service = EmployeeService(db)
    employee = await service.activate_employee(employee_id)
    return employee


@router.post("/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Deactivate employee - set status to TERMINATED
    
    Requires permission: hr:write
    """
    service = EmployeeService(db)
    employee = await service.deactivate_employee(employee_id)
    return employee


@router.patch("/{employee_id}/hierarchy", response_model=EmployeeResponse)
async def update_employee_hierarchy(
    employee_id: str,
    hierarchy_data: EmployeeHierarchyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_write)
):
    """
    Update employee's manager and department (organizational hierarchy)
    
    Requires permission: hr:write
    """
    try:
        emp_uuid = uuid.UUID(employee_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    
    # Get employee
    result = await db.execute(
        select(Employee).where(Employee.id == emp_uuid)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate manager doesn't create circular reference
    if hierarchy_data.manager_id:
        # Check if new manager is not the same employee
        if hierarchy_data.manager_id == emp_uuid:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")
        
        # Check if new manager exists
        manager_result = await db.execute(
            select(Employee).where(Employee.id == hierarchy_data.manager_id)
        )
        manager = manager_result.scalar_one_or_none()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Check for circular reference (if new manager reports to this employee)
        current_manager = manager
        while current_manager.manager_id:
            if current_manager.manager_id == emp_uuid:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot create circular reporting structure"
                )
            manager_result = await db.execute(
                select(Employee).where(Employee.id == current_manager.manager_id)
            )
            current_manager = manager_result.scalar_one_or_none()
            if not current_manager:
                break
    
    # Validate department exists
    if hierarchy_data.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == hierarchy_data.department_id)
        )
        if not dept_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Department not found")
    
    # Update employee
    employee.manager_id = hierarchy_data.manager_id
    if hierarchy_data.department_id:
        employee.department_id = hierarchy_data.department_id
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.position),
            selectinload(Employee.manager)
        ).where(Employee.id == emp_uuid)
    )
    employee = result.scalar_one()
    
    return EmployeeResponse.model_validate(employee)


# TODO: Add endpoints for:
# - Upload employee document
# - List employee documents
# - Get employee contracts
# - Add employee contract
# - Export employee data
