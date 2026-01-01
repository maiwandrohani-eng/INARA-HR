'use client'

import { useState, useRef } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import * as XLSX from 'xlsx'
import { exportEmployeeTemplate } from '@/utils/excelExport'

interface ImportEmployeesDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

interface ImportResult {
  success: number
  failed: number
  errors: string[]
  message?: string
}

export function ImportEmployeesDialog({ open, onOpenChange, onSuccess }: ImportEmployeesDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      // Check if it's an Excel file
      const validExtensions = ['.xlsx', '.xls', '.csv']
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
      if (!validExtensions.includes(fileExtension)) {
        alert('Please select an Excel file (.xlsx, .xls, or .csv)')
        return
      }
      setFile(selectedFile)
      setResult(null)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      const validExtensions = ['.xlsx', '.xls', '.csv']
      const fileExtension = droppedFile.name.substring(droppedFile.name.lastIndexOf('.')).toLowerCase()
      if (validExtensions.includes(fileExtension)) {
        setFile(droppedFile)
        setResult(null)
      } else {
        alert('Please drop an Excel file (.xlsx, .xls, or .csv)')
      }
    }
  }

  const parseExcel = async (file: File): Promise<any[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const data = e.target?.result
          const workbook = XLSX.read(data, { type: 'binary' })
          const sheetName = workbook.SheetNames[0]
          const worksheet = workbook.Sheets[sheetName]
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]
          
          if (jsonData.length < 2) {
            resolve([])
            return
          }

          const headers = jsonData[0].map((h: any) => h?.toString().trim() || '')
          const employees: any[] = []

          for (let i = 1; i < jsonData.length; i++) {
            const values = jsonData[i]
            
            // Skip empty rows
            if (!values || values.every((v: any) => !v || v.toString().trim() === '')) {
              continue
            }
            
            const row: any = {}
            
            headers.forEach((header: string, index: number) => {
              const value = values[index]
              
              // Skip empty values
              if (value === null || value === undefined || value === '') {
                return
              }
              
              const trimmedValue = value.toString().trim()
              
              // Map Excel headers to API fields (case-insensitive matching)
              const headerLower = header.toLowerCase().trim()
              switch (headerLower) {
                case 'first name':
                  row.first_name = trimmedValue
                  break
                case 'last name':
                  row.last_name = trimmedValue
                  break
                case 'work email':
                case 'work_email':
                  row.work_email = trimmedValue.toLowerCase()
                  break
                case 'personal email':
                case 'personal_email':
                  row.personal_email = trimmedValue.toLowerCase()
                  break
                case 'phone':
                  row.phone = trimmedValue
                  break
                case 'mobile':
                  row.mobile = trimmedValue
                  break
                case 'date of birth':
                case 'date_of_birth':
                case 'dob':
                  row.date_of_birth = trimmedValue
                  break
                case 'gender':
                  row.gender = trimmedValue.toLowerCase()
                  break
                case 'nationality':
                  row.nationality = trimmedValue
                  break
                case 'employment type':
                case 'employment_type':
                  row.employment_type = trimmedValue.toLowerCase().replace(/\s+/g, '_')
                  break
                case 'work location':
                case 'work_location':
                  row.work_location = trimmedValue
                  break
                case 'hire date':
                case 'hire_date':
                  row.hire_date = trimmedValue
                  break
                case 'position':
                case 'department':
                  // Skip position and department - would need to lookup ID in system
                  break
              }
            })
            
            if (row.first_name && row.last_name && row.work_email) {
              // Remove any undefined fields that might cause validation errors
              Object.keys(row).forEach(key => {
                if (row[key] === undefined || row[key] === '') {
                  delete row[key]
                }
              })
              employees.push(row)
            }
          }

          resolve(employees)
        } catch (error) {
          reject(error)
        }
      }

      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsBinaryString(file)
    })
  }

  const handleImport = async () => {
    if (!file) return

    setUploading(true)
    setResult(null)

    try {
      const employees = await parseExcel(file)

      if (employees.length === 0) {
        setResult({
          success: 0,
          failed: 0,
          errors: ['No valid employee data found in the file. Please check the format.']
        })
        setUploading(false)
        return
      }

      const token = localStorage.getItem('access_token')
      if (!token) {
        setResult({
          success: 0,
          failed: employees.length,
          errors: ['Not authenticated. Please log in again.']
        })
        setUploading(false)
        return
      }

      let successCount = 0
      let failedCount = 0
      const errors: string[] = []

      // Import employees one by one
      for (let i = 0; i < employees.length; i++) {
        const employee = employees[i]
        try {
          const response = await fetch('http://localhost:8000/api/v1/employees/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(employee),
          })

          if (response.ok) {
            successCount++
          } else {
            const errorData = await response.json()
            failedCount++
            const errorMsg = errorData.error?.message || errorData.detail || 'Failed to import'
            errors.push(`Row ${i + 2}: ${errorMsg}`)
          }
        } catch (error) {
          failedCount++
          errors.push(`Row ${i + 2}: ${error instanceof Error ? error.message : 'Network error'}`)
        }
      }

      setResult({
        success: successCount,
        failed: failedCount,
        errors: errors.slice(0, 10) // Show only first 10 errors
      })

      if (successCount > 0) {
        onSuccess()
      }
    } catch (error) {
      setResult({
        success: 0,
        failed: 0,
        errors: ['Failed to read file. Please check the file format.']
      })
    }

    setUploading(false)
  }

  const handleClose = () => {
    setFile(null)
    setResult(null)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Import Employees from Excel</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>
                Download the template first, fill it with employee data, and upload the Excel file here.
                Required fields: <strong>First Name</strong>, <strong>Last Name</strong>, <strong>Work Email</strong>
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  exportEmployeeTemplate()
                  setResult({
                    success: 0,
                    failed: 0,
                    errors: [],
                    message: 'Template downloaded! Fill it out and upload the file here.'
                  })
                }}
                className="ml-4"
              >
                Download Template
              </Button>
            </AlertDescription>
          </Alert>

          {!file && !result && (
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm font-medium text-gray-700 mb-1">
                Drag and drop your Excel file here
              </p>
              <p className="text-xs text-gray-500 mb-4">or click to browse (.xlsx, .xls, .csv)</p>
              <Button type="button" variant="outline" size="sm">
                <Upload className="w-4 h-4 mr-2" />
                Select File
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv"
                className="hidden"
                onChange={handleFileSelect}
              />
            </div>
          )}

          {file && !result && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-8 h-8 text-green-600" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFile(null)}
                  disabled={uploading}
                >
                  Remove
                </Button>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 bg-green-50">
                  <div className="flex items-center gap-2 text-green-700 mb-1">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-semibold">Successful</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700">{result.success}</p>
                </div>
                <div className="border rounded-lg p-4 bg-red-50">
                  <div className="flex items-center gap-2 text-red-700 mb-1">
                    <XCircle className="w-5 h-5" />
                    <span className="font-semibold">Failed</span>
                  </div>
                  <p className="text-2xl font-bold text-red-700">{result.failed}</p>
                </div>
              </div>

              {result.errors.length > 0 && (
                <div className="border rounded-lg p-4 bg-red-50 max-h-48 overflow-y-auto">
                  <p className="text-sm font-semibold text-red-700 mb-2">Errors:</p>
                  <ul className="text-xs text-red-600 space-y-1">
                    {result.errors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                    {result.failed > result.errors.length && (
                      <li>• ... and {result.failed - result.errors.length} more errors</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2 justify-end pt-4">
            <Button variant="outline" onClick={handleClose}>
              {result ? 'Close' : 'Cancel'}
            </Button>
            {!result && (
              <Button onClick={handleImport} disabled={!file || uploading}>
                {uploading ? 'Importing...' : 'Import Employees'}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
