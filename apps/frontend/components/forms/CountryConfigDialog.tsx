'use client'

import { useState, useEffect } from 'react'
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
import { Globe, Plus, Edit, Trash2 } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface CountryConfig {
  id: string
  country_code: string
  country_name: string
  default_currency: string
  timezone: string
  working_hours_per_week: number
  working_days_per_week: number
  public_holidays: string | null
  is_active: boolean
}

interface CountryConfigDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const COUNTRIES = [
  { code: 'AF', name: 'Afghanistan', currency: 'AFN', timezone: 'Asia/Kabul' },
  { code: 'AL', name: 'Albania', currency: 'ALL', timezone: 'Europe/Tirane' },
  { code: 'DZ', name: 'Algeria', currency: 'DZD', timezone: 'Africa/Algiers' },
  { code: 'AR', name: 'Argentina', currency: 'ARS', timezone: 'America/Argentina/Buenos_Aires' },
  { code: 'AM', name: 'Armenia', currency: 'AMD', timezone: 'Asia/Yerevan' },
  { code: 'AU', name: 'Australia', currency: 'AUD', timezone: 'Australia/Sydney' },
  { code: 'AT', name: 'Austria', currency: 'EUR', timezone: 'Europe/Vienna' },
  { code: 'AZ', name: 'Azerbaijan', currency: 'AZN', timezone: 'Asia/Baku' },
  { code: 'BH', name: 'Bahrain', currency: 'BHD', timezone: 'Asia/Bahrain' },
  { code: 'BD', name: 'Bangladesh', currency: 'BDT', timezone: 'Asia/Dhaka' },
  { code: 'BY', name: 'Belarus', currency: 'BYN', timezone: 'Europe/Minsk' },
  { code: 'BE', name: 'Belgium', currency: 'EUR', timezone: 'Europe/Brussels' },
  { code: 'BO', name: 'Bolivia', currency: 'BOB', timezone: 'America/La_Paz' },
  { code: 'BA', name: 'Bosnia and Herzegovina', currency: 'BAM', timezone: 'Europe/Sarajevo' },
  { code: 'BR', name: 'Brazil', currency: 'BRL', timezone: 'America/Sao_Paulo' },
  { code: 'BG', name: 'Bulgaria', currency: 'BGN', timezone: 'Europe/Sofia' },
  { code: 'KH', name: 'Cambodia', currency: 'KHR', timezone: 'Asia/Phnom_Penh' },
  { code: 'CM', name: 'Cameroon', currency: 'XAF', timezone: 'Africa/Douala' },
  { code: 'CA', name: 'Canada', currency: 'CAD', timezone: 'America/Toronto' },
  { code: 'CL', name: 'Chile', currency: 'CLP', timezone: 'America/Santiago' },
  { code: 'CN', name: 'China', currency: 'CNY', timezone: 'Asia/Shanghai' },
  { code: 'CO', name: 'Colombia', currency: 'COP', timezone: 'America/Bogota' },
  { code: 'CR', name: 'Costa Rica', currency: 'CRC', timezone: 'America/Costa_Rica' },
  { code: 'HR', name: 'Croatia', currency: 'EUR', timezone: 'Europe/Zagreb' },
  { code: 'CY', name: 'Cyprus', currency: 'EUR', timezone: 'Asia/Nicosia' },
  { code: 'CZ', name: 'Czech Republic', currency: 'CZK', timezone: 'Europe/Prague' },
  { code: 'DK', name: 'Denmark', currency: 'DKK', timezone: 'Europe/Copenhagen' },
  { code: 'EC', name: 'Ecuador', currency: 'USD', timezone: 'America/Guayaquil' },
  { code: 'EG', name: 'Egypt', currency: 'EGP', timezone: 'Africa/Cairo' },
  { code: 'SV', name: 'El Salvador', currency: 'USD', timezone: 'America/El_Salvador' },
  { code: 'EE', name: 'Estonia', currency: 'EUR', timezone: 'Europe/Tallinn' },
  { code: 'ET', name: 'Ethiopia', currency: 'ETB', timezone: 'Africa/Addis_Ababa' },
  { code: 'FI', name: 'Finland', currency: 'EUR', timezone: 'Europe/Helsinki' },
  { code: 'FR', name: 'France', currency: 'EUR', timezone: 'Europe/Paris' },
  { code: 'GE', name: 'Georgia', currency: 'GEL', timezone: 'Asia/Tbilisi' },
  { code: 'DE', name: 'Germany', currency: 'EUR', timezone: 'Europe/Berlin' },
  { code: 'GH', name: 'Ghana', currency: 'GHS', timezone: 'Africa/Accra' },
  { code: 'GR', name: 'Greece', currency: 'EUR', timezone: 'Europe/Athens' },
  { code: 'GT', name: 'Guatemala', currency: 'GTQ', timezone: 'America/Guatemala' },
  { code: 'HN', name: 'Honduras', currency: 'HNL', timezone: 'America/Tegucigalpa' },
  { code: 'HK', name: 'Hong Kong', currency: 'HKD', timezone: 'Asia/Hong_Kong' },
  { code: 'HU', name: 'Hungary', currency: 'HUF', timezone: 'Europe/Budapest' },
  { code: 'IS', name: 'Iceland', currency: 'ISK', timezone: 'Atlantic/Reykjavik' },
  { code: 'IN', name: 'India', currency: 'INR', timezone: 'Asia/Kolkata' },
  { code: 'ID', name: 'Indonesia', currency: 'IDR', timezone: 'Asia/Jakarta' },
  { code: 'IR', name: 'Iran', currency: 'IRR', timezone: 'Asia/Tehran' },
  { code: 'IQ', name: 'Iraq', currency: 'IQD', timezone: 'Asia/Baghdad' },
  { code: 'IE', name: 'Ireland', currency: 'EUR', timezone: 'Europe/Dublin' },
  { code: 'IL', name: 'Israel', currency: 'ILS', timezone: 'Asia/Jerusalem' },
  { code: 'IT', name: 'Italy', currency: 'EUR', timezone: 'Europe/Rome' },
  { code: 'JP', name: 'Japan', currency: 'JPY', timezone: 'Asia/Tokyo' },
  { code: 'JO', name: 'Jordan', currency: 'JOD', timezone: 'Asia/Amman' },
  { code: 'KZ', name: 'Kazakhstan', currency: 'KZT', timezone: 'Asia/Almaty' },
  { code: 'KE', name: 'Kenya', currency: 'KES', timezone: 'Africa/Nairobi' },
  { code: 'KW', name: 'Kuwait', currency: 'KWD', timezone: 'Asia/Kuwait' },
  { code: 'KG', name: 'Kyrgyzstan', currency: 'KGS', timezone: 'Asia/Bishkek' },
  { code: 'LA', name: 'Laos', currency: 'LAK', timezone: 'Asia/Vientiane' },
  { code: 'LV', name: 'Latvia', currency: 'EUR', timezone: 'Europe/Riga' },
  { code: 'LB', name: 'Lebanon', currency: 'LBP', timezone: 'Asia/Beirut' },
  { code: 'LY', name: 'Libya', currency: 'LYD', timezone: 'Africa/Tripoli' },
  { code: 'LT', name: 'Lithuania', currency: 'EUR', timezone: 'Europe/Vilnius' },
  { code: 'LU', name: 'Luxembourg', currency: 'EUR', timezone: 'Europe/Luxembourg' },
  { code: 'MY', name: 'Malaysia', currency: 'MYR', timezone: 'Asia/Kuala_Lumpur' },
  { code: 'MV', name: 'Maldives', currency: 'MVR', timezone: 'Indian/Maldives' },
  { code: 'ML', name: 'Mali', currency: 'XOF', timezone: 'Africa/Bamako' },
  { code: 'MT', name: 'Malta', currency: 'EUR', timezone: 'Europe/Malta' },
  { code: 'MX', name: 'Mexico', currency: 'MXN', timezone: 'America/Mexico_City' },
  { code: 'MD', name: 'Moldova', currency: 'MDL', timezone: 'Europe/Chisinau' },
  { code: 'MA', name: 'Morocco', currency: 'MAD', timezone: 'Africa/Casablanca' },
  { code: 'MZ', name: 'Mozambique', currency: 'MZN', timezone: 'Africa/Maputo' },
  { code: 'MM', name: 'Myanmar', currency: 'MMK', timezone: 'Asia/Yangon' },
  { code: 'NP', name: 'Nepal', currency: 'NPR', timezone: 'Asia/Kathmandu' },
  { code: 'NL', name: 'Netherlands', currency: 'EUR', timezone: 'Europe/Amsterdam' },
  { code: 'NZ', name: 'New Zealand', currency: 'NZD', timezone: 'Pacific/Auckland' },
  { code: 'NI', name: 'Nicaragua', currency: 'NIO', timezone: 'America/Managua' },
  { code: 'NG', name: 'Nigeria', currency: 'NGN', timezone: 'Africa/Lagos' },
  { code: 'MK', name: 'North Macedonia', currency: 'MKD', timezone: 'Europe/Skopje' },
  { code: 'NO', name: 'Norway', currency: 'NOK', timezone: 'Europe/Oslo' },
  { code: 'OM', name: 'Oman', currency: 'OMR', timezone: 'Asia/Muscat' },
  { code: 'PK', name: 'Pakistan', currency: 'PKR', timezone: 'Asia/Karachi' },
  { code: 'PS', name: 'Palestine', currency: 'ILS', timezone: 'Asia/Gaza' },
  { code: 'PA', name: 'Panama', currency: 'PAB', timezone: 'America/Panama' },
  { code: 'PY', name: 'Paraguay', currency: 'PYG', timezone: 'America/Asuncion' },
  { code: 'PE', name: 'Peru', currency: 'PEN', timezone: 'America/Lima' },
  { code: 'PH', name: 'Philippines', currency: 'PHP', timezone: 'Asia/Manila' },
  { code: 'PL', name: 'Poland', currency: 'PLN', timezone: 'Europe/Warsaw' },
  { code: 'PT', name: 'Portugal', currency: 'EUR', timezone: 'Europe/Lisbon' },
  { code: 'QA', name: 'Qatar', currency: 'QAR', timezone: 'Asia/Qatar' },
  { code: 'RO', name: 'Romania', currency: 'RON', timezone: 'Europe/Bucharest' },
  { code: 'RU', name: 'Russia', currency: 'RUB', timezone: 'Europe/Moscow' },
  { code: 'RW', name: 'Rwanda', currency: 'RWF', timezone: 'Africa/Kigali' },
  { code: 'SA', name: 'Saudi Arabia', currency: 'SAR', timezone: 'Asia/Riyadh' },
  { code: 'SN', name: 'Senegal', currency: 'XOF', timezone: 'Africa/Dakar' },
  { code: 'RS', name: 'Serbia', currency: 'RSD', timezone: 'Europe/Belgrade' },
  { code: 'SG', name: 'Singapore', currency: 'SGD', timezone: 'Asia/Singapore' },
  { code: 'SK', name: 'Slovakia', currency: 'EUR', timezone: 'Europe/Bratislava' },
  { code: 'SI', name: 'Slovenia', currency: 'EUR', timezone: 'Europe/Ljubljana' },
  { code: 'SO', name: 'Somalia', currency: 'SOS', timezone: 'Africa/Mogadishu' },
  { code: 'ZA', name: 'South Africa', currency: 'ZAR', timezone: 'Africa/Johannesburg' },
  { code: 'KR', name: 'South Korea', currency: 'KRW', timezone: 'Asia/Seoul' },
  { code: 'SS', name: 'South Sudan', currency: 'SSP', timezone: 'Africa/Juba' },
  { code: 'ES', name: 'Spain', currency: 'EUR', timezone: 'Europe/Madrid' },
  { code: 'LK', name: 'Sri Lanka', currency: 'LKR', timezone: 'Asia/Colombo' },
  { code: 'SD', name: 'Sudan', currency: 'SDG', timezone: 'Africa/Khartoum' },
  { code: 'SE', name: 'Sweden', currency: 'SEK', timezone: 'Europe/Stockholm' },
  { code: 'CH', name: 'Switzerland', currency: 'CHF', timezone: 'Europe/Zurich' },
  { code: 'SY', name: 'Syria', currency: 'SYP', timezone: 'Asia/Damascus' },
  { code: 'TW', name: 'Taiwan', currency: 'TWD', timezone: 'Asia/Taipei' },
  { code: 'TJ', name: 'Tajikistan', currency: 'TJS', timezone: 'Asia/Dushanbe' },
  { code: 'TZ', name: 'Tanzania', currency: 'TZS', timezone: 'Africa/Dar_es_Salaam' },
  { code: 'TH', name: 'Thailand', currency: 'THB', timezone: 'Asia/Bangkok' },
  { code: 'TN', name: 'Tunisia', currency: 'TND', timezone: 'Africa/Tunis' },
  { code: 'TR', name: 'Turkey', currency: 'TRY', timezone: 'Europe/Istanbul' },
  { code: 'TM', name: 'Turkmenistan', currency: 'TMT', timezone: 'Asia/Ashgabat' },
  { code: 'UG', name: 'Uganda', currency: 'UGX', timezone: 'Africa/Kampala' },
  { code: 'UA', name: 'Ukraine', currency: 'UAH', timezone: 'Europe/Kyiv' },
  { code: 'AE', name: 'United Arab Emirates', currency: 'AED', timezone: 'Asia/Dubai' },
  { code: 'GB', name: 'United Kingdom', currency: 'GBP', timezone: 'Europe/London' },
  { code: 'US', name: 'United States', currency: 'USD', timezone: 'America/New_York' },
  { code: 'UY', name: 'Uruguay', currency: 'UYU', timezone: 'America/Montevideo' },
  { code: 'UZ', name: 'Uzbekistan', currency: 'UZS', timezone: 'Asia/Tashkent' },
  { code: 'VE', name: 'Venezuela', currency: 'VES', timezone: 'America/Caracas' },
  { code: 'VN', name: 'Vietnam', currency: 'VND', timezone: 'Asia/Ho_Chi_Minh' },
  { code: 'YE', name: 'Yemen', currency: 'YER', timezone: 'Asia/Aden' },
  { code: 'ZM', name: 'Zambia', currency: 'ZMW', timezone: 'Africa/Lusaka' },
  { code: 'ZW', name: 'Zimbabwe', currency: 'ZWL', timezone: 'Africa/Harare' },
]

