import React from 'react';

const RecommendationList = ({ recommendations = [] }) => {
  if (!Array.isArray(recommendations) || recommendations.length === 0) {
    return <p className="mt-3 rounded-2xl border border-dashed border-slate-200 bg-white/70 p-4 text-sm text-slate-600">No recommendations.</p>;
  }

  return (
    <ul className="mt-3 space-y-2">
      {recommendations.map((item, index) => (
        <li key={`${item}-${index}`} className="flex items-start gap-2 rounded-2xl border border-slate-200 bg-white/80 p-3 text-sm text-slate-700 shadow-sm">
          <span className="mt-1 h-2.5 w-2.5 flex-none rounded-full bg-amber-500" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
};

export default RecommendationList;
