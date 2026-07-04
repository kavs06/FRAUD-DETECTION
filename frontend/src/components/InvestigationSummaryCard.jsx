import React from 'react';

const toneClasses = {
  red: 'from-red-50 to-white border-red-100 text-red-700',
  amber: 'from-amber-50 to-white border-amber-100 text-amber-700',
  emerald: 'from-emerald-50 to-white border-emerald-100 text-emerald-700',
  slate: 'from-slate-50 to-white border-slate-200 text-slate-700',
};

const InvestigationSummaryCard = ({ title, value, subtitle, tone = 'slate', icon }) => {
  return (
    <div className={`rounded-2xl border bg-gradient-to-br ${toneClasses[tone] || toneClasses.slate} p-4 shadow-sm`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{title}</p>
        {icon}
      </div>
      <div className="mt-3">
        <p className="text-2xl font-black text-slate-800">{value}</p>
        {subtitle ? <p className="mt-1 text-sm text-slate-600">{subtitle}</p> : null}
      </div>
    </div>
  );
};

export default InvestigationSummaryCard;