export function CountryConfigDialog({ open, onOpenChange }: CountryConfigDialogProps) {
  const [loading, setLoading] = useState(false)
  const [configs, setConfigs] = useState<CountryConfig[]>([])
  const [showAddConfig, setShowAddConfig] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  // Form state
  const [countryCode, setCountryCode] = useState('')
  const [currencyCode, setCurrencyCode] = useState('')
  const [timezone, setTimezone] = useState('')
  const [workingHours, setWorkingHours] = useState('40')
  const [workingDays, setWorkingDays] = useState('5')
  const [publicHolidays, setPublicHolidays] = useState('')

  useEffect(() => {
    if (open) {
      fetchConfigs()
    }
  }, [open])

  const fetchConfigs = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      console.log('Fetching country configs...')
      console.log('Token exists:', !!token)
      console.log('Token prefix:', token ? token.substring(0, 20) + '...' : 'none')
      
      if (!token) {
        console.error('No authentication token found')
        alert('Please log in again. No authentication token found.')
        setLoading(false)
        return
      }

      console.log('Making request to:', 'http://localhost:8000/api/v1/admin/countries')
      
      const response = await fetch('http://localhost:8000/api/v1/admin/countries', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      console.log('Response status:', response.status)
      console.log('Response ok:', response.ok)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Failed to fetch configs:', response.status, errorText)
        throw new Error(`Server error (${response.status}): ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Configs loaded:', data.length)
      setConfigs(data)
    } catch (error) {
      console.error('Error fetching country configs:', error)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        alert('Failed to connect to server. Please ensure the backend is running on port 8000.')
      } else {
        alert(`Failed to load country configurations: ${error instanceof Error ? error.message : 'Please try again'}`)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const selectedCountry = COUNTRIES.find(c => c.code === countryCode)
      if (!selectedCountry) {
        alert('Please select a country')
        setLoading(false)
        return
      }

      const configData = {
        country_code: countryCode,
        country_name: selectedCountry.name,
        default_currency: currencyCode,
        timezone: timezone,
        working_hours_per_week: parseFloat(workingHours),
        working_days_per_week: parseInt(workingDays),
        public_holidays: publicHolidays || null,
        is_active: true,
      }

      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const url = editingId 
        ? `http://localhost:8000/api/v1/admin/countries/${editingId}`
        : 'http://localhost:8000/api/v1/admin/countries'
      
      console.log('Saving country config to:', url)
      console.log('Method:', editingId ? 'PUT' : 'POST')
      console.log('Data:', configData)
      
      const response = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(configData),
      })

      console.log('Save response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Save failed:', response.status, errorText)
        let errorMessage = 'Failed to save country configuration'
        try {
          const error = JSON.parse(errorText)
          errorMessage = error.detail || errorMessage
          if (response.status === 403) {
            errorMessage = 'Access denied. You need admin permissions to manage country configurations.'
          }
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      alert(`Country configuration ${editingId ? 'updated' : 'created'} successfully!`)
      setShowAddConfig(false)
      setEditingId(null)
      resetForm()
      fetchConfigs()
    } catch (error) {
      console.error('Error saving country config:', error)
      alert(`Failed to save: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (config: CountryConfig) => {
    setCountryCode(config.country_code)
    setCurrencyCode(config.default_currency)
    setTimezone(config.timezone)
    setWorkingHours(config.working_hours_per_week.toString())
    setWorkingDays(config.working_days_per_week.toString())
    setPublicHolidays(config.public_holidays || '')
    setEditingId(config.id)
    setShowAddConfig(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this country configuration?')) return

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const response = await fetch(`http://localhost:8000/api/v1/admin/countries/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Delete failed:', response.status, errorText)
        let errorMessage = 'Failed to delete country configuration'
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      alert('Country configuration deleted successfully')
      await fetchConfigs()
    } catch (error) {
      console.error('Error deleting country config:', error)
      alert(`Failed to delete: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setCountryCode('')
    setCurrencyCode('')
    setTimezone('')
    setWorkingHours('40')
    setWorkingDays('5')
    setPublicHolidays('')
  }

  const handleCountryChange = (code: string) => {
    setCountryCode(code)
    const country = COUNTRIES.find(c => c.code === code)
    if (country) {
      setCurrencyCode(country.currency)
      setTimezone(country.timezone)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Globe className="h-6 w-6" />
            Country Configurations
          </DialogTitle>
          <DialogDescription>
            Configure country-specific employment settings
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!showAddConfig ? (
            <div className="flex justify-end">
              <Button onClick={() => setShowAddConfig(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Country Configuration
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="border rounded-lg p-4 space-y-4">
              <h3 className="text-lg font-semibold">
                {editingId ? 'Edit' : 'Add'} Country Configuration
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="country">Country *</Label>
                  <Select 
                    value={countryCode} 
                    onValueChange={handleCountryChange}
                    disabled={!!editingId}
                    required
                  >
                    <SelectTrigger id="country">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      {COUNTRIES.map((country) => (
                        <SelectItem key={country.code} value={country.code}>
                          {country.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Currency Code *</Label>
                  <Input
                    id="currency"
                    value={currencyCode}
                    onChange={(e) => setCurrencyCode(e.target.value)}
                    placeholder="USD, EUR, GBP..."
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone *</Label>
                  <Input
                    id="timezone"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    placeholder="Asia/Kabul, Europe/London..."
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="working-hours">Working Hours/Week *</Label>
                  <Input
                    id="working-hours"
                    type="number"
                    value={workingHours}
                    onChange={(e) => setWorkingHours(e.target.value)}
                    min="0"
                    max="168"
                    step="0.5"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="working-days">Working Days/Week *</Label>
                  <Input
                    id="working-days"
                    type="number"
                    value={workingDays}
                    onChange={(e) => setWorkingDays(e.target.value)}
                    min="1"
                    max="7"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="public-holidays">Public Holidays (Optional)</Label>
                  <Input
                    id="public-holidays"
                    value={publicHolidays}
                    onChange={(e) => setPublicHolidays(e.target.value)}
                    placeholder="New Year, Eid..."
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Saving...' : editingId ? 'Update Configuration' : 'Create Configuration'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowAddConfig(false)
                    setEditingId(null)
                    resetForm()
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {/* Configurations List */}
          <div className="border rounded-lg">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">Configured Countries ({configs.length})</h3>
            </div>
            
            {loading && configs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Loading configurations...
              </div>
            ) : configs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No country configurations found. Add your first configuration above.
              </div>
            ) : (
              <div className="divide-y">
                {configs.map((config) => (
                  <div key={config.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-lg">{config.country_name}</h4>
                          <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                            {config.country_code}
                          </span>
                          <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                            {config.default_currency}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div>
                            <p className="text-gray-500">Timezone</p>
                            <p className="font-semibold">{config.timezone}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Working Hours/Week</p>
                            <p className="font-semibold">{config.working_hours_per_week}h</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Working Days/Week</p>
                            <p className="font-semibold">{config.working_days_per_week} days</p>
                          </div>
                          {config.public_holidays && (
                            <div>
                              <p className="text-gray-500">Public Holidays</p>
                              <p className="font-semibold">{config.public_holidays}</p>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(config)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(config.id)}
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
