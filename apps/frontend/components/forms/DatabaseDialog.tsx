'use client'

import { useState } from 'react'
import { API_BASE_URL } from '@/lib/api-config'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Database, Download, Upload, RefreshCw, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface DatabaseDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function DatabaseDialog({ open, onOpenChange }: DatabaseDialogProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('')

  const handleBackup = async () => {
    setLoading(true)
    setMessage('')
    
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/admin/database/backup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to create database backup')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `inara_hris_backup_${new Date().toISOString().split('T')[0]}.sql`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setMessage('Database backup created and downloaded successfully!')
      setMessageType('success')
    } catch (error) {
      console.error('Error creating backup:', error)
      setMessage(`Failed to create backup: ${error instanceof Error ? error.message : 'Please try again'}`)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const handleRestore = async (file: File) => {
    if (!confirm('Are you sure you want to restore the database? This will overwrite all current data!')) {
      return
    }

    setLoading(true)
    setMessage('')
    
    try {
      const formData = new FormData()
      formData.append('file', file)

      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/admin/database/restore`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to restore database')
      }

      setMessage('Database restored successfully! Please refresh the page.')
      setMessageType('success')
    } catch (error) {
      console.error('Error restoring database:', error)
      setMessage(`Failed to restore database: ${error instanceof Error ? error.message : 'Please try again'}`)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleRestore(file)
    }
  }

  const handleOptimize = async () => {
    setLoading(true)
    setMessage('')
    
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/admin/database/optimize`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to optimize database')
      }

      setMessage('Database optimized successfully!')
      setMessageType('success')
    } catch (error) {
      console.error('Error optimizing database:', error)
      setMessage(`Failed to optimize database: ${error instanceof Error ? error.message : 'Please try again'}`)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Database className="h-6 w-6" />
            Database Management
          </DialogTitle>
          <DialogDescription>
            Backup, restore, and maintain your database
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {message && (
            <Alert variant={messageType === 'error' ? 'destructive' : 'default'}>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Download className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">Backup Database</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Create a complete backup of your database. This will download a SQL file containing all your data.
                  </p>
                  <Button 
                    onClick={handleBackup} 
                    disabled={loading}
                    variant="outline"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {loading ? 'Creating Backup...' : 'Create Backup'}
                  </Button>
                </div>
              </div>
            </div>

            <div className="border rounded-lg p-4 border-orange-200 bg-orange-50">
              <div className="flex items-start gap-3">
                <Upload className="w-5 h-5 text-orange-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold mb-1 text-orange-900">Restore Database</h3>
                  <p className="text-sm text-orange-800 mb-3">
                    Restore database from a backup file. <strong>Warning:</strong> This will overwrite all current data!
                  </p>
                  <div>
                    <input
                      type="file"
                      id="restore-file"
                      accept=".sql,.dump"
                      onChange={handleFileSelect}
                      className="hidden"
                      disabled={loading}
                    />
                    <Button 
                      onClick={() => document.getElementById('restore-file')?.click()}
                      disabled={loading}
                      variant="outline"
                      className="border-orange-300 text-orange-700 hover:bg-orange-100"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      {loading ? 'Restoring...' : 'Select Backup File'}
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <div className="flex items-start gap-3">
                <RefreshCw className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">Optimize Database</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Optimize database tables and rebuild indexes to improve performance.
                  </p>
                  <Button 
                    onClick={handleOptimize} 
                    disabled={loading}
                    variant="outline"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    {loading ? 'Optimizing...' : 'Optimize Now'}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">Best Practices</h4>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>Create regular backups before making major changes</li>
              <li>Store backup files in a secure, off-site location</li>
              <li>Test your backups periodically to ensure they work</li>
              <li>Optimize your database monthly for best performance</li>
              <li>Only restore backups in a controlled environment</li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
