// Utility functions for Excel export/import
import * as XLSX from 'xlsx'

export interface ExcelColumn {
  header: string
  key: string
  width?: number
}

export function exportToExcel(data: any[], columns: ExcelColumn[], filename: string) {
  // Create worksheet data
  const headers = columns.map(col => col.header)
  const rows = data.map(item => 
    columns.map(col => {
      const value = item[col.key]
      return value === null || value === undefined ? '' : value
    })
  )
  
  const worksheetData = [headers, ...rows]
  
  // Create workbook and worksheet
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
  
  // Set column widths
  const columnWidths = columns.map(col => ({ wch: col.width || 15 }))
  worksheet['!cols'] = columnWidths
  
  // Generate Excel file and download
  XLSX.writeFile(workbook, `${filename}_${new Date().toISOString().split('T')[0]}.xlsx`)
}

export function exportEmployeeTemplate() {
  // Define columns exactly as expected by the import function
  // Order matters - should match ImportEmployeesDialog.tsx parsing
  const columns: ExcelColumn[] = [
    { header: 'First Name', key: 'first_name', width: 20 }, // REQUIRED
    { header: 'Last Name', key: 'last_name', width: 20 }, // REQUIRED
    { header: 'Work Email', key: 'work_email', width: 30 }, // REQUIRED
    { header: 'Personal Email', key: 'personal_email', width: 30 }, // Optional
    { header: 'Phone', key: 'phone', width: 18 }, // Optional
    { header: 'Mobile', key: 'mobile', width: 18 }, // Optional
    { header: 'Date of Birth', key: 'date_of_birth', width: 18 }, // Optional - Format: YYYY-MM-DD
    { header: 'Gender', key: 'gender', width: 12 }, // Optional - Values: male, female, other
    { header: 'Nationality', key: 'nationality', width: 20 }, // Optional - Country name
    { header: 'Employment Type', key: 'employment_type', width: 18 }, // Optional - Values: full_time, part_time, consultant, volunteer, intern
    { header: 'Work Location', key: 'work_location', width: 25 }, // Optional - City/Office location
    { header: 'Hire Date', key: 'hire_date', width: 18 }, // Optional - Format: YYYY-MM-DD
    // Note: Position and Department are not imported (require ID lookup in system)
    // If needed, these should be set manually after import
  ]
  
  // Create workbook with instructions sheet and data sheet
  const workbook = XLSX.utils.book_new()
  
  // Instructions sheet
  const instructions = [
    ['EMPLOYEE IMPORT TEMPLATE - INSTRUCTIONS'],
    [''],
    ['REQUIRED FIELDS (must be filled):'],
    ['  - First Name: Employee\'s first name'],
    ['  - Last Name: Employee\'s last name'],
    ['  - Work Email: Official work email address (must be unique)'],
    [''],
    ['OPTIONAL FIELDS:'],
    ['  - Personal Email: Personal email address'],
    ['  - Phone: Office phone number'],
    ['  - Mobile: Mobile phone number'],
    ['  - Date of Birth: Format YYYY-MM-DD (e.g., 1990-01-15)'],
    ['  - Gender: male, female, or other'],
    ['  - Nationality: Country name (e.g., Afghanistan)'],
    ['  - Employment Type: full_time, part_time, consultant, volunteer, or intern'],
    ['  - Work Location: City or office location'],
    ['  - Hire Date: Format YYYY-MM-DD (e.g., 2024-01-01)'],
    [''],
    ['NOTES:'],
    ['  - Position and Department fields are NOT imported (use system to assign after import)'],
    ['  - Dates must be in YYYY-MM-DD format'],
    ['  - Employment Type is case-insensitive but should match listed values'],
    ['  - Empty rows will be skipped'],
    ['  - Rows missing required fields will be skipped'],
    [''],
    ['IMPORT PROCESS:'],
    ['  1. Fill in employee data in the "Employees" sheet below'],
    ['  2. Save the file'],
    ['  3. Use the Import Employees feature in the system'],
    ['  4. Select this file to upload'],
    [''],
  ]
  
  const instructionsSheet = XLSX.utils.aoa_to_sheet(instructions)
  
  // Set column widths for instructions
  instructionsSheet['!cols'] = [{ wch: 80 }]
  
  // Employees data sheet with sample row
  const sampleData = [
    {
      first_name: 'John',
      last_name: 'Doe',
      work_email: 'john.doe@example.org',
      personal_email: 'john.personal@gmail.com',
      phone: '+93123456789',
      mobile: '+93987654321',
      date_of_birth: '1990-01-15',
      gender: 'male',
      nationality: 'Afghanistan',
      employment_type: 'full_time',
      work_location: 'Kabul',
      hire_date: '2024-01-01',
    }
  ]
  
  // Create headers row
  const headers = columns.map(col => col.header)
  const rows = sampleData.map(item => 
    columns.map(col => {
      const value = item[col.key]
      return value === null || value === undefined ? '' : value
    })
  )
  
  const worksheetData = [headers, ...rows]
  const employeesSheet = XLSX.utils.aoa_to_sheet(worksheetData)
  
  // Set column widths
  const columnWidths = columns.map(col => ({ wch: col.width || 15 }))
  employeesSheet['!cols'] = columnWidths
  
  // Freeze header row
  employeesSheet['!freeze'] = { xSplit: 0, ySplit: 1 }
  
  // Add sheets to workbook
  XLSX.utils.book_append_sheet(workbook, instructionsSheet, 'Instructions')
  XLSX.utils.book_append_sheet(workbook, employeesSheet, 'Employees')
  
  // Generate Excel file and download
  XLSX.writeFile(workbook, `employee_import_template_${new Date().toISOString().split('T')[0]}.xlsx`)
}

