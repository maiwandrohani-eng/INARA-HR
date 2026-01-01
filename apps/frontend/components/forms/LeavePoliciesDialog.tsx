"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings, Plus, Pencil, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";

interface LeavePolicy {
  id: string;
  name: string;
  leave_type: string;
  days_per_year: number;
  accrual_rate: string | null;
  max_carryover: number | null;
  requires_approval: boolean;
  description: string | null;
  country_code: string;
  created_at: string;
}

interface LeavePoliciesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LeavePoliciesDialog({ open, onOpenChange }: LeavePoliciesDialogProps) {
  const { toast } = useToast();
  const [policies, setPolicies] = useState<LeavePolicy[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<LeavePolicy | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [leaveType, setLeaveType] = useState("");
  const [daysPerYear, setDaysPerYear] = useState("");
  const [accrualRate, setAccrualRate] = useState("");
  const [maxCarryover, setMaxCarryover] = useState("");
  const [requiresApproval, setRequiresApproval] = useState(true);
  const [description, setDescription] = useState("");

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const token = localStorage.getItem("access_token");
      
      const response = await fetch(`${baseUrl}/leave/policies`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch leave policies");
      }

      const data = await response.json();
      setPolicies(data);
    } catch (error) {
      console.error("Error fetching leave policies:", error);
      toast({
        title: "Error",
        description: "Failed to load leave policies",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchPolicies();
    }
  }, [open]);

  const resetForm = () => {
    setName("");
    setLeaveType("");
    setDaysPerYear("");
    setAccrualRate("");
    setMaxCarryover("");
    setRequiresApproval(true);
    setDescription("");
    setEditingPolicy(null);
  };

  const handleEdit = (policy: LeavePolicy) => {
    setEditingPolicy(policy);
    setName(policy.name);
    setLeaveType(policy.leave_type);
    setDaysPerYear(policy.days_per_year.toString());
    setAccrualRate(policy.accrual_rate || "");
    setMaxCarryover(policy.max_carryover?.toString() || "");
    setRequiresApproval(policy.requires_approval);
    setDescription(policy.description || "");
  };

  const handleSave = async () => {
    if (!name || !leaveType || !daysPerYear) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    const parsedDaysPerYear = parseFloat(daysPerYear);
    if (isNaN(parsedDaysPerYear) || parsedDaysPerYear <= 0) {
      toast({
        title: "Validation Error",
        description: "Days per year must be a positive number",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const token = localStorage.getItem("access_token");

      const policyData = {
        name,
        leave_type: leaveType,
        days_per_year: parsedDaysPerYear,
        accrual_rate: accrualRate || null,
        max_carryover: maxCarryover ? parseFloat(maxCarryover) : null,
        requires_approval: requiresApproval,
        description: description || null,
      };

      const url = editingPolicy
        ? `${baseUrl}/leave/policies/${editingPolicy.id}`
        : `${baseUrl}/leave/policies`;

      const method = editingPolicy ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(policyData),
      });

      if (!response.ok) {
        throw new Error("Failed to save leave policy");
      }

      toast({
        title: "Success",
        description: `Leave policy ${editingPolicy ? "updated" : "created"} successfully`,
      });

      resetForm();
      fetchPolicies();
    } catch (error) {
      console.error("Error saving leave policy:", error);
      toast({
        title: "Error",
        description: "Failed to save leave policy",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (policyId: string) => {
    if (!confirm("Are you sure you want to delete this leave policy?")) {
      return;
    }

    setLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const token = localStorage.getItem("access_token");

      const response = await fetch(`${baseUrl}/leave/policies/${policyId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete leave policy");
      }

      toast({
        title: "Success",
        description: "Leave policy deleted successfully",
      });

      fetchPolicies();
    } catch (error) {
      console.error("Error deleting leave policy:", error);
      toast({
        title: "Error",
        description: "Failed to delete leave policy",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const leaveTypes = [
    { value: "annual", label: "Annual Leave" },
    { value: "sick", label: "Sick Leave" },
    { value: "maternity", label: "Maternity Leave" },
    { value: "paternity", label: "Paternity Leave" },
    { value: "compassionate", label: "Compassionate Leave" },
    { value: "study", label: "Study Leave" },
    { value: "unpaid", label: "Unpaid Leave" },
  ];

  const accrualRates = [
    { value: "monthly", label: "Monthly" },
    { value: "yearly", label: "Yearly" },
    { value: "biweekly", label: "Bi-weekly" },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Manage Leave Policies</DialogTitle>
          <DialogDescription>
            Configure leave types and annual allowances for employees
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 py-4">
          {/* Form Section */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="text-sm font-semibold mb-4">
              {editingPolicy ? "Edit Leave Policy" : "Add New Leave Policy"}
            </h3>
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">
                    Policy Name <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Standard Annual Leave"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="leaveType">
                    Leave Type <span className="text-red-500">*</span>
                  </Label>
                  <Select value={leaveType} onValueChange={setLeaveType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select leave type" />
                    </SelectTrigger>
                    <SelectContent>
                      {leaveTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="daysPerYear">
                    Days Per Year <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="daysPerYear"
                    type="number"
                    step="0.5"
                    value={daysPerYear}
                    onChange={(e) => setDaysPerYear(e.target.value)}
                    placeholder="20"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="accrualRate">Accrual Rate</Label>
                  <Select value={accrualRate} onValueChange={setAccrualRate}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select rate" />
                    </SelectTrigger>
                    <SelectContent>
                      {accrualRates.map((rate) => (
                        <SelectItem key={rate.value} value={rate.value}>
                          {rate.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="maxCarryover">Max Carryover (Days)</Label>
                  <Input
                    id="maxCarryover"
                    type="number"
                    step="0.5"
                    value={maxCarryover}
                    onChange={(e) => setMaxCarryover(e.target.value)}
                    placeholder="5"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Additional details about this leave policy..."
                  rows={2}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="requiresApproval"
                  checked={requiresApproval}
                  onCheckedChange={setRequiresApproval}
                />
                <Label htmlFor="requiresApproval" className="cursor-pointer">
                  Requires manager approval
                </Label>
              </div>

              <div className="flex gap-2">
                <Button onClick={handleSave} disabled={loading}>
                  {loading ? "Saving..." : editingPolicy ? "Update" : "Add Policy"}
                </Button>
                {editingPolicy && (
                  <Button
                    variant="outline"
                    onClick={resetForm}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Existing Policies List */}
          <div>
            <h3 className="text-sm font-semibold mb-3">Existing Policies</h3>
            {loading && policies.length === 0 ? (
              <p className="text-sm text-gray-500">Loading policies...</p>
            ) : policies.length === 0 ? (
              <p className="text-sm text-gray-500">
                No leave policies configured yet
              </p>
            ) : (
              <div className="space-y-2">
                {policies.map((policy) => (
                  <div
                    key={policy.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{policy.name}</h4>
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                          {policy.leave_type.replace("_", " ").toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {policy.days_per_year} days/year
                        {policy.max_carryover && ` • Max carryover: ${policy.max_carryover} days`}
                        {policy.accrual_rate && ` • Accrual: ${policy.accrual_rate}`}
                        {!policy.requires_approval && " • No approval required"}
                      </p>
                      {policy.description && (
                        <p className="text-xs text-gray-500 mt-1">
                          {policy.description}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(policy)}
                        disabled={loading}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(policy.id)}
                        disabled={loading}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
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
  );
}
