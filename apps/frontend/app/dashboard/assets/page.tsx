/**
 * Asset/Equipment Management Page
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { AssetForm } from '@/components/forms/AssetForm'

export default function AssetsPage() {
  const [assets, setAssets] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddAsset, setShowAddAsset] = useState(false)

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const response = await apiClient.get('/assets/assets')
      setAssets(response.data)
    } catch (error) {
      console.error('Failed to fetch assets:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Asset Management</h1>
          <p className="text-gray-600 mt-2">Track IT assets, equipment, and assignments</p>
        </div>
        <Button onClick={() => setShowAddAsset(true)}>Add Asset</Button>
      </div>

      <AssetForm 
        open={showAddAsset} 
        onOpenChange={setShowAddAsset}
        onSubmitSuccess={fetchAssets}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assets.map((asset) => (
            <Card key={asset.id}>
              <CardHeader>
                <CardTitle>{asset.asset_name}</CardTitle>
                <CardDescription>{asset.asset_number}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm"><strong>Type:</strong> {asset.asset_type}</p>
                  <p className="text-sm"><strong>Status:</strong> {asset.status}</p>
                  {asset.serial_number && (
                    <p className="text-sm"><strong>Serial:</strong> {asset.serial_number}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

