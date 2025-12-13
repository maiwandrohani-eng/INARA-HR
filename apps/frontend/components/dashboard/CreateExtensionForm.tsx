'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';
import { employeeFilesService, type EmploymentContract } from '@/services/employee-files.service';

interface CreateExtensionFormProps {
  contract: EmploymentContract;
  employeeId: string;
  employeeName: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export default function CreateExtensionForm({
  contract,
  employeeId,
  employeeName,
  onSuccess,
  onCancel,
}: CreateExtensionFormProps) {
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    new_start_date: contract.end_date,
    new_end_date: '',
    new_monthly_salary: contract.monthly_salary.toString(),
    salary_change_reason: '',
    new_position_title: contract.position_title,
    new_location: contract.location,
    terms_changes: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const extensionData = {
        contract_id: contract.id,
        employee_id: employeeId,
        new_start_date: formData.new_start_date,
        new_end_date: formData.new_end_date,
        new_monthly_salary:
          parseFloat(formData.new_monthly_salary) !== contract.monthly_salary
            ? parseFloat(formData.new_monthly_salary)
            : undefined,
        salary_change_reason:
          parseFloat(formData.new_monthly_salary) !== contract.monthly_salary
            ? formData.salary_change_reason
            : undefined,
        new_position_title:
          formData.new_position_title !== contract.position_title
            ? formData.new_position_title
            : undefined,
        new_location:
          formData.new_location !== contract.location ? formData.new_location : undefined,
        terms_changes: formData.terms_changes || undefined,
      };

      await employeeFilesService.createExtension(extensionData);
      alert('Contract extension created successfully!');
      onSuccess();
    } catch (error) {
      console.error('Failed to create extension:', error);
      alert('Failed to create extension. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Card className="border-blue-500">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Create Contract Extension for {employeeName}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-sm text-gray-500 mt-2">
          Extend contract {contract.contract_number} - Current period:{' '}
          {new Date(contract.start_date).toLocaleDateString()} to{' '}
          {new Date(contract.end_date).toLocaleDateString()}
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Period Section */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-4">Extension Period *</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Extend From (New Start Date) *
                </label>
                <input
                  type="date"
                  name="new_start_date"
                  value={formData.new_start_date}
                  onChange={handleChange}
                  required
                  className="w-full p-2 border rounded"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Usually the day after current contract ends
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Extend To (New End Date) *
                </label>
                <input
                  type="date"
                  name="new_end_date"
                  value={formData.new_end_date}
                  onChange={handleChange}
                  required
                  min={formData.new_start_date}
                  className="w-full p-2 border rounded"
                />
                <p className="text-xs text-gray-500 mt-1">Must be after start date</p>
              </div>
            </div>
          </div>

          {/* Compensation Changes */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-4">Compensation Changes (Optional)</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  New Monthly Salary ({contract.currency})
                </label>
                <input
                  type="number"
                  name="new_monthly_salary"
                  value={formData.new_monthly_salary}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  className="w-full p-2 border rounded"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Current: {contract.currency}{' '}
                  {parseFloat(contract.monthly_salary.toString()).toFixed(2)}/month
                </p>
              </div>

              {parseFloat(formData.new_monthly_salary) !== contract.monthly_salary && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Reason for Salary Change *
                  </label>
                  <textarea
                    name="salary_change_reason"
                    value={formData.salary_change_reason}
                    onChange={handleChange}
                    required
                    rows={2}
                    placeholder="e.g., Performance-based increase, Cost of living adjustment..."
                    className="w-full p-2 border rounded"
                  ></textarea>
                </div>
              )}
            </div>
          </div>

          {/* Position and Location Changes */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-4">Position & Location Changes (Optional)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Position Title</label>
                <input
                  type="text"
                  name="new_position_title"
                  value={formData.new_position_title}
                  onChange={handleChange}
                  className="w-full p-2 border rounded"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Current: {contract.position_title}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Work Location</label>
                <input
                  type="text"
                  name="new_location"
                  value={formData.new_location}
                  onChange={handleChange}
                  className="w-full p-2 border rounded"
                />
                <p className="text-xs text-gray-500 mt-1">Current: {contract.location}</p>
              </div>
            </div>
          </div>

          {/* Terms and Conditions Changes */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-4">Additional Terms Changes (Optional)</h3>
            <div>
              <label className="block text-sm font-medium mb-2">
                Changes to Terms & Conditions
              </label>
              <textarea
                name="terms_changes"
                value={formData.terms_changes}
                onChange={handleChange}
                rows={4}
                placeholder="Describe any changes to work conditions, responsibilities, supervisor, benefits, or other terms..."
                className="w-full p-2 border rounded"
              ></textarea>
              <p className="text-xs text-gray-500 mt-1">
                Include changes to reporting structure, benefits, working hours, etc.
              </p>
            </div>
          </div>

          {/* Info Alert */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> After creating this extension, the employee will receive
              a notification to review and accept the new terms. They will have 7 days before
              the new start date to accept the extension. If they don't accept, the extension
              will expire.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={submitting} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              {submitting ? 'Creating Extension...' : 'Create Extension'}
            </Button>
            <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
