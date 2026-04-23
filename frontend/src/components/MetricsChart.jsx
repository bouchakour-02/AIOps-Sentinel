import {
    ComposedChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
    Label,
} from 'recharts';

const CPU_SPIKE_THRESHOLD = 85;

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-navy-800 border border-navy-600 rounded-lg p-3 shadow-xl text-xs">
            <p className="text-slate-400 mb-2 font-medium font-tech">{label}</p>
            {payload.map(p => (
                <div key={p.dataKey} className="flex items-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
                    <span className="text-slate-300">{p.name}:</span>
                    <span className="font-semibold text-white font-tech">
                        {p.value?.toFixed(1)}%
                    </span>
                </div>
            ))}
        </div>
    );
};

export default function MetricsChart({ cpuHistory = [], latestCpu = 0 }) {
    // Find first spike point for AI annotation
    const spikePoint = cpuHistory.find(pt => pt.cpu > CPU_SPIKE_THRESHOLD);
    const hasSpike = latestCpu > CPU_SPIKE_THRESHOLD;

    return (
        <div className="card glass-panel shadow-lg shadow-navy-950/50 hover:shadow-primary-500/5 transition-all duration-500">
            <div className="flex items-center justify-between mb-5">
                <div>
                    <h2 className="text-sm font-semibold text-slate-100 italic tracking-tight uppercase">Real-Time CPU Telemetry</h2>
                    <p className="text-[10px] text-slate-500 mt-0.5 font-tech uppercase tracking-widest">
                        LIVE FROM PROMETHEUS · {cpuHistory.length}/{20} POINTS · POLL 5s
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="badge bg-success/10 text-success border border-success/20 animate-pulse text-[10px]">● Telemetry Active</span>
                    {hasSpike && (
                        <span className="badge bg-critical/10 text-critical border border-critical/30 animate-pulse text-[10px] font-tech font-bold">
                            ⚠ SPIKE {latestCpu.toFixed(1)}%
                        </span>
                    )}
                </div>
            </div>

            {cpuHistory.length === 0 ? (
                <div className="flex items-center justify-center h-[240px] text-slate-500 text-xs font-tech">
                    <div className="flex flex-col items-center gap-2">
                        <div className="w-5 h-5 border-2 border-primary-500/40 border-t-primary-400 rounded-full animate-spin" />
                        Waiting for CPU data…
                    </div>
                </div>
            ) : (
                <ResponsiveContainer width="100%" height={240}>
                    <ComposedChart data={cpuHistory} margin={{ top: 20, right: 16, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} opacity={0.5} />
                        <XAxis
                            dataKey="time"
                            tick={{ fill: '#475569', fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                            axisLine={false}
                            tickLine={false}
                            interval="preserveStartEnd"
                        />
                        <YAxis
                            domain={[0, 100]}
                            tick={{ fill: '#475569', fontSize: 10 }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={v => `${v}%`}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            wrapperStyle={{ fontSize: '10px', paddingTop: '12px' }}
                            formatter={v => <span className="text-slate-500 uppercase font-tech tracking-tighter">{v}</span>}
                        />

                        {/* CPU Area */}
                        <defs>
                            <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
                            </linearGradient>
                        </defs>
                        <Line
                            type="monotone"
                            dataKey="cpu"
                            name="CPU %"
                            stroke="#3b82f6"
                            strokeWidth={2.5}
                            dot={false}
                            activeDot={{ r: 5, fill: '#3b82f6', stroke: '#1e293b', strokeWidth: 2 }}
                            isAnimationActive={true}
                            animationDuration={500}
                        />

                        {/* Danger threshold line */}
                        <ReferenceLine
                            y={CPU_SPIKE_THRESHOLD}
                            stroke="#f43f5e"
                            strokeDasharray="6 3"
                            strokeWidth={1}
                            strokeOpacity={0.5}
                        >
                            <Label
                                value={`THRESHOLD ${CPU_SPIKE_THRESHOLD}%`}
                                position="insideTopRight"
                                fill="#f43f5e"
                                fontSize={9}
                                fontWeight="700"
                                className="font-tech"
                            />
                        </ReferenceLine>

                        {/* AI Spike Detection Annotation */}
                        {spikePoint && (
                            <ReferenceLine
                                x={spikePoint.time}
                                stroke="#f43f5e"
                                strokeDasharray="4 4"
                                strokeWidth={2}
                            >
                                <Label
                                    value="AI DETECTED SPIKE"
                                    position="top"
                                    fill="#f43f5e"
                                    fontSize={10}
                                    fontWeight="900"
                                    offset={15}
                                    className="font-tech italic"
                                />
                            </ReferenceLine>
                        )}
                    </ComposedChart>
                </ResponsiveContainer>
            )}
        </div>
    );
}
