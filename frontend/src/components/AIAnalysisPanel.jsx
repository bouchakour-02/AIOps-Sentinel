import { useState } from 'react';
import { X, BrainCircuit, Terminal, TrendingUp, CheckCircle2, AlertCircle, Search } from 'lucide-react';
import clsx from 'clsx';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';

const SEVERITY_COLORS = {
    critical: 'text-critical',
    warning: 'text-warning',
    info: 'text-primary-400',
};

const FEEDBACK_OPTIONS = [
    { id: 'accurate', label: '✅ Accurate', hoverClass: 'hover:bg-success/10 hover:border-success/30 hover:text-success' },
    { id: 'false-positive', label: '❌ False Positive', hoverClass: 'hover:bg-critical/10 hover:border-critical/30 hover:text-critical' },
    { id: 'need-logs', label: '🔍 Need more logs', hoverClass: 'hover:bg-primary-400/10 hover:border-primary-400/30 hover:text-primary-400' },
];

export default function AIAnalysisPanel({ incident, onClose }) {
    const [feedback, setFeedback] = useState(null);

    if (!incident) return null;

    const sevColor = SEVERITY_COLORS[incident.severity] || 'text-slate-300';
    const chartColor = incident.severity === 'critical' ? '#f43f5e' : incident.severity === 'warning' ? '#f59e0b' : '#3b82f6';

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 animate-fade-in"
                onClick={onClose}
            />

            {/* Panel */}
            <div className="fixed right-0 top-0 h-full w-full max-w-xl bg-navy-900 border-l border-navy-700 z-40 flex flex-col animate-slide-in shadow-2xl">
                {/* Header */}
                <div className="flex items-start justify-between px-6 py-5 border-b border-navy-700">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-[10px] font-tech text-slate-500">{incident.id}</span>
                            <span className={clsx('badge bg-navy-800 border border-navy-600 text-[10px] font-tech uppercase', sevColor)}>
                                {incident.severity}
                            </span>
                            <span className="badge bg-anomaly/10 text-anomaly border border-anomaly/20 text-[9px] font-tech">
                                Score: {incident.anomalyScore}
                            </span>
                        </div>
                        <h2 className="text-base font-bold text-slate-100">{incident.title}</h2>
                        <p className="text-xs text-slate-500 mt-0.5">
                            {incident.service} · {incident.metric}: <span className="text-slate-300 font-medium font-tech">{incident.metricValue}{incident.metricUnit}</span>
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="btn-ghost p-1.5 rounded-lg text-slate-400 hover:text-white"
                    >
                        <X size={16} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                    {/* Metric Spike Chart */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingUp size={13} className={sevColor} />
                            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Metric Spike</h3>
                        </div>
                        <div className="bg-navy-800 border border-navy-700 rounded-xl p-4">
                            <ResponsiveContainer width="100%" height={120}>
                                <AreaChart data={incident.metricSpike} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="spikeGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor={chartColor} stopOpacity={0.3} />
                                            <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="time" tick={{ fill: '#475569', fontSize: 9 }} axisLine={false} tickLine={false} interval={2} />
                                    <YAxis tick={{ fill: '#475569', fontSize: 9 }} axisLine={false} tickLine={false} />
                                    <Tooltip
                                        contentStyle={{ background: '#1e293b', border: '1px solid #253352', borderRadius: '8px', fontSize: '11px' }}
                                        labelStyle={{ color: '#94a3b8' }}
                                        itemStyle={{ color: '#e2e8f0' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="cpu"
                                        name="CPU %"
                                        stroke={chartColor}
                                        strokeWidth={2}
                                        fill="url(#spikeGrad)"
                                        dot={false}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* AI Diagnosis */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <BrainCircuit size={13} className="text-anomaly" />
                            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">AI Diagnosis</h3>
                            <span className="badge bg-anomaly/10 text-anomaly border border-anomaly/20 text-[9px] ml-auto font-tech">
                                Ministral-3B Analysis
                            </span>
                        </div>
                        <div className="bg-navy-800 border border-navy-700 rounded-xl p-4">
                            <p className="text-sm text-slate-300 leading-relaxed">{incident.aiDiagnosis}</p>
                        </div>
                    </div>

                    {/* Log Snippet */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Terminal size={13} className="text-slate-400" />
                            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Log Evidence</h3>
                        </div>
                        <pre className="bg-navy-950 border border-navy-700 rounded-xl px-4 py-3 text-[11px] text-slate-400 font-tech leading-relaxed overflow-x-auto whitespace-pre-wrap break-all">{incident.logSnippet}</pre>
                    </div>

                    {/* Technical Recommendation */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <Terminal size={13} className="text-success" />
                            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Technical Recommendation</h3>
                        </div>
                        <div className="relative">
                            <pre className="bg-navy-950 border border-success/20 rounded-xl px-4 py-4 text-[11px] text-success font-tech leading-relaxed overflow-x-auto whitespace-pre-wrap">{incident.recommendation}</pre>
                            <span className="absolute top-2 right-2 badge bg-success/10 text-success border border-success/20 text-[9px] font-tech font-bold uppercase">
                                kubectl
                            </span>
                        </div>
                    </div>

                    {/* Feedback Loop (Human-in-the-loop) */}
                    <div className="pt-4 border-t border-navy-800">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Feedback for Ministral-3B</h3>
                            <span className="text-[10px] text-slate-600 font-tech">Reinforcement Learning active</span>
                        </div>

                        {feedback ? (
                            <div className="flex items-center gap-2 py-3 px-4 rounded-lg bg-success/5 border border-success/20">
                                <CheckCircle2 size={14} className="text-success shrink-0" />
                                <p className="text-xs text-success font-medium">
                                    Feedback recorded: <span className="font-tech">{feedback}</span> — Thank you!
                                </p>
                            </div>
                        ) : (
                            <div className="flex flex-wrap gap-2">
                                {FEEDBACK_OPTIONS.map(opt => (
                                    <button
                                        key={opt.id}
                                        onClick={() => setFeedback(opt.label)}
                                        className={clsx(
                                            'flex-1 min-w-[100px] flex items-center justify-center gap-2 py-2.5 rounded-lg bg-navy-800 border border-slate-700/50 text-[11px] font-medium text-slate-300 transition-all duration-150 cursor-pointer',
                                            opt.hoverClass
                                        )}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer actions */}
                <div className="px-6 py-4 border-t border-navy-700 flex items-center gap-3">
                    <button className="btn-primary flex-1 justify-center py-2">
                        Acknowledge Incident
                    </button>
                    <button className="btn-ghost border border-navy-600 flex-1 justify-center py-2">
                        Escalate to On-Call
                    </button>
                </div>
            </div>
        </>
    );
}
