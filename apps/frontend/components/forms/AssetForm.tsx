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
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Laptop } from 'lucide-react'

interface AssetFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function AssetForm({ open, onOpenChange, onSubmitSuccess }: AssetFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [assetName, setAssetName] = useState('')
  const [assetType, setAssetType] = useState('')
  const [category, setCategory] = useState('')
  const [manufacturer, setManufacturer] = useState('')
  const [model, setModel] = useState('')
  const [serialNumber, setSerialNumber] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [purchasePrice, setPurchasePrice] = useState('')
  const [location, setLocation] = useState('')
  const [status, setStatus] = useState('available')

  const resetForm = () => {
    setAssetName('')
    setAssetType('')
    setCategory('')
    setManufacturer('')
    setModel('')
    setSerialNumber('')
    setPurchaseDate('')
    setPurchasePrice('')
    setLocation('')
    setStatus('available')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const assetData = {
        asset_name: assetName,
        asset_type: assetType,
        category: category || null,
        manufacturer: manufacturer || null,
        model: model || null,
        serial_number: serialNumber || null,
        purchase_date: purchaseDate || null,
        purchase_price: purchasePrice ? parseFloat(purchasePrice) : null,
        location: location || null,
        status,
      }

      await apiClient.post('/assets/assets', assetData)

      toast({
        title: 'Success',
        description: 'Asset created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating asset:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create asset',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Laptop className="h-6 w-6" />
            Add Asset
          </DialogTitle>
          <DialogDescription>
            Register a new asset or equipment
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="asset-name">Asset Name *</Label>
              <Input
                id="asset-name"
                value={assetName}
                onChange={(e) => setAssetName(e.target.value)}
                placeholder="e.g., MacBook Pro 16"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="asset-type">Asset Type *</Label>
              <Select value={assetType} onValueChange={setAssetType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="laptop">Laptop</SelectItem>
                  <SelectItem value="phone">Phone</SelectItem>
                  <SelectItem value="monitor">Monitor</SelectItem>
                  <SelectItem value="printer">Printer</SelectItem>
                  <SelectItem value="tablet">Tablet</SelectItem>
                  <SelectItem value="vehicle">Vehicle</SelectItem>
                  <SelectItem value="furniture">Furniture</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g., IT, Office Equipment"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status *</Label>
              <Select value={status} onValueChange={setStatus} required>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">Available</SelectItem>
                  <SelectItem value="assigned">Assigned</SelectItem>
                  <SelectItem value="maintenance">Maintenance</SelectItem>
                  <SelectItem value="retired">Retired</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="manufacturer">Manufacturer</Label>
              <Input
                id="manufacturer"
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value)}
                placeholder="e.g., Apple, Dell"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Input
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="Model number"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="serial-number">Serial Number</Label>
              <Input
                id="serial-number"
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
                placeholder="Serial number"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Office location"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="purchase-date">Purchase Date</Label>
              <Input
                id="purchase-date"
                type="date"
                value={purchaseDate}
                onChange={(e) => setPurchaseDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="purchase-price">Purchase Price</Label>
              <Input
                id="purchase-price"
                type="number"
                step="0.01"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Asset'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

