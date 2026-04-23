
import { Server, Database, Globe, Activity } from 'lucide-react';
import clsx from 'clsx';

const SERVICES = [
    { id: 'gateway', name: 'Gateway', x: 50, y: 120, icon: Globe, status: 'healthy' },
    { id: 'auth', name: 'Auth-Svc', x: 180, y: 60, icon: Server, status: 'healthy' },
    { id: 'payment', name: 'Payment-API', x: 180, y: 180, icon: Server, status: 'critical' },
    { id: 'order', name: 'Order-Svc', x: 310, y: 120, icon: Server, status: 'warning' },
    { id: 'notification', name: 'Notif-Svc', x: 310, y: 220, icon: Server, status: 'healthy' },
    { id: 'db', name: 'Main-DB', x: 440, y: 120, icon: Database, status: 'healthy' },
];

const CONNECTIONS = [
    { from: 'gateway', to: 'auth' },
    { from: 'gateway', to: 'payment' },
    { from: 'auth', to: 'db' },
    { from: 'payment', to: 'order' },
    { from: 'payment', to: 'notification' },
    { from: 'order', to: 'db' },
];

export default function ServiceMap() {
    return (
        <div className="card glass-panel bg-grid relative overflow-hidden min-h-[340px]">
            <div className="flex items-center justify-between mb-6 relative z-10">
                <div>
                    <h2 className="text-sm font-semibold text-slate-100 italic tracking-tight">System Topology / Blast Radius</h2>
                    <p className="text-[10px] text-slate-500 font-tech">Live dependency mapping — Vermeg Sentinel</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="badge bg-critical/10 text-critical border border-critical/30 animate-pulse text-[10px]">
                        Incident in Progress
                    </span>
                </div>
            </div>

            <svg className="w-full h-[240px] relative z-0" viewBox="0 0 500 280" preserveAspectRatio="xMidYMid meet">
                {/* Connection Lines */}
                {CONNECTIONS.map((conn, i) => {
                    const from = SERVICES.find((s) => s.id === conn.from);
                    const to = SERVICES.find((s) => s.id === conn.to);
                    const isCriticalPath = from.status === 'critical' || to.status === 'critical';

                    return (
                        <g key={i}>
                            <path
                                d={`M ${from.x} ${from.y} L ${to.x} ${to.y}`}
                                stroke={isCriticalPath ? 'var(--color-critical)' : 'var(--color-navy-700)'}
                                strokeWidth={isCriticalPath ? '2' : '1'}
                                fill="none"
                                strokeDasharray={isCriticalPath ? "4 4" : "0"}
                                className={clsx(isCriticalPath && "animate-[dash_2s_linear_infinite]")}
                            />
                            {isCriticalPath && (
                                <circle r="3" fill="var(--color-critical)">
                                    <animateMotion
                                        dur="2s"
                                        repeatCount="indefinite"
                                        path={`M ${from.x} ${from.y} L ${to.x} ${to.y}`}
                                    />
                                </circle>
                            )}
                        </g>
                    );
                })}

                {/* Nodes */}
                {SERVICES.map((svc) => {
                    const Icon = svc.icon;
                    const isCritical = svc.status === 'critical';
                    const isWarning = svc.status === 'warning';

                    return (
                        <g key={svc.id}>
                            {/* Outer Glow for Critical */}
                            {isCritical && (
                                <circle
                                    cx={svc.x}
                                    cy={svc.y}
                                    r="24"
                                    className="fill-critical/20 animate-pulse"
                                />
                            )}

                            {/* Node Circle */}
                            <circle
                                cx={svc.x}
                                cy={svc.y}
                                r="18"
                                className={clsx(
                                    "stroke-2 transition-colors duration-300",
                                    isCritical ? "fill-navy-900 stroke-critical shadow-lg" :
                                        isWarning ? "fill-navy-900 stroke-warning" :
                                            "fill-navy-900 stroke-navy-700"
                                )}
                                style={isCritical ? { filter: 'drop-shadow(0 0 8px var(--color-critical))' } : {}}
                            />

                            {/* Icon */}
                            <foreignObject x={svc.x - 8} y={svc.y - 8} width="16" height="16">
                                <Icon size={16} className={clsx(
                                    isCritical ? "text-critical" :
                                        isWarning ? "text-warning" :
                                            "text-slate-400"
                                )} />
                            </foreignObject>

                            {/* Label */}
                            <text
                                x={svc.x}
                                y={svc.y + 32}
                                textAnchor="middle"
                                className={clsx(
                                    "text-[9px] font-tech font-bold uppercase tracking-tight fill-slate-300",
                                    isCritical && "fill-critical"
                                )}
                            >
                                {svc.name}
                            </text>
                        </g>
                    );
                })}
            </svg>

            {/* CSS for dashed animation and motion */}
            <style>{`
        @keyframes dash {
          to {
            stroke-dashoffset: -20;
          }
        }
      `}</style>
        </div>
    );
}
