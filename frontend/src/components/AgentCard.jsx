import React, { useMemo } from 'react';
import { ShieldAlert, FileText, Users, Briefcase } from 'lucide-react';

const toneClasses = {
  red: 'border-red-200 bg-red-50/60',
  amber: 'border-amber-200 bg-amber-50/60',
  emerald: 'border-emerald-200 bg-emerald-50/60',
  slate: 'border-slate-200 bg-white/70',
};

const riskBadgeClasses = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-emerald-100 text-emerald-700',
};

const AgentCard = ({ title, riskScore, evidence = [], tone = 'slate', icon }) => {
  const scoreLabel = useMemo(() => {
    if (riskScore == null) return 'Unknown';
    if (riskScore >= 0.75) return 'High';
    if (riskScore >= 0.4) return 'Medium';
    return 'Low';
  }, [riskScore]);

  const badgeClass = riskBadgeClasses[scoreLabel.toLowerCase()] || riskBadgeClasses.low;

  const defaultIcon = title?.toLowerCase().includes('provider') ? <ShieldAlert className="w-5 h-5" /> : title?.toLowerCase().includes('claim') ? <Briefcase className="w-5 h-5" /> : title?.toLowerCase().includes('beneficiary') ? <Users className="w-5 h-5" /> : <FileText className="w-5 h-5" />;

  return (
    <div className={`rounded-3xl border p-6 shadow-sm backdrop-blur ${toneClasses[tone] || toneClasses.slate}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/80 p-2 shadow-sm">
            {icon || defaultIcon}
          </div>
          <div>
            <h3 className="text-xl font-black text-slate-800">{title}</h3>
            <p className="text-sm text-slate-500">Agent findings and supporting evidence</p>
          </div>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${badgeClass}`}>
          {scoreLabel} Risk
        </span>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl bg-white/80 p-4 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Risk Score</p>
          <p className="mt-2 text-3xl font-black text-slate-800">{riskScore ?? 'N/A'}</p>
        </div>
        <div className="rounded-2xl bg-white/80 p-4 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Evidence Items</p>
          <p className="mt-2 text-3xl font-black text-slate-800">{Array.isArray(evidence) ? evidence.length : 0}</p>
        </div>
      </div>

      <div className="mt-6">
        <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Evidence</h4>
        {Array.isArray(evidence) && evidence.length > 0 ? (
          <div className="mt-3 overflow-hidden rounded-2xl border border-white/70 bg-white/80">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3 font-semibold">Metric</th>
                  <th className="px-4 py-3 font-semibold">Value</th>
                  <th className="px-4 py-3 font-semibold">Signal</th>
                </tr>
              </thead>
              <tbody>
                {evidence.map((item, index) => (
                  <tr key={`${item.metric || 'metric'}-${index}`} className="border-t border-slate-100">
                    <td className="px-4 py-3 font-medium text-slate-700">{item.metric || '—'}</td>
                    <td className="px-4 py-3 text-slate-700">{item.value ?? '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${item.signal === 'elevated' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'}`}>
                        {item.signal || '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-3 rounded-2xl border border-dashed border-slate-200 bg-white/70 p-4 text-sm text-slate-600">No evidence available.</p>
        )}
      </div>
    </div>
  );
};

export default AgentCard;
