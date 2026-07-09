import React, { useState } from 'react';
import axios from 'axios';
import FraudScoreGauge from './FraudScoreGauge';
import RedFlagsList from './RedFlagsList';
import CostComparisonTable from './CostComparisonTable';
import ReceiptViewer from './ReceiptViewer';

function ResultsPage({ claimData, onNewUpload }) {
  const currency = claimData.currency || 'KES';
  const rec = claimData.recommendation;

  // Officer decision state — one decision per claim
  const [actionLoading, setActionLoading] = useState(null); // status currently in flight
  const [actionTaken, setActionTaken] = useState(null);     // status that was submitted
  const [smsSent, setSmsSent] = useState(false);
  const [actionError, setActionError] = useState(null);

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(claimData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mediclaim_${claimData.claim_id || 'report'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAction = async (status) => {
    if (actionTaken || actionLoading || !claimData.claim_id) return;
    setActionLoading(status);
    setActionError(null);
    try {
      const res = await axios.patch(`/api/claims/${claimData.claim_id}/status`, { status });
      setActionTaken(status);
      setSmsSent(!!res.data.sms_sent);
    } catch (err) {
      setActionError(err.response?.data?.detail || 'Failed to update claim status. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const actionButtons = [
    { label: '✅ Approve Claim',   action: 'APPROVE',      status: 'APPROVED',      color: 'bg-green-500 hover:bg-green-600' },
    { label: '📋 Request Review',  action: 'REVIEW',       status: 'REVIEW',        color: 'bg-yellow-500 hover:bg-yellow-600' },
    { label: '🔍 Investigate',     action: 'INVESTIGATE',  status: 'INVESTIGATING', color: 'bg-orange-500 hover:bg-orange-600' },
    { label: '❌ Reject Claim',    action: 'REJECT',       status: 'REJECTED',      color: 'bg-red-500 hover:bg-red-600' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex justify-between items-center flex-wrap gap-3">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-1">Analysis Results</h1>
              <p className="text-sm text-gray-500">
                Claim ID: <span className="font-mono">{claimData.claim_id || 'N/A'}</span>
                &nbsp;•&nbsp;Processed: {new Date().toLocaleString()}
                {claimData.file_type && (
                  <>&nbsp;•&nbsp;File: <span className="uppercase font-semibold">{claimData.file_type}</span></>
                )}
                {claimData.page_count > 1 && (
                  <>&nbsp;•&nbsp;{claimData.page_count} pages</>
                )}
              </p>
            </div>
            <button
              onClick={onNewUpload}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-all duration-200 shadow-md"
            >
              ➕ Analyze New Receipt
            </button>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div>
            <ReceiptViewer imageUrl={claimData.image_url} elaImageUrl={claimData.ela_image_url} />
          </div>

          <div className="space-y-6">
            <FraudScoreGauge
              score={claimData.fraud_score}
              riskCategory={claimData.risk_category}
              recommendation={claimData.recommendation}
              breakdown={claimData.score_breakdown}
            />

            {/* Extracted Info */}
            <div className="card p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📝 Extracted Information</h3>
              <div className="space-y-2">
                <DataRow label="Hospital" value={claimData.extracted_data?.hospital_name} />
                <DataRow label="Invoice No." value={claimData.extracted_data?.invoice_number} />
                <DataRow label="Date" value={claimData.extracted_data?.invoice_date} />
                <DataRow
                  label="Total Amount"
                  value={
                    claimData.extracted_data?.total_amount
                      ? `${currency} ${Number(claimData.extracted_data.total_amount).toLocaleString()}`
                      : 'N/A'
                  }
                  highlight
                />
              </div>

              {claimData.extracted_data?.line_items?.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-200">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Line Items</p>
                  <div className="space-y-1">
                    {claimData.extracted_data.line_items.map((item, i) => (
                      <div key={i} className="flex justify-between text-sm bg-gray-50 px-3 py-2 rounded">
                        <span className="text-gray-700">{item.description}</span>
                        <span className="font-semibold text-gray-800">
                          {currency} {Number(item.price).toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* EXIF */}
            {claimData.exif_data && Object.keys(claimData.exif_data).length > 0 && (
              <div className="card p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">🔍 Image Metadata</h3>
                <div className="space-y-2 text-sm">
                  {claimData.exif_data.software && (
                    <div className={`flex justify-between p-2 rounded ${claimData.exif_data.edited_with_software ? 'bg-red-50' : 'bg-gray-50'}`}>
                      <span className="text-gray-600">Software</span>
                      <span className={`font-semibold ${claimData.exif_data.edited_with_software ? 'text-red-700' : 'text-gray-800'}`}>
                        {claimData.exif_data.software}{claimData.exif_data.edited_with_software && ' ⚠️'}
                      </span>
                    </div>
                  )}
                  {claimData.exif_data.device && <DataRow label="Device" value={claimData.exif_data.device} small />}
                  {claimData.exif_data.created_date && <DataRow label="Created" value={claimData.exif_data.created_date} small />}
                  <DataRow
                    label="Screenshot"
                    value={claimData.is_screenshot ? 'Yes ⚠️' : 'No ✓'}
                    small
                    highlight={claimData.is_screenshot}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Red Flags */}
        <div className="mb-6">
          <RedFlagsList redFlags={claimData.red_flags} />
        </div>

        {/* Cost Comparison */}
        {claimData.cost_comparison?.length > 0 && (
          <div className="mb-6">
            <CostComparisonTable costComparison={claimData.cost_comparison} currency={currency} />
          </div>
        )}

        {/* Action Buttons — recommended action is highlighted */}
        <div className="card p-6 mb-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Take Action</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {actionButtons.map(({ label, action, status, color }) => {
              const isThisLoading = actionLoading === status;
              const isThisTaken = actionTaken === status;
              const disabled = !!actionTaken || !!actionLoading || !claimData.claim_id;

              return (
                <button
                  key={status}
                  onClick={() => handleAction(status)}
                  disabled={disabled}
                  className={`${color} text-white px-4 py-3 rounded-lg font-semibold transition-all duration-200 ${
                    isThisTaken
                      ? 'ring-4 ring-offset-2 ring-green-400 scale-105 shadow-lg'
                      : rec === action && !actionTaken
                      ? 'ring-4 ring-offset-2 ring-blue-300 scale-105 shadow-lg'
                      : 'opacity-70'
                  } ${disabled && !isThisTaken ? 'opacity-40 cursor-not-allowed' : ''}`}
                >
                  {isThisLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                      Sending...
                    </span>
                  ) : (
                    <>
                      {label}
                      {isThisTaken && <span className="block text-xs font-normal mt-1">✓ Action taken</span>}
                      {!actionTaken && !isThisLoading && rec === action && (
                        <span className="block text-xs font-normal mt-1">← Recommended</span>
                      )}
                    </>
                  )}
                </button>
              );
            })}
          </div>

          {actionTaken && (
            <div className="mt-4 bg-green-50 border border-green-300 rounded-lg p-3 text-center">
              <p className="text-sm font-semibold text-green-800">
                {smsSent ? 'SMS sent to patient ✓' : 'Status updated — SMS could not be sent'}
              </p>
            </div>
          )}

          {actionError && (
            <div className="mt-4 bg-red-50 border border-red-300 rounded-lg p-3 text-center">
              <p className="text-sm font-semibold text-red-700">{actionError}</p>
            </div>
          )}

          <p className="text-xs text-gray-400 mt-4 text-center">
            {actionTaken
              ? 'This decision is final for this claim.'
              : 'Choose one action — the patient will be notified by SMS and no further changes can be made.'}
          </p>
        </div>

        {/* Export */}
        <div className="text-center space-x-3">
          <button
            onClick={handleExportJSON}
            className="btn btn-ghost px-6 py-2"
          >
            📊 Export JSON Report
          </button>
        </div>

      </div>
    </div>
  );
}

function DataRow({ label, value, highlight = false, small = false }) {
  return (
    <div className={`flex justify-between ${small ? 'text-sm' : ''} ${highlight ? 'bg-yellow-50 p-2 rounded' : 'bg-gray-50 p-2 rounded'}`}>
      <span className="text-gray-600 font-medium">{label}:</span>
      <span className={`font-semibold ${highlight ? 'text-yellow-800' : 'text-gray-800'}`}>
        {value || 'N/A'}
      </span>
    </div>
  );
}

export default ResultsPage;
