import React, { useState } from 'react';
import axios from 'axios';
import {
  Search,
  ShieldAlert,
  CheckCircle,
  Activity,
  Stethoscope,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  FileText,
  Briefcase,
  Users,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import InvestigationSummaryCard from '../components/InvestigationSummaryCard';
import AgentCard from '../components/AgentCard';
import RecommendationList from '../components/RecommendationList';

const ProviderSearch = () => {
  const [providerId, setProviderId] = useState('');
  const [result, setResult] = useState(null);
  const [investigationResult, setInvestigationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [investigationLoading, setInvestigationLoading] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  const { token } = useAuth();

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!providerId) return;

    setLoading(true);

    try {
      const explainRes = await axios.get(
        `http://127.0.0.1:8000/explain/${providerId}`
      );

      setResult(explainRes.data);

    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleInvestigate = async () => {
    if (!providerId) return;

    setInvestigationLoading(true);

    try {
      const investigateRes = await axios.post(
        'http://127.0.0.1:8000/investigate',
        { provider_id: providerId }
      );

      setInvestigationResult(investigateRes.data);
    } catch (error) {
      console.error(error);
      setInvestigationResult({ error: 'Investigation failed' });
    } finally {
      setInvestigationLoading(false);
    }
  };

  const getRiskTone = (score) => {
    if (score == null) return 'slate';
    if (score >= 0.75) return 'red';
    if (score >= 0.4) return 'amber';
    return 'emerald';
  };

  const getRiskLabel = (score) => {
    if (score == null) return 'Unknown';
    if (score >= 0.75) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  const coordinator = investigationResult?.investigation_summary?.coordinator;
  const providerAnalysis = investigationResult?.investigation_summary?.provider;
  const claimAnalysis = investigationResult?.investigation_summary?.claim;
  const beneficiaryAnalysis = investigationResult?.investigation_summary?.beneficiary;
  const overallRisk = coordinator?.['Fraud Score'] ?? investigationResult?.fraud_probability;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in-up pb-10">
      <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white relative overflow-hidden">

        <div className="absolute top-[-50px] right-[-50px] w-64 h-64 bg-teal-400 rounded-full mix-blend-multiply filter blur-[80px] opacity-20 pointer-events-none"></div>

        <div className="flex items-center mb-8 relative z-10">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-600 flex items-center justify-center mr-5 shadow-lg shadow-teal-500/30">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>

          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">
              Provider Risk Assessment
            </h2>

            <p className="text-slate-500 font-medium">
              Real-time fraud scoring powered by Ensemble Machine Learning.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSearch}
          className="flex gap-4 mb-8 relative z-10"
        >
          <div className="flex-1 relative group">
            <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 group-focus-within:text-teal-500 transition-colors" />

            <input
              type="text"
              value={providerId}
              onChange={(e) => setProviderId(e.target.value)}
              placeholder="Enter Provider ID (e.g., P123)"
              className="w-full pl-14 pr-4 py-4 bg-slate-100/50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium text-slate-700"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-8 bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white font-bold rounded-2xl transition-all flex items-center justify-center disabled:opacity-50 shadow-lg shadow-teal-500/30 hover:-translate-y-0.5"
          >
            {loading ? (
              <div className="flex items-center">
                <Activity className="w-5 h-5 mr-2 animate-spin" />
                Analyzing...
              </div>
            ) : (
              'Analyze Provider'
            )}
          </button>

          <button
            type="button"
            onClick={handleInvestigate}
            disabled={investigationLoading}
            className="px-8 bg-gradient-to-r from-amber-600 to-orange-500 hover:from-amber-500 hover:to-orange-400 text-white font-bold rounded-2xl transition-all flex items-center justify-center disabled:opacity-50 shadow-lg shadow-orange-500/30 hover:-translate-y-0.5"
          >
            {investigationLoading ? (
              <div className="flex items-center">
                <Activity className="w-5 h-5 mr-2 animate-spin" />
                Investigating...
              </div>
            ) : (
              'Investigate'
            )}
          </button>
        </form>

        {investigationResult && !investigationResult.error && (
          <div className="animate-fade-in-up relative z-10 mt-10 space-y-6">
            <div className="rounded-3xl border border-amber-100 bg-gradient-to-br from-amber-50 to-white p-8 shadow-xl">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex items-center gap-2 text-amber-700">
                    <Sparkles className="h-5 w-5" />
                    <p className="text-sm font-semibold uppercase tracking-[0.2em]">Investigation Report</p>
                  </div>
                  <h3 className="mt-3 text-3xl font-black text-slate-800">
                    {investigationResult.Provider}
                  </h3>
                  <p className="mt-2 max-w-2xl text-slate-600">
                    The backend returned the complete multi-agent investigation payload. This dashboard presents the provider, claim, beneficiary, and coordinator findings in a structured view for fraud review.
                  </p>
                </div>
                <div className={`rounded-2xl border px-4 py-3 ${getRiskTone(overallRisk) === 'red' ? 'border-red-200 bg-red-100/70 text-red-700' : getRiskTone(overallRisk) === 'amber' ? 'border-amber-200 bg-amber-100/70 text-amber-700' : 'border-emerald-200 bg-emerald-100/70 text-emerald-700'}`}>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em]">Overall Risk</p>
                  <p className="mt-1 text-2xl font-black">{getRiskLabel(overallRisk)}</p>
                </div>
              </div>

              <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                <InvestigationSummaryCard title="Provider ID" value={investigationResult.Provider} subtitle="Investigated provider" tone="slate" icon={<ShieldAlert className="h-5 w-5 text-slate-600" />} />
                <InvestigationSummaryCard title="Fraud Score" value={`${Number(investigationResult.fraud_probability * 100).toFixed(1)}%`} subtitle="Model probability" tone={getRiskTone(investigationResult.fraud_probability)} icon={<AlertTriangle className="h-5 w-5" />} />
                <InvestigationSummaryCard title="Overall Risk" value={getRiskLabel(overallRisk)} subtitle="Coordinator assessment" tone={getRiskTone(overallRisk)} icon={<ShieldAlert className="h-5 w-5" />} />
                <InvestigationSummaryCard title="Priority" value={coordinator?.Priority || 'N/A'} subtitle="Coordinator priority" tone="amber" icon={<FileText className="h-5 w-5" />} />
                <InvestigationSummaryCard title="Confidence" value={coordinator?.Confidence || 'N/A'} subtitle="Coordinator confidence" tone="slate" icon={<Sparkles className="h-5 w-5" />} />
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <AgentCard title="Provider Analysis" riskScore={providerAnalysis?.risk_score} evidence={providerAnalysis?.evidence} tone="red" icon={<ShieldAlert className="w-5 h-5" />} />
              <AgentCard title="Claim Analysis" riskScore={claimAnalysis?.risk_score} evidence={claimAnalysis?.evidence} tone="amber" icon={<Briefcase className="w-5 h-5" />} />
              <AgentCard title="Beneficiary Analysis" riskScore={beneficiaryAnalysis?.risk_score} evidence={beneficiaryAnalysis?.evidence} tone="emerald" icon={<Users className="w-5 h-5" />} />
              <div className="rounded-3xl border border-slate-200 bg-white/70 p-6 shadow-sm backdrop-blur">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-xl font-black text-slate-800">Coordinator Report</h3>
                    <p className="text-sm text-slate-500">Executive summary and next actions</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-sm font-semibold ${getRiskTone(overallRisk) === 'red' ? 'bg-red-100 text-red-700' : getRiskTone(overallRisk) === 'amber' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                    {getRiskLabel(overallRisk)}
                  </span>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl bg-slate-50/70 p-4">
                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Priority</p>
                    <p className="mt-2 text-xl font-black text-slate-800">{coordinator?.Priority || 'N/A'}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50/70 p-4">
                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Confidence</p>
                    <p className="mt-2 text-xl font-black text-slate-800">{coordinator?.Confidence || 'N/A'}</p>
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Recommendations</h4>
                  <RecommendationList recommendations={coordinator?.Recommendation} />
                </div>

                <div className="mt-6">
                  <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Coordinator Evidence</h4>
                  {Array.isArray(coordinator?.Evidence) && coordinator.Evidence.length > 0 ? (
                    <ul className="mt-3 space-y-2">
                      {coordinator.Evidence.slice(0, 8).map((item, index) => (
                        <li key={`${item.metric || 'metric'}-${index}`} className="rounded-2xl border border-slate-200 bg-white/80 p-3 text-sm text-slate-700 shadow-sm">
                          <span className="font-semibold text-slate-800">{item.metric || '—'}</span>: {item.value ?? '—'} {item.signal ? `(${item.signal})` : ''}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-3 rounded-2xl border border-dashed border-slate-200 bg-white/70 p-4 text-sm text-slate-600">No evidence available.</p>
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white/70 p-6 shadow-sm backdrop-blur">
              <button
                type="button"
                onClick={() => setShowRawJson((value) => !value)}
                className="flex w-full items-center justify-between rounded-2xl bg-slate-50 px-4 py-3 text-left text-lg font-bold text-slate-800"
              >
                <span>View Raw Investigation JSON</span>
                {showRawJson ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
              </button>
              {showRawJson ? (
                <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-sm text-slate-100">
                  {JSON.stringify(investigationResult, null, 2)}
                </pre>
              ) : null}
            </div>
          </div>
        )}

        {result && (
          <div className="animate-fade-in-up relative z-10 mt-10">
            <div
              className={`p-8 rounded-3xl border shadow-xl flex flex-col md:flex-row items-center justify-between transition-all duration-500 ${result.risk_level === 'High'
                ? 'bg-gradient-to-br from-red-50 to-white border-red-100'
                : 'bg-gradient-to-br from-emerald-50 to-white border-emerald-100'
                }`}
            >
              <div className="md:pr-10 mb-6 md:mb-0">
                <h3 className="text-2xl font-black text-slate-800 mb-2">
                  Analysis Results for {result.provider_id}
                </h3>

                <p className="text-slate-600 mb-6 font-medium leading-relaxed">
                  The ML engine has completed fraud risk assessment.
                </p>

                <div className="flex items-center space-x-3 bg-white/60 p-4 rounded-xl border border-white shadow-sm inline-flex">
                  <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">
                    Action Required:
                  </span>

                  {result.risk_level === 'High' ? (
                    <span className="text-md font-black text-red-600 bg-red-100/50 px-3 py-1 rounded-lg">
                      Escalate for Manual Audit
                    </span>
                  ) : (
                    <span className="text-md font-black text-emerald-600 bg-emerald-100/50 px-3 py-1 rounded-lg">
                      No Action Required
                    </span>
                  )}
                </div>
              </div>

              <div className="flex flex-col items-center justify-center p-8 bg-white/80 backdrop-blur-md rounded-3xl border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] min-w-[200px]">
                <span className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">
                  Fraud Score
                </span>

                <div className="flex items-center justify-center">
                  {result.risk_level === 'High' ? (
                    <ShieldAlert className="w-10 h-10 text-red-500 mr-3 animate-pulse" />
                  ) : (
                    <CheckCircle className="w-10 h-10 text-emerald-500 mr-3" />
                  )}

                  <span
                    className={`text-6xl font-black tracking-tighter ${result.risk_level === 'High'
                      ? 'text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-rose-400'
                      : 'text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-400'
                      }`}
                  >
                    {result.fraud_score}
                  </span>

                  <span className="text-3xl font-bold text-slate-300 ml-1">
                    %
                  </span>
                </div>

                <div className="mt-4 text-center">
                  <p className="font-bold text-slate-700">
                    Risk Level: {result.risk_level}
                  </p>

                  <p className="text-sm text-slate-500">
                    Prediction: {result.prediction}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProviderSearch;