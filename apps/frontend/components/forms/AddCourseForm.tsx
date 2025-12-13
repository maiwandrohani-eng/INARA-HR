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
import { Calendar, GraduationCap } from 'lucide-react'

interface AddCourseFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AddCourseForm({ open, onOpenChange }: AddCourseFormProps) {
  const [loading, setLoading] = useState(false)
  
  const [courseName, setCourseName] = useState('')
  const [category, setCategory] = useState('')
  const [instructor, setInstructor] = useState('')
  const [duration, setDuration] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [location, setLocation] = useState('')
  const [deliveryMode, setDeliveryMode] = useState('')
  const [maxParticipants, setMaxParticipants] = useState('')
  const [description, setDescription] = useState('')
  const [objectives, setObjectives] = useState('')
  const [prerequisites, setPrerequisites] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const courseData = {
        course_name: courseName,
        category: category,
        instructor: instructor,
        duration: duration,
        start_date: startDate,
        end_date: endDate,
        location: location,
        delivery_mode: deliveryMode,
        max_participants: parseInt(maxParticipants),
        description: description,
        objectives: objectives,
        prerequisites: prerequisites,
        status: 'active',
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/courses/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(courseData),
      })

      if (!response.ok) {
        throw new Error('Failed to create course')
      }

      alert('Course created successfully!')
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error creating course:', error)
      alert('Failed to create course. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setCourseName('')
    setCategory('')
    setInstructor('')
    setDuration('')
    setStartDate('')
    setEndDate('')
    setLocation('')
    setDeliveryMode('')
    setMaxParticipants('')
    setDescription('')
    setObjectives('')
    setPrerequisites('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            Add Training Course
          </DialogTitle>
          <DialogDescription>
            Create a new training course or learning program
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Course Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Course Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="course-name">Course Name *</Label>
              <Input
                id="course-name"
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
                placeholder="e.g., Leadership Development, Child Protection Training"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select value={category} onValueChange={setCategory} required>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="leadership">Leadership & Management</SelectItem>
                    <SelectItem value="technical">Technical Skills</SelectItem>
                    <SelectItem value="safeguarding">Safeguarding & Protection</SelectItem>
                    <SelectItem value="compliance">Compliance & Ethics</SelectItem>
                    <SelectItem value="communication">Communication Skills</SelectItem>
                    <SelectItem value="project_management">Project Management</SelectItem>
                    <SelectItem value="hr">Human Resources</SelectItem>
                    <SelectItem value="finance">Finance & Budgeting</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="instructor">Instructor/Facilitator *</Label>
                <Input
                  id="instructor"
                  value={instructor}
                  onChange={(e) => setInstructor(e.target.value)}
                  placeholder="Name of instructor"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="duration">Duration *</Label>
                <Input
                  id="duration"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g., 3 days, 2 weeks"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="start-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Start Date *
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="end-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  End Date *
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="delivery-mode">Delivery Mode *</Label>
                <Select value={deliveryMode} onValueChange={setDeliveryMode} required>
                  <SelectTrigger id="delivery-mode">
                    <SelectValue placeholder="Select mode" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="in_person">In-Person</SelectItem>
                    <SelectItem value="online">Online</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                    <SelectItem value="self_paced">Self-Paced</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., Training Room A, Zoom, Online"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-participants">Maximum Participants</Label>
              <Input
                id="max-participants"
                type="number"
                value={maxParticipants}
                onChange={(e) => setMaxParticipants(e.target.value)}
                placeholder="e.g., 25"
              />
            </div>
          </div>

          {/* Course Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Course Details</h3>
            
            <div className="space-y-2">
              <Label htmlFor="description">Course Description *</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder="Provide an overview of what this course covers and who it's for..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="objectives">Learning Objectives *</Label>
              <Textarea
                id="objectives"
                value={objectives}
                onChange={(e) => setObjectives(e.target.value)}
                rows={5}
                placeholder="List what participants will learn (one per line)&#10;• Understand key leadership principles&#10;• Develop effective communication skills&#10;• Learn to manage teams effectively"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="prerequisites">Prerequisites (if any)</Label>
              <Textarea
                id="prerequisites"
                value={prerequisites}
                onChange={(e) => setPrerequisites(e.target.value)}
                rows={3}
                placeholder="Any requirements or prior knowledge needed to attend this course..."
              />
            </div>
          </div>

          {/* Notice */}
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-sm text-green-800">
              <strong>Note:</strong> After creating the course, you can enroll participants 
              and track their progress through the course management dashboard.
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
              {loading ? 'Creating...' : 'Create Course'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
