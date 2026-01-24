'use client'

import { useState, useEffect } from 'react'
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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DollarSign, Plus, Edit, Trash2 } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface SalaryBand {
  id: string
  name: string
  level: number
  min_salary: number
  max_salary: number
  currency_code: string
  country_code?: string
  description?: string
  is_active: boolean
}

interface SalaryBandsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SalaryBandsDialog({ open, onOpenChange }: SalaryBandsDialogProps) {
  const [loading, setLoading] = useState(false)
  const [bands, setBands] = useState<SalaryBand[]>([])
  const [showAddBand, setShowAddBand] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  // Form state
  const [name, setName] = useState('')
  const [level, setLevel] = useState('1')
  const [minSalary, setMinSalary] = useState('')
  const [maxSalary, setMaxSalary] = useState('')
  const [currencyCode, setCurrencyCode] = useState('USD')
  const [countryCode, setCountryCode] = useState('ALL')
  const [description, setDescription] = useState('')

  useEffect(() => {
    if (open) {
      fetchBands()
    }
  }, [open])

  const fetchBands = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/compensation/salary-bands`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBands(data)
      }
    } catch (error) {
      console.error('Error fetching salary bands:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const min = parseFloat(minSalary)
      const max = parseFloat(maxSalary)

      if (max <= min) {
        alert('Maximum salary must be greater than minimum salary')
        setLoading(false)
        return
      }

      const bandData = {
        name,
        level: parseInt(level),
        min_salary: min,
        max_salary: max,
        currency_code: currencyCode,
        country_code: (countryCode && countryCode !== 'ALL') ? countryCode : null,
        description: description || null,
        is_active: true,
      }

      const token = localStorage.getItem('access_token')
      const url = editingId 
        ? `${API_BASE_URL}/compensation/salary-bands/${editingId}`
        : `${API_BASE_URL}/compensation/salary-bands`
      
      const response = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(bandData),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to save salary band')
      }

      alert(`Salary band ${editingId ? 'updated' : 'created'} successfully!`)
      setShowAddBand(false)
      setEditingId(null)
      resetForm()
      fetchBands()
    } catch (error) {
      console.error('Error saving salary band:', error)
      alert(`Failed to save: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (band: SalaryBand) => {
    setName(band.name)
    setLevel(band.level.toString())
    setMinSalary(band.min_salary.toString())
    setMaxSalary(band.max_salary.toString())
    setCurrencyCode(band.currency_code)
    setCountryCode(band.country_code || 'ALL')
    setDescription(band.description || '')
    setEditingId(band.id)
    setShowAddBand(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this salary band?')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/compensation/salary-bands/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Salary band deleted successfully')
        fetchBands()
      }
    } catch (error) {
      console.error('Error deleting salary band:', error)
      alert('Failed to delete salary band')
    }
  }

  const resetForm = () => {
    setName('')
    setLevel('1')
    setMinSalary('')
    setMaxSalary('')
    setCurrencyCode('USD')
    setCountryCode('ALL')
    setDescription('')
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Salary Bands
          </DialogTitle>
          <DialogDescription>
            Configure salary ranges for different job levels and positions
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!showAddBand ? (
            <div className="flex justify-end">
              <Button onClick={() => setShowAddBand(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Salary Band
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="border rounded-lg p-4 space-y-4">
              <h3 className="text-lg font-semibold">
                {editingId ? 'Edit' : 'Add'} Salary Band
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Band Name *</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Junior, Mid-Level, Senior"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="level">Level *</Label>
                  <Input
                    id="level"
                    type="number"
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                    min="1"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="min-salary">Minimum Salary *</Label>
                  <Input
                    id="min-salary"
                    type="number"
                    value={minSalary}
                    onChange={(e) => setMinSalary(e.target.value)}
                    min="0"
                    step="0.01"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max-salary">Maximum Salary *</Label>
                  <Input
                    id="max-salary"
                    type="number"
                    value={maxSalary}
                    onChange={(e) => setMaxSalary(e.target.value)}
                    min="0"
                    step="0.01"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Currency Code *</Label>
                  <Select value={currencyCode} onValueChange={setCurrencyCode} required>
                    <SelectTrigger id="currency">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD - US Dollar</SelectItem>
                      <SelectItem value="EUR">EUR - Euro</SelectItem>
                      <SelectItem value="GBP">GBP - British Pound</SelectItem>
                      <SelectItem value="TRY">TRY - Turkish Lira</SelectItem>
                      <SelectItem value="LBP">LBP - Lebanese Pound</SelectItem>
                      <SelectItem value="JOD">JOD - Jordanian Dinar</SelectItem>
                      <SelectItem value="EGP">EGP - Egyptian Pound</SelectItem>
                      <SelectItem value="IQD">IQD - Iraqi Dinar</SelectItem>
                      <SelectItem value="SYP">SYP - Syrian Pound</SelectItem>
                      <SelectItem value="AFN">AFN - Afghan Afghani</SelectItem>
                      <SelectItem value="YER">YER - Yemeni Rial</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country">Country (Optional)</Label>
                  <Select value={countryCode || undefined} onValueChange={(val) => setCountryCode(val)}>
                    <SelectTrigger id="country">
                      <SelectValue placeholder="All countries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ALL">All Countries</SelectItem>
                      <SelectItem value="AF">Afghanistan</SelectItem>
                      <SelectItem value="EG">Egypt</SelectItem>
                      <SelectItem value="IQ">Iraq</SelectItem>
                      <SelectItem value="JO">Jordan</SelectItem>
                      <SelectItem value="LB">Lebanon</SelectItem>
                      <SelectItem value="PS">Palestine</SelectItem>
                      <SelectItem value="SY">Syria</SelectItem>
                      <SelectItem value="TR">Turkey</SelectItem>
                      <SelectItem value="GB">United Kingdom</SelectItem>
                      <SelectItem value="YE">Yemen</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Brief description of this salary band"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Saving...' : editingId ? 'Update Band' : 'Create Band'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowAddBand(false)
                    setEditingId(null)
                    resetForm()
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {/* Bands List */}
          <div className="border rounded-lg">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">Salary Bands ({bands.length})</h3>
            </div>
            
            {loading && bands.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Loading salary bands...
              </div>
            ) : bands.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No salary bands configured. Add your first band above.
              </div>
            ) : (
              <div className="divide-y">
                {bands.sort((a, b) => a.level - b.level).map((band) => (
                  <div key={band.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                            Level {band.level}
                          </span>
                          <h4 className="font-semibold text-lg">{band.name}</h4>
                          {band.country_code && (
                            <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                              {band.country_code}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm mb-1">
                          <div>
                            <span className="text-gray-500">Range: </span>
                            <span className="font-semibold">
                              {formatCurrency(band.min_salary, band.currency_code)} - {formatCurrency(band.max_salary, band.currency_code)}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Midpoint: </span>
                            <span className="font-semibold">
                              {formatCurrency((band.min_salary + band.max_salary) / 2, band.currency_code)}
                            </span>
                          </div>
                        </div>
                        
                        {band.description && (
                          <p className="text-sm text-gray-600">{band.description}</p>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(band)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(band.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
