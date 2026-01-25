'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { API_BASE_URL } from '@/lib/api-config';
import {
  FileText,
  Calendar,
  DollarSign,
  AlertCircle,
  Download,
  Upload,
  CheckCircle,
  Clock,
  XCircle,
  FileCheck,
  Plus,
  Eye,
  X,
} from 'lucide-react';
import {
  employeeFilesService,
  type PersonalFileSummary,
  type EmployeeDocument,
  type EmploymentContract,
  type ContractExtension,
  type Resignation,
} from '@/services/employee-files.service';
import ContractAgreementView from './ContractAgreementView';
import CreateExtensionForm from './CreateExtensionForm';

interface PersonalFileTabProps {
  employeeId: string;
  employeeName: string;
  employeeNumber: string;
  isOwner: boolean; // Is viewing their own file
  isHR: boolean;
  isCEO: boolean;
  isSupervisor: boolean;
}

export default function PersonalFileTab({
  employeeId,
  employeeName,
  employeeNumber,
  isOwner,
  isHR,
  isCEO,
  isSupervisor,
}: PersonalFileTabProps) {
  const [summary, setSummary] = useState<PersonalFileSummary | null>(null);
  const [documents, setDocuments] = useState<EmployeeDocument[]>([]);
  const [contracts, setContracts] = useState<EmploymentContract[]>([]);
  const [extensions, setExtensions] = useState<ContractExtension[]>([]);
  const [resignations, setResignations] = useState<Resignation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showResignationDialog, setShowResignationDialog] = useState(false);
  const [submittingResignation, setSubmittingResignation] = useState(false);
  const [viewingContract, setViewingContract] = useState<EmploymentContract | null>(null);
  const [showCreateExtension, setShowCreateExtension] = useState(false);
  const [selectedContractForExtension, setSelectedContractForExtension] = useState<EmploymentContract | null>(null);
  const [showCreateContract, setShowCreateContract] = useState(false);
  const [employeeData, setEmployeeData] = useState<any>(null);

  const canEdit = isHR || isCEO;
  const canView = isOwner || isHR || isCEO || isSupervisor;

  useEffect(() => {
    if (canView) {
      loadData();
    }
  }, [employeeId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔍 Loading personal file data for employee:', employeeId);
      console.log('🔑 Checking auth token...');
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      console.log('Token exists:', !!token, token ? `(${token.substring(0, 20)}...)` : '');
      
      const [summaryData, docsData, contractsData, extensionsData, resignationsData, empData] =
        await Promise.all([
          employeeFilesService.getPersonalFileSummary(employeeId),
          employeeFilesService.getEmployeeDocuments(employeeId),
          employeeFilesService.getEmployeeContracts(employeeId, true),
          employeeFilesService.getPendingExtensions(employeeId),
          employeeFilesService.getEmployeeResignations(employeeId),
          fetch(`${API_BASE_URL}/employees/${employeeId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(r => r.json()).catch(() => null),
        ]);

      console.log('✅ Personal file data loaded:', {
        summary: summaryData,
        docs: docsData.length,
        contracts: contractsData.length,
        extensions: extensionsData.length,
        resignations: resignationsData.length,
        employee: empData
      });

      setSummary(summaryData);
      setDocuments(docsData);
      setContracts(contractsData);
      setExtensions(extensionsData);
      setResignations(resignationsData);
      setEmployeeData(empData);
    } catch (error) {
      console.error('❌ Failed to load personal file data:', error);
      console.error('❌ Error type:', typeof error, error);
      console.error('❌ Error stack:', error instanceof Error ? error.stack : 'No stack');
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Check if it's an auth error
      if (errorMessage.includes('401') || errorMessage.includes('Unauthorized') || 
          errorMessage.includes('Invalid or expired token')) {
        setError(`Authentication failed: ${errorMessage}. Please log in again.`);
      } else if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Load failed') || 
                 errorMessage.includes('NetworkError') || errorMessage.includes('TypeError')) {
        setError(`Network Error: ${errorMessage}. Backend may not be running or CORS issue. Check console for details.`);
      } else {
        setError(`Error: ${errorMessage}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptExtension = async (extensionId: string) => {
    try {
      await employeeFilesService.acceptExtension(extensionId);
      await loadData();
      alert('Contract extension accepted successfully!');
    } catch (error) {
      console.error('Failed to accept extension:', error);
      alert('Failed to accept extension');
    }
  };

  const handleUploadDocument = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setUploading(true);

    try {
      const formData = new FormData(event.currentTarget);
      formData.append('employee_id', employeeId);
      
      await employeeFilesService.uploadDocument(formData);
      await loadData();
      setShowUploadDialog(false);
      alert('Document uploaded successfully!');
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmitResignation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmittingResignation(true);

    try {
      const formData = new FormData(event.currentTarget);
      
      const resignationData = {
        employee_id: employeeId,
        resignation_date: formData.get('resignation_date') as string,
        intended_last_working_day: formData.get('intended_last_working_day') as string,
        reason: formData.get('reason') as string,
        notice_period_days: parseInt(formData.get('notice_period_days') as string || '30'),
      };

      await employeeFilesService.submitResignation(resignationData);
      await loadData();
      setShowResignationDialog(false);
      alert('Resignation submitted successfully!');
    } catch (error) {
      console.error('Failed to submit resignation:', error);
      alert('Failed to submit resignation');
    } finally {
      setSubmittingResignation(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { color: string; label: string }> = {
      DRAFT: { color: 'bg-gray-500', label: 'Draft' },
      ACTIVE: { color: 'bg-green-500', label: 'Active' },
      EXTENDED: { color: 'bg-blue-500', label: 'Extended' },
      EXPIRED: { color: 'bg-red-500', label: 'Expired' },
      TERMINATED: { color: 'bg-red-700', label: 'Terminated' },
      PENDING: { color: 'bg-yellow-500', label: 'Pending' },
      ACCEPTED: { color: 'bg-green-500', label: 'Accepted' },
      REJECTED: { color: 'bg-red-500', label: 'Rejected' },
      SUBMITTED: { color: 'bg-blue-500', label: 'Submitted' },
      ACCEPTED_BY_SUPERVISOR: { color: 'bg-blue-600', label: 'Supervisor Approved' },
      ACCEPTED_BY_HR: { color: 'bg-blue-700', label: 'HR Approved' },
      ACCEPTED_BY_CEO: { color: 'bg-green-600', label: 'CEO Approved' },
      COMPLETED: { color: 'bg-green-700', label: 'Completed' },
      WITHDRAWN: { color: 'bg-gray-600', label: 'Withdrawn' },
    };

    const config = statusConfig[status] || { color: 'bg-gray-500', label: status };
    return (
      <Badge className={`${config.color} text-white`}>
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  if (!canView) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4" />
            <p>You do not have permission to view this personal file.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <Clock className="w-12 h-12 mx-auto mb-4 animate-spin" />
            <p>Loading personal file...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-red-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4" />
            <p className="font-semibold mb-2">Error Loading Personal File</p>
            <p className="text-sm">{error}</p>
            <Button onClick={loadData} className="mt-4" variant="outline">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Documents</p>
                  <p className="text-2xl font-bold">{summary.total_documents}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Active Contracts</p>
                  <p className="text-2xl font-bold">{summary.active_contracts}</p>
                </div>
                <FileCheck className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Pending Extensions</p>
                  <p className="text-2xl font-bold">{summary.pending_extensions}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Contract Ends In</p>
                  <p className="text-2xl font-bold">
                    {summary.days_until_contract_end !== null && summary.days_until_contract_end !== undefined
                      ? `${summary.days_until_contract_end} days`
                      : 'N/A'}
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* No Data Message */}
      {!summary && !loading && (
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4" />
              <p className="font-semibold mb-2">No Personal File Data</p>
              <p className="text-sm">No documents, contracts, or extensions found for this employee.</p>
              {canEdit && (
                <p className="text-sm mt-2">Start by uploading a document or creating a contract.</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pending Actions Alert */}
      {summary && summary.pending_actions.length > 0 && (
        <Card className="border-yellow-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-600">
              <AlertCircle className="w-5 h-5" />
              Pending Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-1">
              {summary.pending_actions.map((action, index) => (
                <li key={index} className="text-sm">
                  {action}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Tabs for different sections */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="contracts">Contracts</TabsTrigger>
          <TabsTrigger value="extensions">Extensions</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="resignations">Resignations</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          {summary?.current_contract && (
            <Card>
              <CardHeader>
                <CardTitle>Current Contract</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Contract Number</p>
                    <p className="font-semibold">{summary.current_contract.contract_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Position</p>
                    <p className="font-semibold">{summary.current_contract.position_title}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Location</p>
                    <p className="font-semibold">{summary.current_contract.location}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Salary</p>
                    <p className="font-semibold">
                      {formatCurrency(
                        summary.current_contract.monthly_salary,
                        summary.current_contract.currency
                      )}{' '}
                      / month
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Start Date</p>
                    <p className="font-semibold">{formatDate(summary.current_contract.start_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">End Date</p>
                    <p className="font-semibold">{formatDate(summary.current_contract.end_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <div className="mt-1">{getStatusBadge(summary.current_contract.status)}</div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Contract Type</p>
                    <p className="font-semibold">{summary.current_contract.contract_type}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Documents */}
          {summary && summary.recent_documents.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {summary.recent_documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="font-medium">{doc.title}</p>
                          <p className="text-sm text-gray-500">
                            {doc.category} • {formatDate(doc.uploaded_at)}
                          </p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Contracts Tab */}
        <TabsContent value="contracts" className="space-y-4">
          {/* Create Contract Button */}
          {canEdit && !viewingContract && !showCreateContract && (
            <Card>
              <CardContent className="p-4">
                <Button
                  onClick={() => setShowCreateContract(true)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create New Contract
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Create Contract Form */}
          {showCreateContract && canEdit && (
            <Card className="border-blue-500">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Create Employment Contract for {employeeName}</CardTitle>
                  <Button variant="ghost" size="sm" onClick={() => setShowCreateContract(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.currentTarget);
                    
                    try {
                      const contractData = {
                        employee_id: employeeId,
                        contract_number: formData.get('contract_number') as string,
                        position_title: formData.get('position_title') as string,
                        location: formData.get('location') as string,
                        contract_type: formData.get('contract_type') as string,
                        start_date: formData.get('start_date') as string,
                        end_date: formData.get('end_date') as string,
                        monthly_salary: parseFloat(formData.get('monthly_salary') as string),
                        currency: formData.get('currency') as string || 'USD',
                        notice_period_days: parseInt(formData.get('notice_period_days') as string) || 30,
                        signed_date: formData.get('signed_date') as string || undefined,
                      };

                      await employeeFilesService.createContract(contractData);
                      alert('Contract created successfully!');
                      setShowCreateContract(false);
                      loadData();
                    } catch (error) {
                      console.error('Failed to create contract:', error);
                      alert('Failed to create contract. Please try again.');
                    }
                  }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="contract_number">Contract Number *</Label>
                      <Input id="contract_number" name="contract_number" required placeholder="e.g., CNT-2025-001" />
                    </div>
                    <div>
                      <Label htmlFor="contract_type">Contract Type *</Label>
                      <Select name="contract_type" required defaultValue="Annual">
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Annual">Annual</SelectItem>
                          <SelectItem value="Fixed-Term">Fixed-Term</SelectItem>
                          <SelectItem value="Permanent">Permanent</SelectItem>
                          <SelectItem value="Probation">Probation</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="position_title">Position Title *</Label>
                      <Input 
                        id="position_title" 
                        name="position_title" 
                        required 
                        defaultValue={employeeData?.position?.title || ''}
                        placeholder="e.g., Program Manager" 
                      />
                    </div>
                    <div>
                      <Label htmlFor="location">Work Location *</Label>
                      <Input 
                        id="location" 
                        name="location" 
                        required 
                        defaultValue={employeeData?.work_location || ''}
                        placeholder="e.g., Istanbul, Turkey" 
                      />
                    </div>
                    <div>
                      <Label htmlFor="start_date">Start Date *</Label>
                      <Input 
                        id="start_date" 
                        name="start_date" 
                        type="date" 
                        required 
                        defaultValue={employeeData?.hire_date || ''}
                      />
                    </div>
                    <div>
                      <Label htmlFor="end_date">End Date *</Label>
                      <Input id="end_date" name="end_date" type="date" required />
                    </div>
                    <div>
                      <Label htmlFor="monthly_salary">Monthly Salary *</Label>
                      <Input id="monthly_salary" name="monthly_salary" type="number" step="0.01" required placeholder="2500.00" />
                    </div>
                    <div>
                      <Label htmlFor="currency">Currency</Label>
                      <Select name="currency" defaultValue="USD">
                        <SelectTrigger>
                          <SelectValue placeholder="USD" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="USD">USD</SelectItem>
                          <SelectItem value="EUR">EUR</SelectItem>
                          <SelectItem value="GBP">GBP</SelectItem>
                          <SelectItem value="TRY">TRY</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="notice_period_days">Notice Period (days)</Label>
                      <Input id="notice_period_days" name="notice_period_days" type="number" defaultValue="30" />
                    </div>
                    <div>
                      <Label htmlFor="signed_date">Signed Date</Label>
                      <Input id="signed_date" name="signed_date" type="date" />
                    </div>
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                      <Plus className="w-4 h-4 mr-2" />
                      Create Contract
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowCreateContract(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {viewingContract ? (
            <div className="space-y-4">
              <Button onClick={() => setViewingContract(null)} variant="outline">
                ← Back to Contracts List
              </Button>
              <ContractAgreementView
                contract={viewingContract}
                employeeName={employeeName}
                employeeNumber={employeeNumber}
              />
            </div>
          ) : (
            <>
              {contracts.map((contract) => (
                <Card key={contract.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Contract {contract.contract_number}</CardTitle>
                      {getStatusBadge(contract.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Position</p>
                        <p className="font-semibold">{contract.position_title}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Period</p>
                        <p className="font-semibold">
                          {formatDate(contract.start_date)} - {formatDate(contract.end_date)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Salary</p>
                        <p className="font-semibold">
                          {formatCurrency(contract.monthly_salary, contract.currency)} / month
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={() => setViewingContract(contract)} variant="outline">
                        <Eye className="w-4 h-4 mr-2" />
                        View Full Agreement
                      </Button>
                      {canEdit && contract.status === 'ACTIVE' && (
                        <Button
                          onClick={() => {
                            setSelectedContractForExtension(contract);
                            setShowCreateExtension(true);
                          }}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Create Extension
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </TabsContent>

        {/* Extensions Tab */}
        <TabsContent value="extensions" className="space-y-4">
          {/* Create Extension Button - Always show at top if user can edit and has active contract */}
          {canEdit && summary?.current_contract && summary.current_contract.status === 'ACTIVE' && !showCreateExtension && (
            <Card>
              <CardContent className="p-4">
                <Button
                  onClick={() => {
                    setSelectedContractForExtension(summary.current_contract!);
                    setShowCreateExtension(true);
                  }}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create New Extension
                </Button>
              </CardContent>
            </Card>
          )}

          {showCreateExtension && selectedContractForExtension && canEdit && (
            <CreateExtensionForm
              contract={selectedContractForExtension}
              employeeId={employeeId}
              employeeName={employeeName}
              onSuccess={() => {
                setShowCreateExtension(false);
                setSelectedContractForExtension(null);
                loadData();
              }}
              onCancel={() => {
                setShowCreateExtension(false);
                setSelectedContractForExtension(null);
              }}
            />
          )}

          {!showCreateExtension && extensions.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Extension History</h3>
              {extensions.map((extension) => (
            <Card key={extension.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Extension #{extension.extension_number}</CardTitle>
                  {getStatusBadge(extension.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">New Period</p>
                      <p className="font-semibold">
                        {formatDate(extension.new_start_date)} - {formatDate(extension.new_end_date)}
                      </p>
                    </div>
                    {extension.new_monthly_salary && (
                      <div>
                        <p className="text-sm text-gray-500">New Salary</p>
                        <p className="font-semibold">
                          {formatCurrency(extension.new_monthly_salary)} / month
                        </p>
                      </div>
                    )}
                    {extension.new_position_title && (
                      <div>
                        <p className="text-sm text-gray-500">New Position</p>
                        <p className="font-semibold">{extension.new_position_title}</p>
                      </div>
                    )}
                    {extension.new_location && (
                      <div>
                        <p className="text-sm text-gray-500">New Location</p>
                        <p className="font-semibold">{extension.new_location}</p>
                      </div>
                    )}
                  </div>

                  {extension.terms_changes && (
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Terms Changes</p>
                      <p className="text-sm bg-gray-50 p-3 rounded">{extension.terms_changes}</p>
                    </div>
                  )}

                  {extension.status === 'PENDING' && isOwner && (
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleAcceptExtension(extension.id)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Accept Extension
                      </Button>
                      {extension.expires_at && (
                        <p className="text-sm text-yellow-600 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          Expires: {formatDate(extension.expires_at)}
                        </p>
                      )}
                    </div>
                  )}

                  {extension.employee_accepted_at && (
                    <div className="text-sm text-green-600">
                      <CheckCircle className="w-4 h-4 inline mr-1" />
                      Accepted on {formatDate(extension.employee_accepted_at)}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
            </div>
          )}

          {!showCreateExtension && extensions.length === 0 && (
            <Card>
              <CardContent className="p-6 text-center text-gray-500">
                <p className="mb-4">No contract extensions found</p>
                {canEdit && summary?.current_contract && summary.current_contract.status === 'ACTIVE' ? (
                  <Button
                    onClick={() => {
                      setSelectedContractForExtension(summary.current_contract!);
                      setShowCreateExtension(true);
                    }}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create First Extension
                  </Button>
                ) : !summary?.current_contract ? (
                  <p className="text-sm text-gray-400">
                    No active contract found. Please create a contract in the Contracts tab first.
                  </p>
                ) : null}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          {canEdit && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Upload Document</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button onClick={() => setShowUploadDialog(!showUploadDialog)}>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload New Document
                  </Button>
                </CardContent>
              </Card>

              {showUploadDialog && (
                <Card className="border-blue-500">
                  <CardHeader>
                    <CardTitle>Upload New Document</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleUploadDocument} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Document Category *</label>
                        <select name="category" required className="w-full p-2 border rounded">
                          <option value="">Select category...</option>
                          <option value="contract">Contract</option>
                          <option value="contract_extension">Contract Extension</option>
                          <option value="educational">Educational</option>
                          <option value="reference_check">Reference Check</option>
                          <option value="interview_record">Interview Record</option>
                          <option value="background_check">Background Check</option>
                          <option value="id_document">ID Document</option>
                          <option value="bank_details">Bank Details</option>
                          <option value="emergency_contact">Emergency Contact</option>
                          <option value="resignation">Resignation</option>
                          <option value="termination">Termination</option>
                          <option value="performance_review">Performance Review</option>
                          <option value="disciplinary">Disciplinary</option>
                          <option value="training_certificate">Training Certificate</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Document Title *</label>
                        <input type="text" name="title" required className="w-full p-2 border rounded" />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Description</label>
                        <textarea name="description" rows={3} className="w-full p-2 border rounded"></textarea>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">File *</label>
                        <input type="file" name="file" required className="w-full p-2 border rounded" />
                      </div>

                      <div className="flex items-center gap-2">
                        <input type="checkbox" name="is_confidential" id="is_confidential" defaultChecked />
                        <label htmlFor="is_confidential" className="text-sm">Mark as confidential</label>
                      </div>

                      <div className="flex gap-2">
                        <Button type="submit" disabled={uploading}>
                          {uploading ? 'Uploading...' : 'Upload'}
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setShowUploadDialog(false)}>
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          <Card>
            <CardHeader>
              <CardTitle>All Documents ({documents.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <p className="text-center text-gray-500 py-4">No documents found</p>
              ) : (
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="font-medium">{doc.title}</p>
                          <p className="text-sm text-gray-500">
                            {doc.category} • {formatDate(doc.uploaded_at)} • {(doc.file_size / 1024).toFixed(2)} KB
                          </p>
                          {doc.description && (
                            <p className="text-sm text-gray-600 mt-1">{doc.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Download className="w-4 h-4" />
                        </Button>
                        {canEdit && (
                          <Button variant="outline" size="sm" className="text-red-600">
                            <XCircle className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resignations Tab */}
        <TabsContent value="resignations" className="space-y-4">
          {/* Submit Resignation Button - Only show for owner if no active resignation */}
          {isOwner && !resignations.some(r => ['SUBMITTED', 'ACCEPTED_BY_SUPERVISOR', 'ACCEPTED_BY_HR', 'ACCEPTED_BY_CEO'].includes(r.status)) && (
            <>
              <Button onClick={() => setShowResignationDialog(true)} className="w-full sm:w-auto">
                <FileText className="w-4 h-4 mr-2" />
                Submit Resignation
              </Button>

              {showResignationDialog && (
                <Card className="border-red-500">
                  <CardHeader>
                    <CardTitle>Submit Resignation</CardTitle>
                    <p className="text-sm text-gray-500 mt-2">
                      Please provide the required information for your resignation. This will be reviewed by your supervisor, HR, and CEO.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleSubmitResignation} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Resignation Date *</label>
                        <input 
                          type="date" 
                          name="resignation_date" 
                          required 
                          defaultValue={new Date().toISOString().split('T')[0]}
                          className="w-full p-2 border rounded" 
                        />
                        <p className="text-xs text-gray-500 mt-1">The date you are submitting this resignation</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Intended Last Working Day *</label>
                        <input 
                          type="date" 
                          name="intended_last_working_day" 
                          required 
                          min={new Date().toISOString().split('T')[0]}
                          className="w-full p-2 border rounded" 
                        />
                        <p className="text-xs text-gray-500 mt-1">Your proposed last day of work</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Notice Period (Days) *</label>
                        <input 
                          type="number" 
                          name="notice_period_days" 
                          required 
                          defaultValue={30}
                          min={0}
                          className="w-full p-2 border rounded" 
                        />
                        <p className="text-xs text-gray-500 mt-1">Number of days notice as per your contract</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Reason for Resignation *</label>
                        <textarea 
                          name="reason" 
                          required
                          rows={4}
                          placeholder="Please provide your reason for leaving..."
                          className="w-full p-2 border rounded"
                        ></textarea>
                        <p className="text-xs text-gray-500 mt-1">This information will be kept confidential</p>
                      </div>

                      <div className="flex gap-2 pt-2">
                        <Button type="submit" disabled={submittingResignation} variant="destructive">
                          {submittingResignation ? 'Submitting...' : 'Submit Resignation'}
                        </Button>
                        <Button 
                          type="button" 
                          variant="outline" 
                          onClick={() => setShowResignationDialog(false)}
                          disabled={submittingResignation}
                        >
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {/* List of existing resignations */}
          {resignations.map((resignation) => (
            <Card key={resignation.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Resignation {resignation.resignation_number}</CardTitle>
                  {getStatusBadge(resignation.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Resignation Date</p>
                      <p className="font-semibold">{formatDate(resignation.resignation_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Intended Last Day</p>
                      <p className="font-semibold">
                        {formatDate(resignation.intended_last_working_day)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Notice Period</p>
                      <p className="font-semibold">{resignation.notice_period_days} days</p>
                    </div>
                    {resignation.approved_last_working_day && (
                      <div>
                        <p className="text-sm text-gray-500">Approved Last Day</p>
                        <p className="font-semibold">
                          {formatDate(resignation.approved_last_working_day)}
                        </p>
                      </div>
                    )}
                  </div>

                  <div>
                    <p className="text-sm text-gray-500 mb-1">Reason</p>
                    <p className="text-sm bg-gray-50 p-3 rounded">{resignation.reason}</p>
                  </div>

                  {/* Approval Timeline */}
                  <div className="border-l-2 border-gray-300 pl-4 space-y-3">
                    {resignation.supervisor_accepted_at && (
                      <div>
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="font-semibold">Supervisor Approved</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDate(resignation.supervisor_accepted_at)}
                        </p>
                        {resignation.supervisor_comments && (
                          <p className="text-sm mt-1">{resignation.supervisor_comments}</p>
                        )}
                      </div>
                    )}

                    {resignation.hr_accepted_at && (
                      <div>
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="font-semibold">HR Approved</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDate(resignation.hr_accepted_at)}
                        </p>
                        {resignation.hr_comments && (
                          <p className="text-sm mt-1">{resignation.hr_comments}</p>
                        )}
                      </div>
                    )}

                    {resignation.ceo_accepted_at && (
                      <div>
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="font-semibold">CEO Approved</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDate(resignation.ceo_accepted_at)}
                        </p>
                        {resignation.ceo_comments && (
                          <p className="text-sm mt-1">{resignation.ceo_comments}</p>
                        )}
                      </div>
                    )}

                    {resignation.exit_interview_completed && (
                      <div>
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="font-semibold">Exit Interview Completed</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDate(resignation.exit_interview_date)}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Download PDF Button */}
                  <div className="mt-4">
                    <Button
                      onClick={async () => {
                        try {
                          const token = localStorage.getItem('access_token');
                          const response = await fetch(
                            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/employee-files/resignations/${resignation.id}/download-pdf`,
                            {
                              headers: {
                                'Authorization': `Bearer ${token}`,
                              },
                            }
                          );

                          if (!response.ok) {
                            throw new Error('Failed to download PDF');
                          }

                          const blob = await response.blob();
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `resignation_${resignation.resignation_number}.pdf`;
                          document.body.appendChild(a);
                          a.click();
                          window.URL.revokeObjectURL(url);
                          document.body.removeChild(a);
                        } catch (error) {
                          console.error('Error downloading PDF:', error);
                          alert('Failed to download PDF');
                        }
                      }}
                      variant="outline"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download Resignation Letter (PDF)
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {resignations.length === 0 && (
            <Card>
              <CardContent className="p-6 text-center text-gray-500">
                No resignations found
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