export function exportLeaveTemplate() {
  const columns: ExcelColumn[] = [
    { header: 'Employee Email', key: 'employee_email' },
    { header: 'Leave Type (annual/sick/unpaid/maternity/paternity/bereavement/marriage/study)', key: 'leave_type' },
    { header: 'Start Date (YYYY-MM-DD)', key: 'start_date' },
    { header: 'End Date (YYYY-MM-DD)', key: 'end_date' },
    { header: 'Reason', key: 'reason' },
    { header: 'Covering Person (optional)', key: 'covering_person' },
  ]
  
  const sampleData = [
    {
      employee_email: 'john.doe@example.org',
      leave_type: 'annual',
      start_date: '2025-01-15',
      end_date: '2025-01-20',
      reason: 'Family vacation',
      covering_person: '',
    }
  ]
  
  exportToExcel(sampleData, columns, 'leave_import_template')
}

export function exportPayrollTemplate() {
  const columns: ExcelColumn[] = [
    { header: 'Employee Email', key: 'employee_email' },
    { header: 'Pay Period Month (01-12)', key: 'pay_period_month' },
    { header: 'Pay Period Year', key: 'pay_period_year' },
    { header: 'Basic Salary (USD)', key: 'basic_salary' },
    { header: 'Allowances (USD)', key: 'allowances' },
    { header: 'Bonuses (USD)', key: 'bonuses' },
    { header: 'Overtime Hours', key: 'overtime_hours' },
    { header: 'Overtime Rate (USD/hr)', key: 'overtime_rate' },
    { header: 'Other Deductions (USD)', key: 'deductions' },
    { header: 'Tax Amount (USD)', key: 'tax_amount' },
  ]
  
  const sampleData = [
    {
      employee_email: 'john.doe@example.org',
      pay_period_month: '01',
      pay_period_year: '2025',
      basic_salary: '5000.00',
      allowances: '500.00',
      bonuses: '0.00',
      overtime_hours: '0',
      overtime_rate: '0.00',
      deductions: '0.00',
      tax_amount: '750.00',
    }
  ]
  
  exportToExcel(sampleData, columns, 'payroll_import_template')
}

export function exportCourseEnrollmentTemplate() {
  const columns: ExcelColumn[] = [
    { header: 'Employee Email', key: 'employee_email' },
    { header: 'Course Name', key: 'course_name' },
    { header: 'Enrollment Date (YYYY-MM-DD)', key: 'enrollment_date' },
    { header: 'Status (enrolled/completed/dropped)', key: 'status' },
  ]
  
  const sampleData = [
    {
      employee_email: 'john.doe@example.org',
      course_name: 'Leadership Development',
      enrollment_date: '2025-01-01',
      status: 'enrolled',
    }
  ]
  
  exportToExcel(sampleData, columns, 'course_enrollment_template')
}

export function exportPerformanceReviewTemplate() {
  const columns: ExcelColumn[] = [
    { header: 'Employee Email', key: 'employee_email' },
    { header: 'Review Period Start (YYYY-MM-DD)', key: 'period_start' },
    { header: 'Review Period End (YYYY-MM-DD)', key: 'period_end' },
    { header: 'Assessor Email', key: 'assessor_email' },
    { header: 'Overall Rating (1-5)', key: 'overall_rating' },
    { header: 'Comments', key: 'comments' },
  ]
  
  const sampleData = [
    {
      employee_email: 'john.doe@example.org',
      period_start: '2024-01-01',
      period_end: '2024-12-31',
      assessor_email: 'manager@example.org',
      overall_rating: '4',
      comments: 'Excellent performance',
    }
  ]
  
  exportToExcel(sampleData, columns, 'performance_review_template')
}
