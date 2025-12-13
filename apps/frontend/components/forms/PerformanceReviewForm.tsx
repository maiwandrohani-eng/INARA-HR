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
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Calendar } from 'lucide-react'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface CompetencyRating {
  [key: string]: string
}

interface PerformanceReviewFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const competencies = [
  {
    category: 'Quality of Work',
    items: [
      'Sets high standards for quality of work output',
      'Seeks feedback to ensure high-quality work',
      'Helps others improve the quality of their work',
    ],
  },
  {
    category: 'Communication',
    items: [
      'Communicates well orally and in written-form',
      'Displays good listening skills',
      'Shares information freely with others',
    ],
  },
  {
    category: 'Team Work',
    items: [
      'Contributes positively to team',
      'Helps define team roles to maximize output',
      'Can be counted on to complete tasks correctly',
    ],
  },
  {
    category: 'Personal Qualifications and Leadership',
    items: [
      'Presents a positive image to outsiders',
      'Is friendly and easy to work with',
      'Adapts well to change',
      'Has high professional and ethical standards & is accountable',
      'Provides direction and instructions as and when required',
      'Is able to problem solve & make fair decisions',
      'Ensures that the INARA has a long-term strategy that achieves its mission and makes consistent and timely progress',
      'Demonstrates quality of analysis and judgment in program planning, implementation, and evaluation',
      'Executes legal documents appropriately, where required',
      'Assures adequate control and accounting of all funds, including developing and maintaining sound financial practices',
      'Works with the staff, Finance, and the board in preparing a budget and ensures that the organization operates within budget guidelines',
      'Establishes and makes use of an effective management team',
    ],
  },
  {
    category: 'Initiative',
    items: [
      'Recognizes opportunities and initiates actions to capitalize on them',
      'Looks for new and productive ways to make an impact',
      'Uses sound judgment on when to take action and when to seek guidance or approval',
    ],
  },
  {
    category: 'Innovative Thinking',
    items: [
      'Is on-the-lookout for new and innovative approaches that will improve efficiency',
      'Embraces and champions new ideas and encourages others to do likewise',
      'Recognizes and rewards people and teams who are creative and innovative',
    ],
  },
]

