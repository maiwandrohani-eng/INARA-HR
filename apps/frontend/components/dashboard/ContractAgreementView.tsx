'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText } from 'lucide-react';
import type { EmploymentContract } from '@/services/employee-files.service';

interface ContractAgreementViewProps {
  contract: EmploymentContract;
  employeeName: string;
  employeeNumber: string;
}

export default function ContractAgreementView({
  contract,
  employeeName,
  employeeNumber,
}: ContractAgreementViewProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const handleDownloadPDF = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/employee-files/contracts/${contract.id}/download-pdf`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to download PDF');
      }

      // Create a blob from the response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contract_${contract.contract_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF');
    }
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardContent className="p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Employment Agreement</h1>
        </div>

        {/* Contract Info Table */}
        <div className="mb-8 border border-gray-300">
          <table className="w-full">
            <tbody>
              <tr className="border-b border-gray-300">
                <td className="font-semibold p-3 bg-gray-50 w-1/3">Name:</td>
                <td className="p-3">{employeeName}</td>
              </tr>
              <tr className="border-b border-gray-300">
                <td className="font-semibold p-3 bg-gray-50">Position:</td>
                <td className="p-3">{contract.position_title}</td>
              </tr>
              <tr className="border-b border-gray-300">
                <td className="font-semibold p-3 bg-gray-50">Location:</td>
                <td className="p-3">{contract.location}</td>
              </tr>
              <tr className="border-b border-gray-300">
                <td className="font-semibold p-3 bg-gray-50">Type of Contract:</td>
                <td className="p-3">{contract.contract_type}</td>
              </tr>
              <tr>
                <td className="font-semibold p-3 bg-gray-50">Employee #:</td>
                <td className="p-3">{employeeNumber}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Agreement Content */}
        <div className="space-y-6 text-sm leading-relaxed">
          <p>
            This Employment Agreement ("Agreement") was made and entered into on{' '}
            <strong>{formatDate(contract.start_date)}</strong> between{' '}
            <strong>INARA</strong>, hereinafter referred to as the "Employer," and{' '}
            <strong>{employeeName}</strong>, hereinafter referred to as the "Employee."
          </p>

          {/* Section 1 */}
          <div>
            <h2 className="text-lg font-bold mb-2">1. POSITION AND DUTIES:</h2>
            <p>
              The Employee shall be employed as <strong>{contract.position_title}</strong>{' '}
              and perform the duties and responsibilities associated with this position
              (attached JD). The Employer may modify or expand the Employee's duties as
              necessary.
            </p>
          </div>

          {/* Section 2 */}
          <div>
            <h2 className="text-lg font-bold mb-2">2. EMPLOYMENT TERM:</h2>
            <p>
              The employment shall commence on <strong>{formatDate(contract.start_date)}</strong>{' '}
              and constitute an annual contract, subject to review twice a year during
              performance appraisals scheduled in June and December. The continuation of
              this contract beyond each year is contingent upon the outcome of these
              semi-annual performance appraisals.
            </p>
            <p className="mt-2">
              Upon successful performance as determined during the June and December reviews,
              this annual contract may be subject to renewal for subsequent periods. Either
              party may terminate the contract in accordance with the terms specified herein.
            </p>
          </div>

          {/* Section 3 */}
          <div>
            <h2 className="text-lg font-bold mb-2">3. COMPENSATION:</h2>
            <div className="ml-6 space-y-3">
              <div>
                <p className="font-semibold">a. Base Salary:</p>
                <p>
                  The Employee shall receive a net salary of{' '}
                  <strong>{formatCurrency(contract.monthly_salary, contract.currency)}</strong>,
                  payable in accordance with the Employer's standard payroll schedule. This
                  base salary is not subject to regular deductions required by law; INARA
                  will pay all the related taxes.
                </p>
              </div>

              <div>
                <p className="font-semibold">b. Bonuses and Incentives:</p>
                <p>
                  The Employee may be eligible for bonuses or incentives based on
                  performance, as determined by the Employer. The criteria and terms for
                  such bonuses or incentives shall be outlined in the Employer's policies
                  and may be subject to change at the discretion of the Employer.
                </p>
              </div>

              <div>
                <p className="font-semibold">c. Expense Reimbursement:</p>
                <p>
                  The Employee shall be reimbursed for reasonable and authorized expenses
                  incurred during the course of performing their duties on behalf of the
                  Employer. Such expenses must be pre-approved and in compliance with the
                  Employer's policies.
                </p>
              </div>

              <div>
                <p className="font-semibold">d. Salary Reviews:</p>
                <p>
                  The Employer may, at its discretion, conduct periodic reviews of the
                  Employee's performance and may consider adjustments to the Employee's
                  salary based on these reviews. Any salary adjustments shall be
                  communicated to the Employee in writing.
                </p>
              </div>

              <div>
                <p className="font-semibold">e. Withholding:</p>
                <p>
                  The Employer shall withhold applicable taxes and deductions as required
                  by law from the Employee's compensation.
                </p>
              </div>

              <div>
                <p className="font-semibold">f. Payroll Records:</p>
                <p>
                  The Employer shall maintain accurate records of the Employee's
                  compensation, deductions, and benefits in accordance with legal
                  requirements and shall provide the Employee with access to such records
                  upon reasonable request.
                </p>
              </div>

              <div>
                <p className="font-semibold">g. Changes to Compensation:</p>
                <p>
                  The Employer reserves the right to modify the Employee's compensation,
                  benefits, or any other aspects of remuneration, provided such changes are
                  communicated to the Employee in writing and in accordance with applicable
                  laws.
                </p>
              </div>
            </div>
          </div>

          {/* Section 4 */}
          <div>
            <h2 className="text-lg font-bold mb-2">
              4. COMPLIANCE WITH EMPLOYER POLICIES AND HUMANITARIAN STANDARDS:
            </h2>
            <div className="ml-6 space-y-3">
              <div>
                <p className="font-semibold">a.</p>
                <p>
                  The Employee acknowledges and agrees to adhere to all policies, rules,
                  and procedures established by the Employer. These policies may include,
                  but are not limited to, codes of conduct, confidentiality agreements,
                  health and safety guidelines, and any other policies or guidelines
                  communicated by the Employer during the course of employment.
                </p>
              </div>

              <div>
                <p className="font-semibold">b.</p>
                <p>
                  The Employee further acknowledges the humanitarian nature of the
                  organization and agrees to conduct themselves in a manner that upholds the
                  highest ethical and humanitarian standards. This includes promoting
                  diversity, equity, and inclusion, as well as respecting cultural
                  sensitivities and human rights principles in all interactions and
                  activities related to their role.
                </p>
              </div>

              <div>
                <p className="font-semibold">c.</p>
                <p>
                  Any violations of Employer policies or failure to comply with humanitarian
                  standards may result in disciplinary action, up to and including
                  termination of employment, as deemed appropriate by the Employer.
                </p>
              </div>

              <div>
                <p className="font-semibold">d.</p>
                <p>
                  The Employer reserves the right to update, amend, or introduce new
                  policies and standards as necessary. The Employee shall be notified of any
                  such changes in a timely manner, and continued employment shall be
                  considered as acceptance of these updated policies and standards.
                </p>
              </div>

              <div>
                <p className="font-semibold">e.</p>
                <p>
                  The Employee understands that adherence to Employer policies and
                  humanitarian standards is essential to maintaining the reputation,
                  integrity, and mission of <strong className="text-blue-600">INARA</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* Section 5 */}
          <div>
            <h2 className="text-lg font-bold mb-2">5. LEARNING AND DEVELOPMENT:</h2>
            <div className="ml-6 space-y-3">
              <div>
                <p className="font-semibold">a.</p>
                <p>
                  The Employer recognizes the importance of continuous learning and
                  professional development for enhancing work performance and fostering
                  organizational growth.
                </p>
              </div>

              <div>
                <p className="font-semibold">b.</p>
                <p>
                  The Employee shall be allocated up to 10% of their working hours per year
                  for engaging in learning and development activities through the INARA
                  learning platform or other approved educational resources the Employer
                  facilitates.
                </p>
              </div>

              <div>
                <p className="font-semibold">c.</p>
                <p>
                  The Employee is encouraged to utilize the INARA learning platform to
                  access courses, training materials, and resources aimed at enhancing
                  skills relevant to the Employee's role within the organization.
                </p>
              </div>

              <div>
                <p className="font-semibold">d.</p>
                <p>
                  The Employer shall provide access to the INARA learning platform and other
                  approved resources necessary for the Employee's development. The Employee
                  shall responsibly manage this dedicated time for learning and ensure that
                  it aligns with the Employee's professional growth and the needs of the
                  Employer.
                </p>
              </div>

              <div>
                <p className="font-semibold">e.</p>
                <p>
                  The Employee agrees to report the progress of their learning and
                  development activities periodically, as required by the Employer, to track
                  and evaluate the impact of such efforts on work performance.
                </p>
              </div>

              <div>
                <p className="font-semibold">f.</p>
                <p>
                  While the Employer supports the Employee's learning and development, it is
                  understood that this time allocation should not compromise the timely and
                  efficient completion of the Employee's primary job responsibilities.
                </p>
              </div>

              <div>
                <p className="font-semibold">g.</p>
                <p>
                  The Employer reserves the right to modify the allocated time for learning
                  and development in consultation with the Employee, considering the
                  operational needs of the organization.
                </p>
              </div>
            </div>
          </div>

          {/* Section 6 */}
          <div>
            <h2 className="text-lg font-bold mb-2">6. CONFIDENTIALITY:</h2>
            <p>
              During the course of employment, the Employee may have access to confidential
              information belonging to the Employer. The Employee agrees not to disclose,
              directly or indirectly, any confidential information to any third party during
              or after the employment period, except as required by law or with the
              Employer's written consent.
            </p>
          </div>

          {/* Section 7 */}
          <div>
            <h2 className="text-lg font-bold mb-2">7. TERMINATION:</h2>
            <p>
              Either party may terminate this Agreement at any time, with or without cause,
              by providing <strong>30 days</strong> written notice to the other party (or as
              required by the local law where applicable). Upon termination, the Employee
              shall return any property or confidential information belonging to the
              Employer.
            </p>
          </div>

          {/* Section 8 */}
          <div>
            <h2 className="text-lg font-bold mb-2">8. INTELLECTUAL PROPERTY:</h2>
            <p>
              Any inventions, creations, or works developed by the Employee during the
              course of employment that relate to the Employer's business shall be the
              exclusive property of the Employer.
            </p>
          </div>

          {/* Section 9 */}
          <div>
            <h2 className="text-lg font-bold mb-2">9. ENTIRE AGREEMENT:</h2>
            <p>
              This Agreement constitutes the entire understanding between the parties
              concerning the employment of the Employee and supersedes any prior agreements
              or understandings, whether written or oral.
            </p>
            <p className="mt-2">
              IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the
              date first above written.
            </p>
          </div>

          {/* Signatures */}
          <div className="border-t-2 border-gray-800 pt-6 mt-8 space-y-8">
            <div>
              <p className="font-bold mb-2">On Behalf of INARA</p>
              <p className="font-semibold">Maiwand Rohani</p>
              <p>CEO</p>
              <p>01 January 2025</p>
              <div className="border-b border-gray-400 w-64 mt-4"></div>
            </div>

            <div>
              <p className="font-bold mb-2">{employeeName}</p>
              <p>{formatDate(contract.signed_date || contract.start_date)}</p>
              <div className="border-b border-gray-400 w-64 mt-4"></div>
            </div>
          </div>
        </div>

        {/* Download Button */}
        <div className="mt-8 text-center">
          <Button onClick={handleDownloadPDF} className="bg-blue-600 hover:bg-blue-700">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>INARA EMPLOYMENT AGREEMENT - Page 1 of 5</p>
        </div>
      </CardContent>
    </Card>
  );
}
