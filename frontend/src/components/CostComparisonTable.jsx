import React from 'react';

function CostComparisonTable({ costComparison, currency = 'KES' }) {
  if (!costComparison || costComparison.length === 0) {
    return (
      <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-6 text-center">
        <p className="text-gray-600">No cost comparison data available</p>
      </div>
    );
  }

  const fmt = (n) => `${currency} ${Number(n).toLocaleString()}`;

  const totalClaimed  = costComparison.reduce((s, i) => s + (i.claimed || 0), 0);
  const totalExpected = costComparison.reduce((s, i) => s + (typeof i.expected === 'number' ? i.expected : 0), 0);
  const overallDev    = totalExpected > 0 ? ((totalClaimed - totalExpected) / totalExpected) * 100 : 0;

  return (
    <div className="cost-comparison bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">💰 Cost Analysis</h3>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <SummaryCard label="Total Claimed"   value={fmt(totalClaimed)}  color="blue" />
        <SummaryCard label="Expected Cost"   value={totalExpected > 0 ? fmt(totalExpected) : 'N/A'} color="green" />
        <SummaryCard
          label="Overall Deviation"
          value={`${overallDev > 0 ? '+' : ''}${overallDev.toFixed(0)}%`}
          color={overallDev > 50 ? 'red' : overallDev > 20 ? 'yellow' : 'green'}
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b-2 border-gray-300">
              <th className="text-left p-3 text-sm font-bold text-gray-700">Service</th>
              <th className="text-right p-3 text-sm font-bold text-gray-700">Claimed</th>
              <th className="text-right p-3 text-sm font-bold text-gray-700">Expected</th>
              <th className="text-right p-3 text-sm font-bold text-gray-700">Deviation</th>
              <th className="text-center p-3 text-sm font-bold text-gray-700">Status</th>
            </tr>
          </thead>
          <tbody>
            {costComparison.map((item, i) => {
              const dev         = item.deviation_pct || 0;
              const isSuspicious = item.suspicious || dev > 50;
              const isUnknown   = typeof item.expected === 'string';
              return (
                <tr key={i} className={`border-b border-gray-200 ${isSuspicious ? 'bg-red-50' : i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                  <td className="p-3 text-sm">
                    <div className="font-medium text-gray-800">{item.description}</div>
                    {item.max_reasonable && (
                      <div className="text-xs text-gray-400 mt-0.5">
                        Market max: {fmt(item.max_reasonable)}
                      </div>
                    )}
                  </td>
                  <td className="p-3 text-right">
                    <span className={`text-sm font-bold ${isSuspicious ? 'text-red-700' : 'text-gray-800'}`}>
                      {fmt(item.claimed)}
                    </span>
                  </td>
                  <td className="p-3 text-right text-sm text-gray-600">
                    {isUnknown ? item.expected : fmt(item.expected)}
                  </td>
                  <td className="p-3 text-right">
                    {isUnknown ? (
                      <span className="text-sm text-gray-400">—</span>
                    ) : (
                      <span className={`text-sm font-bold ${dev > 50 ? 'text-red-600' : dev > 20 ? 'text-yellow-600' : 'text-green-600'}`}>
                        {dev > 0 ? '+' : ''}{dev.toFixed(0)}%
                      </span>
                    )}
                  </td>
                  <td className="p-3 text-center">
                    {isUnknown ? (
                      <Badge color="gray">Unknown</Badge>
                    ) : isSuspicious ? (
                      <Badge color="red">⚠️ Suspicious</Badge>
                    ) : (
                      <Badge color="green">✓ Normal</Badge>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800">
          <span className="font-semibold">Note:</span> Expected costs are based on standard Nairobi private hospital rates in {currency}.
          Items deviating over 50% above market rate are flagged as suspicious.
        </p>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  const styles = {
    blue:   { bg: 'bg-blue-50',   border: 'border-blue-200',   text: 'text-blue-800',   label: 'text-blue-600' },
    green:  { bg: 'bg-green-50',  border: 'border-green-200',  text: 'text-green-800',  label: 'text-green-600' },
    red:    { bg: 'bg-red-50',    border: 'border-red-200',    text: 'text-red-800',    label: 'text-red-600' },
    yellow: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', label: 'text-yellow-600' },
  }[color] || {};
  return (
    <div className={`${styles.bg} p-4 rounded-lg border ${styles.border}`}>
      <p className={`text-xs font-semibold mb-1 ${styles.label}`}>{label}</p>
      <p className={`text-xl font-bold ${styles.text}`}>{value}</p>
    </div>
  );
}

function Badge({ color, children }) {
  const styles = {
    gray:  'bg-gray-200 text-gray-600',
    red:   'bg-red-200 text-red-800',
    green: 'bg-green-200 text-green-800',
  }[color] || '';
  return <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${styles}`}>{children}</span>;
}

export default CostComparisonTable;
