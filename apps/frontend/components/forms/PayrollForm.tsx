'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Calendar, DollarSign, Download } from 'lucide-react'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface PayrollFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function PayrollForm({ open, onOpenChange }: PayrollFormProps) {
  const [loading, setLoading] = useState(false)
  const [generatingPayslip, setGeneratingPayslip] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()
  
  const [employeeId, setEmployeeId] = useState('')
  const [payPeriodMonth, setPayPeriodMonth] = useState('')
  const [payPeriodYear, setPayPeriodYear] = useState(new Date().getFullYear().toString())
  const [basicSalary, setBasicSalary] = useState('')
  const [allowances, setAllowances] = useState('')
  const [bonuses, setBonuses] = useState('')
  const [deductions, setDeductions] = useState('')
  const [taxAmount, setTaxAmount] = useState('')
  const [overtimeHours, setOvertimeHours] = useState('')
  const [overtimeRate, setOvertimeRate] = useState('')

  const selectedEmployee = employees.find(emp => emp.id === employeeId)

  const calculateTotals = () => {
    const basic = parseFloat(basicSalary) || 0
    const allow = parseFloat(allowances) || 0
    const bonus = parseFloat(bonuses) || 0
    const deduc = parseFloat(deductions) || 0
    const tax = parseFloat(taxAmount) || 0
    const otHours = parseFloat(overtimeHours) || 0
    const otRate = parseFloat(overtimeRate) || 0
    
    const overtimePay = otHours * otRate
    const grossPay = basic + allow + bonus + overtimePay
    const totalDeductions = deduc + tax
    const netPay = grossPay - totalDeductions
    
    return { grossPay, totalDeductions, netPay, overtimePay }
  }

  const { grossPay, totalDeductions, netPay, overtimePay } = calculateTotals()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payrollData = {
        employee_id: employeeId,
        employee_name: selectedEmployee ? getEmployeeFullName(selectedEmployee) : '',
        pay_period_month: payPeriodMonth,
        pay_period_year: parseInt(payPeriodYear),
        basic_salary: parseFloat(basicSalary),
        allowances: parseFloat(allowances) || 0,
        bonuses: parseFloat(bonuses) || 0,
        overtime_hours: parseFloat(overtimeHours) || 0,
        overtime_rate: parseFloat(overtimeRate) || 0,
        overtime_pay: overtimePay,
        gross_pay: grossPay,
        deductions: parseFloat(deductions) || 0,
        tax_amount: parseFloat(taxAmount) || 0,
        total_deductions: totalDeductions,
        net_pay: netPay,
        status: 'processed',
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/payroll/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payrollData),
      })

      if (!response.ok) {
        throw new Error('Failed to process payroll')
      }

      const result = await response.json()
      alert('Payroll processed successfully!')
      
      // Ask if user wants to generate payslip
      if (window.confirm('Would you like to generate and download the payslip now?')) {
        await generatePayslip(result.id || employeeId)
      }
      
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error processing payroll:', error)
      alert('Failed to process payroll. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const generatePayslip = async (payrollId: string) => {
    setGeneratingPayslip(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/payroll/${payrollId}/payslip`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to generate payslip')
      }

      // Download the PDF
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `payslip_${selectedEmployee?.employee_number}_${payPeriodMonth}_${payPeriodYear}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      alert('Payslip downloaded successfully!')
    } catch (error) {
      console.error('Error generating payslip:', error)
      alert('Failed to generate payslip. The payroll was processed but payslip generation failed.')
    } finally {
      setGeneratingPayslip(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setPayPeriodMonth('')
    setBasicSalary('')
    setAllowances('')
    setBonuses('')
    setDeductions('')
    setTaxAmount('')
    setOvertimeHours('')
    setOvertimeRate('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Process Payroll & Generate Payslip
          </DialogTitle>
          <DialogDescription>
            Process employee payroll and generate payslip document
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Employee & Period */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Employee & Pay Period</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2 col-span-2">
                <Label htmlFor="employee">Employee *</Label>
                <Select value={employeeId} onValueChange={setEmployeeId} required>
                  <SelectTrigger id="employee">
                    <SelectValue placeholder={employeesLoading ? "Loading..." : "Select employee"} />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.employee_number} - {getEmployeeFullName(emp)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedEmployee && (
                <>
                  <div className="space-y-2">
                    <Label>Position</Label>
                    <Input value={selectedEmployee.position_id || 'N/A'} readOnly className="bg-gray-50" />
                  </div>
                  <div className="space-y-2">
                    <Label>Location</Label>
                    <Input value={selectedEmployee.work_location || 'N/A'} readOnly className="bg-gray-50" />
                  </div>
                </>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="month" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Pay Period Month *
                </Label>
                <Select value={payPeriodMonth} onValueChange={setPayPeriodMonth} required>
                  <SelectTrigger id="month">
                    <SelectValue placeholder="Select month" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="01">January</SelectItem>
                    <SelectItem value="02">February</SelectItem>
                    <SelectItem value="03">March</SelectItem>
                    <SelectItem value="04">April</SelectItem>
                    <SelectItem value="05">May</SelectItem>
                    <SelectItem value="06">June</SelectItem>
                    <SelectItem value="07">July</SelectItem>
                    <SelectItem value="08">August</SelectItem>
                    <SelectItem value="09">September</SelectItem>
                    <SelectItem value="10">October</SelectItem>
                    <SelectItem value="11">November</SelectItem>
                    <SelectItem value="12">December</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="year">Pay Period Year *</Label>
                <Select value={payPeriodYear} onValueChange={setPayPeriodYear} required>
                  <SelectTrigger id="year">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2024">2024</SelectItem>
                    <SelectItem value="2025">2025</SelectItem>
                    <SelectItem value="2026">2026</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Earnings */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Earnings</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="basic-salary">Basic Salary (USD) *</Label>
                <Input
                  id="basic-salary"
                  type="number"
                  step="0.01"
                  value={basicSalary}
                  onChange={(e) => setBasicSalary(e.target.value)}
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="allowances">Allowances (USD)</Label>
                <Input
                  id="allowances"
                  type="number"
                  step="0.01"
                  value={allowances}
                  onChange={(e) => setAllowances(e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="bonuses">Bonuses (USD)</Label>
                <Input
                  id="bonuses"
                  type="number"
                  step="0.01"
                  value={bonuses}
                  onChange={(e) => setBonuses(e.target.value)}
                  placeholder="0.00"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="overtime-hours">Overtime Hours</Label>
                <Input
                  id="overtime-hours"
                  type="number"
                  step="0.5"
                  value={overtimeHours}
                  onChange={(e) => setOvertimeHours(e.target.value)}
                  placeholder="0"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="overtime-rate">Overtime Rate (USD/hr)</Label>
                <Input
                  id="overtime-rate"
                  type="number"
                  step="0.01"
                  value={overtimeRate}
                  onChange={(e) => setOvertimeRate(e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>

            {overtimePay > 0 && (
              <div className="bg-green-50 border border-green-200 rounded p-3">
                <p className="text-sm text-green-800">
                  <strong>Overtime Pay:</strong> ${overtimePay.toFixed(2)}
                </p>
              </div>
            )}
          </div>

          {/* Deductions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Deductions</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="deductions">Other Deductions (USD)</Label>
                <Input
                  id="deductions"
                  type="number"
                  step="0.01"
                  value={deductions}
                  onChange={(e) => setDeductions(e.target.value)}
                  placeholder="0.00"
                />
                <p className="text-xs text-gray-500">Loans, advances, insurance, etc.</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tax">Tax Amount (USD)</Label>
                <Input
                  id="tax"
                  type="number"
                  step="0.01"
                  value={taxAmount}
                  onChange={(e) => setTaxAmount(e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
            <h3 className="text-lg font-semibold">Payment Summary</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Gross Pay</p>
                <p className="text-xl font-bold text-green-600">${grossPay.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-500">Total Deductions</p>
                <p className="text-xl font-bold text-red-600">${totalDeductions.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-500">Net Pay</p>
                <p className="text-2xl font-bold text-blue-600">${netPay.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading || generatingPayslip}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || generatingPayslip}
              className="bg-gradient-to-r from-pink-600 to-cyan-600 hover:from-pink-700 hover:to-cyan-700"
            >
              <DollarSign className="w-4 h-4 mr-2" />
              {loading ? 'Processing...' : generatingPayslip ? 'Generating Payslip...' : 'Process & Generate Payslip'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
