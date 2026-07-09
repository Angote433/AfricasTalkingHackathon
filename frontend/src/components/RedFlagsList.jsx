import React, { useState } from 'react';

function RedFlagsList({ redFlags }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  const severityConfig = {
    CRITICAL: {
      color: 'red',
      icon: '🔴',
      bgColor: '#fee2e2',
      borderColor: '#ef4444',
      textColor: '#991b1b'
    },
    HIGH: {
      color: 'orange',
      icon: '🟠',
      bgColor: '#ffedd5',
      borderColor: '#f97316',
      textColor: '#9a3412'
    },
    MEDIUM: {
      color: 'yellow',
      icon: '🟡',
      bgColor: '#fef3c7',
      borderColor: '#f59e0b',
      textColor: '#92400e'
    },
    LOW: {
      color: 'blue',
      icon: '🔵',
      bgColor: '#dbeafe',
      borderColor: '#3b82f6',
      textColor: '#1e40af'
    }
  };

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  if (!redFlags || redFlags.length === 0) {
    return (
      <div className="bg-green-50 border-2 border-green-300 rounded-xl p-6">
        <div className="flex items-center justify-center">
          <span className="text-3xl mr-3">✅</span>
          <div>
            <h3 className="text-lg font-bold text-green-800">No Red Flags Detected</h3>
            <p className="text-sm text-green-600">This receipt appears to be legitimate</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="red-flags-section">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">
          ⚠️ Red Flags Detected
        </h3>
        <span className="bg-red-100 text-red-800 text-sm font-bold px-3 py-1 rounded-full">
          {redFlags.length} issue{redFlags.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {redFlags.map((flag, index) => {
          const config = severityConfig[flag.severity] || severityConfig.MEDIUM;
          const isExpanded = expandedIndex === index;

          return (
            <div
              key={index}
              className="rounded-lg border-l-4 shadow-sm cursor-pointer transition-all duration-200 hover:shadow-md"
              style={{
                borderLeftColor: config.borderColor,
                backgroundColor: config.bgColor
              }}
              onClick={() => toggleExpand(index)}
            >
              <div className="p-4">
                {/* Header */}
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="text-xl mr-2">{config.icon}</span>
                      <span
                        className="inline-block px-2 py-1 text-xs font-bold rounded"
                        style={{
                          backgroundColor: config.borderColor,
                          color: 'white'
                        }}
                      >
                        {flag.severity}
                      </span>
                      <span className="ml-2 text-sm font-semibold" style={{ color: config.textColor }}>
                        {flag.category}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-sm font-medium" style={{ color: config.textColor }}>
                      {flag.description}
                    </p>

                    {/* Evidence (expandable) */}
                    {isExpanded && flag.evidence && (
                      <div className="mt-3 pt-3 border-t" style={{ borderColor: config.borderColor }}>
                        <p className="text-xs font-semibold mb-1" style={{ color: config.textColor }}>
                          Evidence:
                        </p>
                        <p className="text-xs" style={{ color: config.textColor }}>
                          {flag.evidence}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Confidence & Expand Icon */}
                  <div className="ml-4 flex flex-col items-end">
                    <span className="text-xs font-semibold mb-1" style={{ color: config.textColor }}>
                      {flag.confidence} confidence
                    </span>
                    <svg
                      className={`w-5 h-5 transition-transform duration-200 ${isExpanded ? 'transform rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      style={{ color: config.textColor }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-700">
          <span className="font-semibold">Summary:</span> {redFlags.length} suspicious indicator
          {redFlags.length !== 1 ? 's' : ''} detected.{' '}
          {redFlags.filter(f => f.severity === 'CRITICAL').length > 0 && (
            <span className="font-bold text-red-600">
              {redFlags.filter(f => f.severity === 'CRITICAL').length} critical issue
              {redFlags.filter(f => f.severity === 'CRITICAL').length !== 1 ? 's' : ''} require
              {redFlags.filter(f => f.severity === 'CRITICAL').length === 1 ? 's' : ''} immediate attention.
            </span>
          )}
        </p>
      </div>
    </div>
  );
}

export default RedFlagsList;