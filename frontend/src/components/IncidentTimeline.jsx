import clsx from 'clsx';
import { Zap, Clock, Eye } from 'lucide-react';

const SEVERITY_CONFIG = {
    critical: { label: 'Critical', bg: 'bg-critical/10', text: 'text-critical', border: 'border-critical/20', dot: 'bg-critical', glow: true },
    error: { label: 'Error', bg: 'bg-critical/10', text: 'text-critical', border: 'border-critical/20', dot: 'bg-critical', glow: true },
    warning: { label: 'Warning', bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/20', dot: 'bg-warning', glow: false },
    info: { label: 'Info', bg: 'bg-primary-500/10', text: 'text-primary-400', border: 'border-primary-500/20', dot: 'bg-primary-400', glow: false },
};

function formatRelTime(iso) {
    if (!iso) return 'Unknown';
    const diff = Date.now() - new Date(iso).getTime();
    if (diff < 0) return 'Just now';
    const m = Math.floor(diff / 60_000);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    return `${h}h ${m % 60}m ago`;
}

export default function IncidentTimeline({ logs = [], onSelect }) {
    if (logs.length === 0) {
        return (
            <div className="card glass-panel flex-1">
                <div className="flex items-center justify-between mb-5">
                    <div>
                        <h2 className="text-sm font-semibold text-slate-100 italic tracking-tight">Incident Stream</h2>
                        <p className="text-[10px] text-slate-500 mt-0.5 font-tech uppercase tracking-widest">Live from Elasticsearch</p>
                    </div>
                </div>
                <div className="flex items-center justify-center h-40 text-slate-500 text-xs font-tech">
                    <div className="flex flex-col items-center gap-2">
                        <div className="w-5 h-5 border-2 border-primary-500/40 border-t-primary-400 rounded-full animate-spin" />
                        Waiting for logs…
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card glass-panel flex-1">
            <div className="flex items-center justify-between mb-5">
                <div>
                    <h2 className="text-sm font-semibold text-slate-100 italic tracking-tight">Incident Stream</h2>
                    <p className="text-[10px] text-slate-500 mt-0.5 font-tech uppercase tracking-widest">
                        LIVE FROM ELASTICSEARCH · {logs.length} LOG{logs.length !== 1 ? 'S' : ''}
                    </p>
                </div>
                <span className="badge bg-primary-500/10 text-primary-400 border border-primary-500/30 text-[9px] font-tech font-bold uppercase">
                    <Zap size={10} /> LIVE_FEED
                </span>
            </div>

            <div className="relative">
                <div className="absolute left-[17px] top-0 bottom-0 w-px bg-navy-700/50" />

                <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1 custom-scrollbar">
                    {logs.map((log, idx) => {
                        const sev = SEVERITY_CONFIG[log.severity] || SEVERITY_CONFIG.info;
                        const isCritical = log.severity === 'critical' || log.severity === 'error';
                        const hasCriticalMsg = (log.message || '').toUpperCase().includes('CRITICAL');

                        const incident = {
                            id: `LIVE-${idx}`,
                            timestamp: log.timestamp,
                            service: log.service || 'unknown',
                            severity: log.severity,
                            title: log.message ? log.message.substring(0, 80) : 'No message',
                            logSnippet: log.message,
                            aiDiagnosis: 'Live log fetched from Elasticsearch via the Otel pipeline.',
                            recommendation: 'Check service health and review surrounding log context.',
                        };

                        return (
                            <div
                                key={`${log.timestamp}-${idx}`}
                                className={clsx(
                                    'relative flex gap-4 p-3 rounded-xl border transition-all duration-300 cursor-pointer group',
                                    (isCritical || hasCriticalMsg)
                                        ? 'bg-critical/5 border-critical/30 glow-critical hover:bg-critical/10'
                                        : 'bg-navy-800/30 border-navy-700/50 hover:bg-navy-800 hover:border-navy-600'
                                )}
                                onClick={() => onSelect(incident)}
                            >
                                {/* Timeline dot */}
                                <div className={clsx('w-2 h-2 rounded-full mt-2 shrink-0 z-10 ring-4 ring-navy-950', sev.dot)} />

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-2 mb-2">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className="text-xs font-bold text-slate-100 tracking-tight">{log.service || 'unknown'}</span>
                                            <span className={clsx('badge border text-[9px] font-tech font-bold uppercase', sev.bg, sev.text, sev.border)}>
                                                {sev.label}
                                            </span>
                                            {hasCriticalMsg && (
                                                <span className="badge bg-critical/20 text-critical border border-critical/40 text-[9px] font-tech font-bold uppercase animate-pulse">
                                                    🔴 CRITICAL
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Log message with JetBrains Mono */}
                                    <pre className="text-[10px] text-slate-400 bg-black/40 border border-white/5 rounded-lg px-3 py-2 font-tech leading-relaxed line-clamp-2 whitespace-pre-wrap break-all opacity-80 group-hover:opacity-100 transition-opacity">
                                        {log.message || 'Empty log body'}
                                    </pre>

                                    <div className="flex items-center justify-between mt-3">
                                        <span className="text-[9px] text-slate-600 font-tech uppercase tracking-widest flex items-center gap-1">
                                            <Clock size={10} /> {formatRelTime(log.timestamp)}
                                        </span>
                                        <span className="text-[9px] text-slate-600 font-tech">
                                            {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
