import React, { useState } from 'react';
import axios from 'axios';
import {
  FileText,
  ChevronRight,
  Activity,
  Search,
  Sparkles
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

import {
  AreaChart,
  Area,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const Explainability = () => {
  const [providerId, setProviderId] = useState('');
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);

  const { token } = useAuth();

  const handleExplain = async (e) => {
    e.preventDefault();

    if (!providerId) {
      alert('Please enter a Provider ID');
      return;
    }

    setLoading(true);

    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/explain/${providerId}`
      );

      console.log('Explainability Response:', res.data);

      setExplanation(res.data);
    } catch (error) {
      console.error('Explainability Error:', error);

      alert(
        error.response?.data?.detail ||
        error.message ||
        'Failed to generate report'
      );
    } finally {
      setLoading(false);
    }
  };

  const mockShapData =
    explanation?.feature_importance?.map((item) => ({
      name: item.feature,
      value: item.impact
    })) || [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in-up pb-10">
      <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white relative overflow-hidden">

        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500 rounded-full mix-blend-multiply filter blur-[80px] opacity-20 pointer-events-none"></div>

        {/* Header */}
        <div className="flex items-center mb-8 relative z-10">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mr-5 shadow-lg shadow-indigo-500/30">
            <FileText className="w-8 h-8 text-white" />
          </div>

          <div>
            <h2 className="text-3xl font-black text-slate-800 tracking-tight">
              AI Explainability
            </h2>

            <p className="text-slate-500 font-medium">
              SHAP-based transparent feature analysis for flagged providers.
            </p>
          </div>
        </div>

        {/* Search Form */}
        <form
          onSubmit={handleExplain}
          className="flex gap-4 mb-8 relative z-10"
        >
          <div className="flex-1 relative group">
            <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5 group-focus-within:text-indigo-500 transition-colors" />

            <input
              type="text"
              value={providerId}
              onChange={(e) => setProviderId(e.target.value)}
              placeholder="Enter Provider ID (e.g., P123)"
              className="w-full pl-14 pr-4 py-4 bg-slate-100/50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-700"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-8 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-bold rounded-2xl transition-all flex items-center justify-center disabled:opacity-50 shadow-lg shadow-indigo-500/30 hover:-translate-y-0.5"
          >
            {loading ? (
              <div className="flex items-center">
                <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                Analyzing...
              </div>
            ) : (
              'Generate Report'
            )}
          </button>
        </form>

        {/* Results */}
        {explanation && (
          <div className="space-y-8 animate-fade-in-up relative z-10">

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

              {/* Top Features */}
              <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center">
                  <Activity className="w-6 h-6 mr-3 text-indigo-600" />
                  Top Risk Factors
                </h3>

                <ul className="space-y-4">
                  {explanation.top_features?.map((feature, idx) => (
                    <li
                      key={idx}
                      className="flex items-center text-slate-700 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm"
                    >
                      <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mr-4">
                        <ChevronRight className="w-4 h-4 text-indigo-600" />
                      </div>

                      <span className="font-bold">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Feature Importance */}
              <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xl font-bold text-slate-800 mb-6">
                  SHAP Feature Impact
                </h3>

                <div className="space-y-6">
                  {explanation.feature_importance?.map((item, idx) => (
                    <div key={idx}>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-700 font-bold">
                          {item.feature}
                        </span>

                        <span className="text-indigo-600 font-bold">
                          {(item.impact * 100).toFixed(0)}% impact
                        </span>
                      </div>

                      <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-1000"
                          style={{
                            width: `${item.impact * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* AI Summary */}
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100/50 rounded-3xl p-8 border border-indigo-100 shadow-inner">
              <h3 className="text-2xl font-bold text-indigo-900 mb-4 flex items-center">
                <Sparkles className="w-6 h-6 mr-3 text-indigo-600" />
                AI Generated Summary
              </h3>

              <p className="text-indigo-900 whitespace-pre-wrap leading-relaxed">
                {explanation.shap_summary}
              </p>

              {/* Chart */}
              <div className="mt-8 h-64 bg-white rounded-2xl border border-indigo-200 p-6 shadow-sm">
                <h4 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-4">
                  Impact Visualization
                </h4>

                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockShapData}>
                    <Tooltip />

                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default Explainability;