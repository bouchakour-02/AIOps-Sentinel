import { TrendingUp, TrendingDown, Activity, AlertOctagon, Clock, Cpu } from 'lucide-react';
import clsx from 'clsx';

// Ring gauge
function RingGauge({ value, max = 100, color }) {
    const r = 18;
    const circ = 2 * Math.PI * r;
    const pct = Math.min(value, max) / max;
    const dash = pct * circ;
    return (
        <svg width="44" height="44" viewBox="0 0 44 44">
            <circle cx="22" cy="22" r={r} fill="none" stroke="#1e293b" strokeWidth="4" />
            <circle
                cx="22" cy="22" r={r}
                fill="none"
                stroke={color}
                strokeWidth="4"
                strokeDasharray={`${dash} ${circ}`}
                strokeLinecap="round"
                transform="rotate(-90 22 22)"
                style={{ transition: 'stroke-dasharray 0.6s ease' }}
            />
            <text x="22" y="26" textAnchor="middle" fontSize="9" fill="white" fontWeight="600" fontFamily="'JetBrains Mono', monospace">
                {value.toFixed(0)}%
            </text>
        </svg>
    );
}

export default function SummaryCards({ latestCpu = 0, isDegraded = false, healthLabel = 'Operational', logCount = 0, criticalCount = 0 }) {
    const cards = [
        {
            id: 'status',
            label: 'Global Status',
            icon: Activity,
            iconColor: isDegraded ? 'text-warning' : 'text-success',
            bgColor: isDegraded ? 'bg-warning/10' : 'bg-success/10',
            value: healthLabel,
            valueClass: isDegraded ? 'text-warning text-xl font-bold' : 'text-success text-xl font-bold',
            sub: (
                <span className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span className={clsx('status-dot', isDegraded ? 'bg-warning animate-pulse' : 'bg-success animate-pulse-slow')} />
                    {isDegraded ? `CPU at ${latestCpu.toFixed(1)}%` : 'All systems nominal'}
                </span>
            ),
            extra: null,
        },
        {
            id: 'anomalies',
            label: 'Critical Logs',
            icon: AlertOctagon,
            iconColor: criticalCount > 0 ? 'text-critical' : 'text-slate-500',
            bgColor: criticalCount > 0 ? 'bg-critical/10' : 'bg-navy-800',
            value: criticalCount,
            valueClass: criticalCount > 0 ? 'text-critical text-3xl font-bold font-tech' : 'text-slate-400 text-3xl font-bold font-tech',
            sub: (
                <span className="text-xs text-slate-500 flex items-center gap-1">
                    {criticalCount > 0 ? <TrendingUp size={10} className="text-critical" /> : <TrendingDown size={10} className="text-success" />}
                    {criticalCount > 0 ? 'Attention required' : 'No critical logs'}
                </span>
            ),
            extra: null,
        },
        {
            id: 'logs',
            label: 'Total Logs Ingested',
            icon: Clock,
            iconColor: 'text-warning',
            bgColor: 'bg-warning/10',
            value: logCount,
            valueClass: 'text-warning text-3xl font-bold font-tech',
            sub: <span className="text-xs text-slate-500">From Elasticsearch</span>,
            extra: null,
        },
        {
            id: 'load',
            label: 'CPU Load',
            icon: Cpu,
            iconColor: latestCpu > 80 ? 'text-critical' : 'text-primary-400',
            bgColor: latestCpu > 80 ? 'bg-critical/10' : 'bg-primary-500/10',
            value: null,
            valueClass: '',
            sub: (
                <span className={clsx('text-xs font-tech font-bold', latestCpu > 80 ? 'text-critical' : 'text-primary-400')}>
                    {latestCpu.toFixed(1)}%
                </span>
            ),
            extra: <RingGauge value={latestCpu} color={latestCpu > 80 ? '#f43f5e' : '#3b82f6'} />,
        },
    ];

    return (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
            {cards.map(({ id, label, icon: Icon, iconColor, bgColor, value, valueClass, sub, extra }) => (
                <div key={id} className={clsx(
                    "card glass-panel flex flex-col gap-3 hover:border-navy-500 transition-all duration-300",
                    id === 'anomalies' && criticalCount > 0 && "glow-critical border-critical/40"
                )}>
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{label}</p>
                            {value !== null && <p className={clsx('mt-1', valueClass)}>{value}</p>}
                        </div>
                        <div className={clsx('w-9 h-9 rounded-lg flex items-center justify-center border border-white/5', bgColor)}>
                            <Icon size={16} className={iconColor} />
                        </div>
                    </div>
                    <div className="flex items-end justify-between">
                        <div className="font-tech uppercase">{sub}</div>
                        {extra && <div>{extra}</div>}
                    </div>
                </div>
            ))}
        </div>
    );
}