export function PerformanceReviewForm({
  open,
  onOpenChange,
}: PerformanceReviewFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()
  
  // Employee Information
  const [employeeId, setEmployeeId] = useState('')
  const [position, setPosition] = useState('')
  const [location, setLocation] = useState('')
  
  // Get selected employee details
  const selectedEmployee = employees.find(emp => emp.id === employeeId)
  
  // Assessor Information
  const [assessorName, setAssessorName] = useState('')
  const [assessorPosition, setAssessorPosition] = useState('')
  const [assessorLocation, setAssessorLocation] = useState('')
  const [relationToEmployee, setRelationToEmployee] = useState('')
  const [assessmentDate, setAssessmentDate] = useState(new Date().toISOString().split('T')[0])
  const [timeSpent, setTimeSpent] = useState('every-day')
  
  // Appraisal period
  const [appraisalStartDate, setAppraisalStartDate] = useState('')
  const [appraisalEndDate, setAppraisalEndDate] = useState('')
  
  // Competency ratings
  const [competencyRatings, setCompetencyRatings] = useState<CompetencyRating>({})
  const [competencyComments, setCompetencyComments] = useState<CompetencyRating>({})
  
  // Goals
  const [goalDescriptions, setGoalDescriptions] = useState<string[]>(['', '', '', '', '', '', ''])
  const [goalSelfAssessments, setGoalSelfAssessments] = useState<string[]>(['', '', '', '', '', '', ''])
  const [goalManagerAssessments, setGoalManagerAssessments] = useState<string[]>(['', '', '', '', '', '', ''])
  const [goalOverallRatings, setGoalOverallRatings] = useState<string[]>(['', '', '', '', '', '', ''])
  
  // Overall rating and comments
  const [overallRating, setOverallRating] = useState('')
  const [employeeSummary, setEmployeeSummary] = useState('')
  const [managerSummary, setManagerSummary] = useState('')

  const updateCompetencyRating = (category: string, item: string, rating: string) => {
    const key = `${category}:${item}`
    setCompetencyRatings({ ...competencyRatings, [key]: rating })
  }

  const updateCompetencyComment = (category: string, comment: string) => {
    setCompetencyComments({ ...competencyComments, [category]: comment })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const reviewData = {
        employee_id: employeeId,
        employee_name: selectedEmployee ? getEmployeeFullName(selectedEmployee) : '',
        position,
        location,
        assessor_name: assessorName,
        assessor_position: assessorPosition,
        assessor_location: assessorLocation,
        relation_to_employee: relationToEmployee,
        assessment_date: assessmentDate,
        time_spent: timeSpent,
        appraisal_start_date: appraisalStartDate,
        appraisal_end_date: appraisalEndDate,
        competency_ratings: competencyRatings,
        competency_comments: competencyComments,
        goals: goalDescriptions.map((desc, i) => ({
          description: desc,
          self_assessment: goalSelfAssessments[i],
          manager_assessment: goalManagerAssessments[i],
          overall_rating: goalOverallRatings[i],
        })),
        overall_rating: overallRating,
        employee_summary: employeeSummary,
        manager_summary: managerSummary,
        status: 'draft',
      }

      const response = await fetch(
        'http://localhost:8000/api/v1/performance/reviews',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(reviewData),
        }
      )

      if (!response.ok) {
        throw new Error('Failed to submit performance review')
      }

      alert('Performance review submitted successfully!')
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error submitting performance review:', error)
      alert('Failed to submit performance review. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setPosition('')
    setLocation('')
    setAssessorName('')
    setAssessorPosition('')
    setAssessorLocation('')
    setRelationToEmployee('')
    setAssessmentDate(new Date().toISOString().split('T')[0])
    setTimeSpent('every-day')
    setAppraisalStartDate('')
    setAppraisalEndDate('')
    setCompetencyRatings({})
    setCompetencyComments({})
    setGoalDescriptions(['', '', '', '', '', '', ''])
    setGoalSelfAssessments(['', '', '', '', '', '', ''])
    setGoalManagerAssessments(['', '', '', '', '', '', ''])
    setGoalOverallRatings(['', '', '', '', '', '', ''])
    setOverallRating('')
    setEmployeeSummary('')
    setManagerSummary('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center">
            360-DEGREE PERFORMANCE EVALUATION FORM
          </DialogTitle>
          <DialogDescription className="text-center text-sm italic">
            Private & confidential
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Instructions */}
          <div className="border-l-4 border-blue-500 bg-blue-50 p-4 space-y-3">
            <h3 className="font-semibold text-blue-900">Instructions</h3>
            <ul className="list-disc list-inside space-y-2 text-sm text-gray-700">
              <li>Complete the Employee, Position, Performance Period, and Manager fields.</li>
              <li>
                <strong>Goal Setting</strong>
                <ul className="list-disc list-inside ml-5 mt-1 space-y-1">
                  <li>Complete <strong>Description of Goal</strong> and <strong>Criteria for Measurement</strong> fields for each goal.</li>
                </ul>
              </li>
              <li>
                <strong>Performance Review</strong>
                <ul className="list-disc list-inside ml-5 mt-1 space-y-1">
                  <li>Employee: Complete Self-Assessment and select a Rating for each goal.</li>
                  <li>Manager: Complete Manager-Assessment and select a Rating for each goal. Select Overall Rating.</li>
                </ul>
              </li>
              <li>Employee & Manager: Add Summary Comments.</li>
              <li>Obtain appropriate signatures before filing documents.</li>
            </ul>
          </div>

          {/* Appraisal Period */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="font-semibold mb-3">Appraisal Period</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="appraisal-start-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Start Date:
                </Label>
                <Input
                  id="appraisal-start-date"
                  type="date"
                  value={appraisalStartDate}
                  onChange={(e) => setAppraisalStartDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="appraisal-end-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  End Date:
                </Label>
                <Input
                  id="appraisal-end-date"
                  type="date"
                  value={appraisalEndDate}
                  onChange={(e) => setAppraisalEndDate(e.target.value)}
                  required
                />
              </div>
            </div>
            <p className="text-xs text-gray-600 italic mt-3">
              As someone who routinely works with this person, your feedback on his or her performance will
              be valuable to the overall review process. Your identity will remain confidential and will not be
              disclosed.
            </p>
          </div>

          {/* Employee Information */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-blue-100 px-4 py-2 font-semibold">
              EMPLOYEE INFORMATION
            </div>
            <div className="grid grid-cols-2 gap-4 p-4">
              <div className="space-y-2">
                <Label htmlFor="employee-name">Name</Label>
                <Select value={employeeId} onValueChange={setEmployeeId} required>
                  <SelectTrigger id="employee-name">
                    <SelectValue placeholder={employeesLoading ? "Loading employees..." : "Select employee"} />
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
              <div className="space-y-2">
                <Label htmlFor="position">Position:</Label>
                <Input
                  id="position"
                  value={selectedEmployee?.work_location || position}
                  onChange={(e) => setPosition(e.target.value)}
                  placeholder="Position"
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={selectedEmployee?.work_location || location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Office Location"
                />
              </div>
            </div>
          </div>

          {/* Assessor Information */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-blue-100 px-4 py-2 font-semibold">
              ASSESSOR INFORMATION
            </div>
            <div className="grid grid-cols-2 gap-4 p-4">
              <div className="space-y-2">
                <Label htmlFor="assessor-name">Name of the Assessor:</Label>
                <Input
                  id="assessor-name"
                  value={assessorName}
                  onChange={(e) => setAssessorName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="assessor-position">Position:</Label>
                <Input
                  id="assessor-position"
                  value={assessorPosition}
                  onChange={(e) => setAssessorPosition(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="assessor-location">Location</Label>
                <Input
                  id="assessor-location"
                  value={assessorLocation}
                  onChange={(e) => setAssessorLocation(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="relation">Relation to Employee</Label>
                <Select value={relationToEmployee} onValueChange={setRelationToEmployee} required>
                  <SelectTrigger id="relation">
                    <SelectValue placeholder="Select relation" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="peer">Peer</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="subordinate">Subordinate</SelectItem>
                    <SelectItem value="beneficiaries">Beneficiaries</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Date:
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={assessmentDate}
                  onChange={(e) => setAssessmentDate(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Time Spent - Your interaction with an employee</Label>
                <Select value={timeSpent} onValueChange={setTimeSpent} required>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="every-day">Every Day</SelectItem>
                    <SelectItem value="few-times-week">A few times a week</SelectItem>
                    <SelectItem value="few-times-month">A few times a month</SelectItem>
                    <SelectItem value="every-few-months">Every few months</SelectItem>
                    <SelectItem value="never">N.A. (Never)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Rating Definition */}
          <div className="border rounded-lg p-4 bg-gray-50 text-xs space-y-2">
            <h3 className="font-semibold">Rating Definition</h3>
            <div><strong>EXCEPTIONAL (5):</strong> Consistently exceeds all relevant performance standards. Provides leadership, fosters teamwork, is highly productive, innovative, responsive, and generates top-quality work.</div>
            <div><strong>EXCEEDS EXPECTATIONS (4):</strong> Consistently meets and often exceeds all relevant performance standards. Shows initiative and versatility, works collaboratively, has strong technical & interpersonal skills, or has achieved significant improvement in these areas.</div>
            <div><strong>MEETS EXPECTATIONS (3):</strong> Meets all relevant performance standards. Seldom exceeds or falls short of desired results or objectives.</div>
            <div><strong>BELOW EXPECTATIONS (2):</strong> Sometimes meets the performance standards. Seldom exceeds and often falls short of desired results. Performance has declined significantly, or the employee has not sustained adequate improvement, as required, since the last performance review or performance.</div>
            <div><strong>NEEDS IMPROVEMENT (1):</strong> Consistently falls short of performance standards.</div>
          </div>

          {/* Competencies */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-gray-200 px-4 py-2">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left font-semibold py-2">COMPETENCIES</th>
                    <th className="text-center w-20 font-semibold">Exception al (5)</th>
                    <th className="text-center w-20 font-semibold">Exceeds Exp (4)</th>
                    <th className="text-center w-20 font-semibold">Meets Exp (3)</th>
                    <th className="text-center w-20 font-semibold">Below Exp (2)</th>
                    <th className="text-center w-20 font-semibold">Needs Impro vement (1)</th>
                  </tr>
                </thead>
              </table>
            </div>

            <div className="divide-y">
              {competencies.map((section) => (
                <div key={section.category} className="p-4 space-y-3">
                  <h4 className="font-semibold">{section.category}</h4>
                  <div className="space-y-2">
                    {section.items.map((item) => {
                      const key = `${section.category}:${item}`
                      return (
                        <div key={item} className="flex items-center gap-2">
                          <span className="flex-1 text-sm">{item}</span>
                          <div className="flex gap-4">
                            {['5', '4', '3', '2', '1'].map((rating) => (
                              <label key={rating} className="flex items-center justify-center w-12">
                                <input
                                  type="checkbox"
                                  checked={competencyRatings[key] === rating}
                                  onChange={() => updateCompetencyRating(section.category, item, rating)}
                                  className="h-4 w-4"
                                />
                              </label>
                            ))}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <div className="space-y-1">
                    <Label className="text-sm font-semibold">Your comments</Label>
                    <Textarea
                      value={competencyComments[section.category] || ''}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                        updateCompetencyComment(section.category, e.target.value)
                      }
                      rows={2}
                      className="text-sm"
                      placeholder="Add your comments..."
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Goals and Performance Objectives */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-blue-100 px-4 py-2 font-semibold text-center">
              GOALS AND PERFORMANCE OBJECTIVES (Can be changed in midyear or check-in)
            </div>
            
            {/* Guidance for Writing Performance Goals */}
            <div className="bg-yellow-50 border-b p-4 space-y-3 text-sm">
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Guidance for Writing Performance Goals</h4>
                
                <div className="space-y-2">
                  <div>
                    <strong className="text-gray-700">What are goals?</strong>
                    <p className="text-gray-600 ml-4">Goals are statements of end results expected within a specified period of time.</p>
                  </div>
                  
                  <div>
                    <strong className="text-gray-700">How do I write a goal?</strong>
                    <p className="text-gray-600 ml-4">A goal should include the following three elements:</p>
                    <ol className="list-decimal ml-8 mt-1 space-y-1 text-gray-600">
                      <li><strong>The goal</strong>—the results you plan to achieve and how it links to the project, departmental or organizational priorities (for example, increase growth, improve quality, or improve staff effectiveness.)</li>
                      <li><strong>Measurement criteria</strong> (or indicators) — the measures or milestones that enable you or others to assess your progress toward the achievement of the intended results.</li>
                      <li><strong>A timeline</strong>—a "by when" date.</li>
                    </ol>
                  </div>
                  
                  <div>
                    <p className="text-gray-600 ml-4">After you have written your goal, check it to make sure it passes the SMART test:</p>
                    <ul className="list-disc ml-8 mt-1 space-y-1 text-gray-600">
                      <li><strong>Specific:</strong> What is the desired result? What is the difference you are going to make?</li>
                      <li><strong>Measurable:</strong> What are your milestones, indicators of success? How can you measure progress?</li>
                      <li><strong>Achievable/Attainable:</strong> What skills and resources are needed? Do you have them?</li>
                      <li><strong>Relevant:</strong> What are your milestones aligned with department or organizational priorities?</li>
                      <li><strong>Time-bound:</strong> What is the deadline? Is the deadline realistic?</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left font-semibold border">
                      Description of Goal
                      <div className="text-xs font-normal italic text-gray-600">
                        Establish goals that will be key accomplishments expected for the performance period.
                      </div>
                    </th>
                    <th className="px-4 py-2 text-center font-semibold border w-40">Self Assessment</th>
                    <th className="px-4 py-2 text-center font-semibold border w-40">Managers Assessment</th>
                    <th className="px-4 py-2 text-center font-semibold border w-32">Overall</th>
                  </tr>
                </thead>
                <tbody>
                  {[0, 1, 2, 3, 4, 5, 6].map((index) => (
                    <tr key={index} className="border-b">
                      <td className="px-4 py-2 border">
                        <Input
                          value={goalDescriptions[index]}
                          onChange={(e) => {
                            const newGoals = [...goalDescriptions]
                            newGoals[index] = e.target.value
                            setGoalDescriptions(newGoals)
                          }}
                          placeholder="Enter goal description..."
                          className="border-0 focus-visible:ring-0 text-sm"
                        />
                      </td>
                      <td className="px-4 py-2 border">
                        <Select
                          value={goalSelfAssessments[index]}
                          onValueChange={(value: string) => {
                            const newAssessments = [...goalSelfAssessments]
                            newAssessments[index] = value
                            setGoalSelfAssessments(newAssessments)
                          }}
                        >
                          <SelectTrigger className="text-sm h-8">
                            <SelectValue placeholder="Choose" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="exceptional">Exceptional (5)</SelectItem>
                            <SelectItem value="exceeds">Exceeds Exp (4)</SelectItem>
                            <SelectItem value="meets">Meets Exp (3)</SelectItem>
                            <SelectItem value="below">Below Exp (2)</SelectItem>
                            <SelectItem value="needs">Needs Improvement (1)</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                      <td className="px-4 py-2 border">
                        <Select
                          value={goalManagerAssessments[index]}
                          onValueChange={(value: string) => {
                            const newAssessments = [...goalManagerAssessments]
                            newAssessments[index] = value
                            setGoalManagerAssessments(newAssessments)
                          }}
                        >
                          <SelectTrigger className="text-sm h-8">
                            <SelectValue placeholder="Choose" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="exceptional">Exceptional (5)</SelectItem>
                            <SelectItem value="exceeds">Exceeds Exp (4)</SelectItem>
                            <SelectItem value="meets">Meets Exp (3)</SelectItem>
                            <SelectItem value="below">Below Exp (2)</SelectItem>
                            <SelectItem value="needs">Needs Improvement (1)</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                      <td className="px-4 py-2 border">
                        <Select
                          value={goalOverallRatings[index]}
                          onValueChange={(value: string) => {
                            const newRatings = [...goalOverallRatings]
                            newRatings[index] = value
                            setGoalOverallRatings(newRatings)
                          }}
                        >
                          <SelectTrigger className="text-sm h-8">
                            <SelectValue placeholder="Choose" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="exceptional">Exceptional (5)</SelectItem>
                            <SelectItem value="exceeds">Exceeds Exp (4)</SelectItem>
                            <SelectItem value="meets">Meets Exp (3)</SelectItem>
                            <SelectItem value="below">Below Exp (2)</SelectItem>
                            <SelectItem value="needs">Needs Improvement (1)</SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Overall Rating */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-gray-100 px-4 py-3 font-semibold">
              OVERALL RATING
            </div>
            
            {/* Rating Descriptions */}
            <div className="bg-gray-50 border-b p-4 space-y-2 text-xs">
              <h4 className="font-semibold text-gray-800 mb-2">RATING DESCRIPTIONS</h4>
              
              <div className="space-y-2">
                <div>
                  <strong className="text-gray-700">Option 3</strong>
                  <ul className="list-disc ml-5 mt-1 text-gray-600">
                    <li>Sets the standard for high performance in the group. Sets high goals. Exceeds agreed-upon performance goals. Makes significant contributions to improving organizational efficiency and effectiveness.</li>
                  </ul>
                </div>
                
                <div>
                  <strong className="text-gray-700">Option 2</strong>
                  <ul className="list-disc ml-5 mt-1 text-gray-600">
                    <li>Meets all or the majority of agreed-upon performance goals. Is self-directed in accomplishing work according to expected standards and timelines. Makes strong contributions to improving organizational efficiency and effectiveness.</li>
                  </ul>
                </div>
                
                <div>
                  <strong className="text-gray-700">Option 1</strong>
                  <ul className="list-disc ml-5 mt-1 text-gray-600">
                    <li>Meets some or a few of the agreed-upon performance goals. Requires guidance to complete work according to expected standards and timelines. Makes limited or no contributions to improving organizational efficiency and effectiveness. *If very few or no goals were met, a Performance Improvement Plan (PIP) is strongly advised.</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="p-4">
              <Select value={overallRating} onValueChange={setOverallRating} required>
                <SelectTrigger>
                  <SelectValue placeholder="Choose an item" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="option3">Option 3 - Sets the standard for high performance</SelectItem>
                  <SelectItem value="option2">Option 2 - Meets all or the majority of agreed-upon performance goals</SelectItem>
                  <SelectItem value="option1">Option 1 - Meets some or a few of the agreed-upon performance goals</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Summary Comments */}
          <div className="grid grid-cols-2 gap-4 border rounded-lg overflow-hidden">
            <div className="border-r">
              <div className="bg-gray-100 px-4 py-2 font-semibold text-center">
                EMPLOYEE SUMMARY COMMENT
              </div>
              <div className="bg-blue-50 border-b px-4 py-2 text-xs">
                <h5 className="font-semibold text-gray-800 mb-2">Guidance for Writing Performance Reviews</h5>
                <p className="text-gray-600 mb-2">
                  The annual performance review is an opportunity to formally document your performance and review it 
                  with your manager, making the most of your talents and contributions while ensuring alignment with 
                  team and organizational priorities. Use the following steps as a guide:
                </p>
                <ol className="list-decimal ml-5 space-y-1 text-gray-600">
                  <li>Review your annual goals and accomplishments, using your goals and other documents as well.</li>
                  <li>Complete the self-assessment of your annual performance.</li>
                  <li>Provide an overall performance rating, and submit the completed assessment to your manager.</li>
                </ol>
                <p className="text-gray-600 mt-2 italic">
                  <strong>The following optional guidance is recommended but not required.</strong>
                </p>
                <p className="text-gray-600 mt-2">
                  For each goal, it is recommended that the employee writes four assessment statements, and the 
                  manager writes four corresponding statements, including:
                </p>
                <ol className="list-decimal ml-5 mt-1 space-y-1 text-gray-600">
                  <li>One statement describing if the goal was achieved (were all the <strong>elements accomplished</strong>?)</li>
                  <li>One statement on <strong>the impact</strong> it had on your department/function overall, and your specific contribution toward that end</li>
                  <li>One statement regarding <strong>the learning you will take forward</strong> into next year</li>
                  <li>One statement on the <strong>organizational values demonstrated</strong> while achieving these results (Innovation, Mutual respect, Accountability, Commitment to excellence, Teamwork)</li>
                </ol>
              </div>
              <div className="p-4">
                <Textarea
                  value={employeeSummary}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setEmployeeSummary(e.target.value)}
                  rows={8}
                  placeholder="Employee's summary comments..."
                  className="resize-none"
                />
              </div>
            </div>
            <div>
              <div className="bg-gray-100 px-4 py-2 font-semibold text-center">
                MANAGER SUMMARY COMMENT
              </div>
              <div className="bg-blue-50 border-b px-4 py-2 text-xs">
                <p className="text-gray-600 italic mb-2">
                  Use the same guidance as shown in the employee section to provide comprehensive feedback.
                </p>
                <p className="text-gray-600">
                  For each goal, provide assessment addressing:
                </p>
                <ol className="list-decimal ml-5 mt-1 space-y-1 text-gray-600">
                  <li>Elements accomplished</li>
                  <li>Impact on department/organization</li>
                  <li>Learning and growth opportunities</li>
                  <li>Organizational values demonstrated</li>
                </ol>
              </div>
              <div className="p-4">
                <Textarea
                  value={managerSummary}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setManagerSummary(e.target.value)}
                  rows={8}
                  placeholder="Manager's summary comments..."
                  className="resize-none"
                />
              </div>
            </div>
          </div>

          {/* Signatures Note */}
          <div className="border rounded-lg p-4 bg-gray-50 text-xs italic">
            <strong>SIGNATURES:</strong> The signature indicates that the content of this assessment has been reviewed with the
            employee but does not necessarily signify agreement with the content.
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
              {loading ? 'Submitting...' : 'Submit Review'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
