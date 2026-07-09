import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const COLOR_MAP = {
  green:  { path: '#10b981', bg: '#d1fae5', border: '#10b981', text: '#065f46' },
  yellow: { path: '#f59e0b', bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
  orange: { path: '#f97316', bg: '#ffedd5', border: '#f97316', text: '#9a3412' },
  red:    { path: '#ef4444', bg: '#fee2e2', border: '#ef4444', text: '#991b1b' },
};

function getColor(score) {
  if (score < 25) return 'green';
  if (score < 55) return 'yellow';
  if (score < 80) return 'orange';
  return 'red';
}

function BreakdownBar({ label, value, max = 35 }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = value > max * 0.6 ? '#ef4444' : value > max * 0.3 ? '#f59e0b' : '#10b981';
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{label}</span>
        <span className="font-semibold" style={{ color }}>{value.toFixed(1)} pts</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

function FraudScoreGauge({ score, riskCategory, recommendation, breakdown }) {
  const colorKey = getColor(score);
  const colors   = COLOR_MAP[colorKey];

  const icon = score < 25 ? '✅' : score < 55 ? '⚠️' : score < 80 ? '🚨' : '❌';

  const summaryText = {
    LOW:      'This claim appears legitimate with no significant red flags.',
    MEDIUM:   'Some suspicious indicators detected. Manual review recommended.',
    HIGH:     'Multiple fraud indicators found. Detailed investigation required.',
    CRITICAL: 'High probability of fraud. Strong evidence of manipulation detected.',
  }[riskCategory] || '';

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">Fraud Risk Assessment</h2>

      <div className="w-40 mx-auto mb-4">
        <CircularProgressbar
          value={score}
          text={`${Math.round(score)}`}
          styles={buildStyles({
            pathColor: colors.path,
            textColor: '#1f2937',
            trailColor: '#e5e7eb',
            textSize: '28px',
            pathTransitionDuration: 1.2,
          })}
        />
      </div>

      <div
        className="p-3 rounded-lg border-2 mb-4 text-center"
        style={{ backgroundColor: colors.bg, borderColor: colors.border }}
      >
        <span className="text-2xl mr-2">{icon}</span>
        <span className="text-lg font-bold" style={{ color: colors.text }}>
          {riskCategory} RISK
        </span>
        <p className="text-sm font-semibold mt-1" style={{ color: colors.text }}>
          Recommendation: {recommendation}
        </p>
      </div>

      {/* Score breakdown */}
      {breakdown && (
        <div className="border-t border-gray-100 pt-4 mt-2">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Score Breakdown</p>
          <BreakdownBar label="Image Forensics (35%)"  value={breakdown.image_forensics} max={35} />
          <BreakdownBar label="Cost Deviation (35%)"   value={breakdown.cost_deviation}  max={35} />
          <BreakdownBar label="Business Rules (20%)"   value={breakdown.business_rules}  max={20} />
          <BreakdownBar label="Screenshot Flag (10%)"  value={breakdown.screenshot_flag} max={10} />
        </div>
      )}

      <p className="text-xs text-gray-400 text-center mt-4">{summaryText}</p>
    </div>
  );
}

export default FraudScoreGauge;
