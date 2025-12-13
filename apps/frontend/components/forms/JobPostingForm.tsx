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
import { Textarea } from '@/components/ui/textarea'
import { Calendar, Briefcase } from 'lucide-react'

interface JobPostingFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function JobPostingForm({ open, onOpenChange }: JobPostingFormProps) {
  const [loading, setLoading] = useState(false)
  
  const [jobTitle, setJobTitle] = useState('')
  const [department, setDepartment] = useState('')
  const [location, setLocation] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [salaryRange, setSalaryRange] = useState('')
  const [closingDate, setClosingDate] = useState('')
  const [description, setDescription] = useState('')
  const [responsibilities, setResponsibilities] = useState('')
  const [qualifications, setQualifications] = useState('')
  const [benefits, setBenefits] = useState('')
  const [howToApply, setHowToApply] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const jobData = {
        job_title: jobTitle,
        department: department,
        location: location,
        employment_type: employmentType,
        salary_range: salaryRange,
        closing_date: closingDate,
        description: description,
        responsibilities: responsibilities,
        qualifications: qualifications,
        benefits: benefits,
        how_to_apply: howToApply,
        status: 'open',
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/jobs/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(jobData),
      })

      if (!response.ok) {
        throw new Error('Failed to create job posting')
      }

      alert('Job posting created successfully!')
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error creating job posting:', error)
      alert('Failed to create job posting. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setJobTitle('')
    setDepartment('')
    setLocation('')
    setEmploymentType('')
    setSalaryRange('')
    setClosingDate('')
    setDescription('')
    setResponsibilities('')
    setQualifications('')
    setBenefits('')
    setHowToApply('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Briefcase className="h-6 w-6" />
            Create Job Posting
          </DialogTitle>
          <DialogDescription>
            Post a new job opening to attract qualified candidates
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Basic Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="job-title">Job Title *</Label>
              <Input
                id="job-title"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g., Senior HR Manager, Project Coordinator"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="department">Department *</Label>
                <Input
                  id="department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g., Human Resources, Programs"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Location *</Label>
                <Select value={location} onValueChange={setLocation} required>
                  <SelectTrigger id="location">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Kabul">Kabul, Afghanistan</SelectItem>
                    <SelectItem value="Beirut">Beirut, Lebanon</SelectItem>
                    <SelectItem value="Cairo">Cairo, Egypt</SelectItem>
                    <SelectItem value="Gaza">Gaza, Palestine</SelectItem>
                    <SelectItem value="Damascus">Damascus, Syria</SelectItem>
                    <SelectItem value="Istanbul">Istanbul, Turkey</SelectItem>
                    <SelectItem value="London">London, United Kingdom</SelectItem>
                    <SelectItem value="Remote">Remote</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="employment-type">Employment Type *</Label>
                <Select value={employmentType} onValueChange={setEmploymentType} required>
                  <SelectTrigger id="employment-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="full_time">Full Time</SelectItem>
                    <SelectItem value="part_time">Part Time</SelectItem>
                    <SelectItem value="consultant">Consultant</SelectItem>
                    <SelectItem value="volunteer">Volunteer</SelectItem>
                    <SelectItem value="internship">Internship</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="salary-range">Salary Range</Label>
                <Input
                  id="salary-range"
                  value={salaryRange}
                  onChange={(e) => setSalaryRange(e.target.value)}
                  placeholder="e.g., $45,000 - $55,000"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="closing-date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Application Closing Date *
              </Label>
              <Input
                id="closing-date"
                type="date"
                value={closingDate}
                onChange={(e) => setClosingDate(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Job Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Job Details</h3>
            
            <div className="space-y-2">
              <Label htmlFor="description">Job Description *</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder="Provide an overview of the role, its purpose, and how it fits within the organization..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="responsibilities">Key Responsibilities *</Label>
              <Textarea
                id="responsibilities"
                value={responsibilities}
                onChange={(e) => setResponsibilities(e.target.value)}
                rows={6}
                placeholder="List the main duties and responsibilities (one per line)&#10;• Manage HR operations&#10;• Oversee recruitment processes&#10;• Develop training programs"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="qualifications">Required Qualifications *</Label>
              <Textarea
                id="qualifications"
                value={qualifications}
                onChange={(e) => setQualifications(e.target.value)}
                rows={6}
                placeholder="List required education, experience, skills, and competencies (one per line)&#10;• Bachelor's degree in relevant field&#10;• 5+ years of experience&#10;• Strong communication skills"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="benefits">Benefits & Perks</Label>
              <Textarea
                id="benefits"
                value={benefits}
                onChange={(e) => setBenefits(e.target.value)}
                rows={4}
                placeholder="Describe benefits, compensation package, and perks offered..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="how-to-apply">How to Apply *</Label>
              <Textarea
                id="how-to-apply"
                value={howToApply}
                onChange={(e) => setHowToApply(e.target.value)}
                rows={3}
                placeholder="Provide application instructions, required documents, and contact information..."
                required
              />
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> This job posting will be visible to all candidates. 
              Ensure all information is accurate and complies with employment regulations.
            </p>
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-pink-600 to-cyan-600 hover:from-pink-700 hover:to-cyan-700"
            >
              {loading ? 'Publishing...' : 'Publish Job Posting'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
