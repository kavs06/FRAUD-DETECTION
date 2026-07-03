import React from 'react';
import { Users, AlertTriangle, ShieldAlert, TrendingUp, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', risk: 4000, baseline: 2400 },
  { name: 'Feb', risk: 3000, baseline: 1398 },
  { name: 'Mar', risk: 2000, baseline: 9800 },
  { name: 'Apr', risk: 2780, baseline: 3908 },
  { name: 'May', risk: 1890, baseline: 4800 },
  { name: 'Jun', risk: 2390, baseline: 3800 },
  { name: 'Jul', risk: 3490, baseline: 4300 },
];

const Dashboard = () => {
  return (
    <div className="space-y-8 animate-fade-in-up pb-10">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-3xl font-black text-slate-800 tracking-tight">System Overview</h2>
          <p className="text-slate-500 font-medium">Real-time fraud detection metrics.</p>
        </div>
        <div className="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-xl font-bold flex items-center shadow-sm">
          <Activity className="w-5 h-5 mr-2 animate-pulse" />
          System Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Metric Cards */}
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white flex items-center transform transition-transform hover:-translate-y-2 duration-300">
          <div className="bg-gradient-to-br from-blue-400 to-blue-600 p-4 rounded-2xl text-white mr-5 shadow-lg shadow-blue-500/30">
            <Users className="w-7 h-7" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-bold uppercase tracking-wider">Total Providers</p>
            <h3 className="text-3xl font-black text-slate-800">5,423</h3>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white flex items-center transform transition-transform hover:-translate-y-2 duration-300">
          <div className="bg-gradient-to-br from-red-400 to-rose-600 p-4 rounded-2xl text-white mr-5 shadow-lg shadow-red-500/30">
            <AlertTriangle className="w-7 h-7" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-bold uppercase tracking-wider">Flagged Providers</p>
            <h3 className="text-3xl font-black text-slate-800">142</h3>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white flex items-center transform transition-transform hover:-translate-y-2 duration-300">
          <div className="bg-gradient-to-br from-amber-400 to-orange-500 p-4 rounded-2xl text-white mr-5 shadow-lg shadow-amber-500/30">
            <ShieldAlert className="w-7 h-7" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-bold uppercase tracking-wider">High Risk Claims</p>
            <h3 className="text-3xl font-black text-slate-800">$2.4M</h3>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white flex items-center transform transition-transform hover:-translate-y-2 duration-300">
          <div className="bg-gradient-to-br from-emerald-400 to-teal-500 p-4 rounded-2xl text-white mr-5 shadow-lg shadow-emerald-500/30">
            <TrendingUp className="w-7 h-7" />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-bold uppercase tracking-wider">Fraud Trend</p>
            <h3 className="text-3xl font-black text-slate-800">+12%</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white min-h-[400px]">
          <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center">
            Risk Distribution Over Time
          </h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBaseline" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }} />
                <Area type="monotone" dataKey="risk" stroke="#4f46e5" strokeWidth={3} fillOpacity={1} fill="url(#colorRisk)" />
                <Area type="monotone" dataKey="baseline" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorBaseline)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Recent Alerts</h3>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((item) => (
              <div key={item} className="group flex items-center justify-between p-5 border border-slate-100 rounded-2xl bg-white hover:bg-slate-50 transition-all duration-300 hover:shadow-md cursor-pointer">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-red-500 mr-4 group-hover:scale-150 transition-transform"></div>
                  <div>
                    <p className="font-bold text-slate-800">Provider PRV10{80 + item}</p>
                    <p className="text-xs text-slate-500 mt-1 font-medium">Unusual billing detected</p>
                  </div>
                </div>
                <span className="px-4 py-2 bg-red-50 text-red-600 rounded-xl text-sm font-bold border border-red-100">
                  {90 + item}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
