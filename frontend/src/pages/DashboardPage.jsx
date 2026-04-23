import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import SummaryCards from '../components/SummaryCards';
import MetricsChart from '../components/MetricsChart';
import IncidentTimeline from '../components/IncidentTimeline';
import AIAnalysisPanel from '../components/AIAnalysisPanel';
import { RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000';
const POLL_INTERVAL = 5000;
const MAX_CPU_HISTORY = 20;

function SectionLabel({ label }) {
    return (
        <div className="flex items-center gap-3">
            <span className="text-[9px] font-tech font-bold text-slate-500 uppercase tracking-[0.2em]">{label}</span>
            <span className="flex-1 h-px bg-navy-700/50" />
        </div>
    );
}

export default function DashboardPage() {
    const [selectedIncident, setSelectedIncident] = useState(null);
    const [refreshAge, setRefreshAge] = useState(0);
    const [isSyncing, setIsSyncing] = useState(false);

    // ── CPU History State ──
    const [cpuHistory, setCpuHistory] = useState([]);
    const [latestCpu, setLatestCpu] = useState(0);

    // ── Logs State ──
    const [logs, setLogs] = useState([]);

    // ── Fetch CPU metric ──
    const fetchCpu = useCallback(async () => {
        try {
            const { data } = await axios.get(`${API_BASE}/api/metrics/cpu`);
            const value = data.value ?? 0;
            const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            setLatestCpu(value);
            setCpuHistory(prev => {
                const next = [...prev, { time, cpu: value }];
                return next.length > MAX_CPU_HISTORY ? next.slice(-MAX_CPU_HISTORY) : next;
            });
        } catch (err) {
            console.error('[Sentinel] CPU fetch failed:', err.message);
        }
    }, []);

    // ── Fetch Logs ──
    const fetchLogs = useCallback(async () => {
        try {
            const { data } = await axios.get(`${API_BASE}/api/logs`);
            if (data.logs) setLogs(data.logs);
        } catch (err) {
            console.error('[Sentinel] Logs fetch failed:', err.message);
        }
    }, []);

    // ── Poll every 5s ──
    useEffect(() => {
        const poll = async () => {
            setIsSyncing(true);
            await Promise.all([fetchCpu(), fetchLogs()]);
            setIsSyncing(false);
            setRefreshAge(0);
        };
        poll(); // initial fetch
        const id = setInterval(poll, POLL_INTERVAL);
        return () => clearInterval(id);
    }, [fetchCpu, fetchLogs]);

    // ── Refresh age ticker ──
    useEffect(() => {
        const id = setInterval(() => setRefreshAge(a => a + 1), 1000);
        return () => clearInterval(id);
    }, []);

    // ── Derive health status from CPU ──
    const isDegraded = latestCpu > 80;
    const healthLabel = isDegraded ? 'Degraded' : 'Operational';
    const healthValue = isDegraded ? Math.max(0, 100 - latestCpu).toFixed(1) : (100 - latestCpu * 0.02).toFixed(1);

    return (
        <main className="flex-1 overflow-y-auto p-6 space-y-6 bg-navy-950">
            {/* Page title */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                        <span className="w-1 h-6 bg-primary-500 rounded-full" />
                        Unified Health Dashboard
                    </h1>
                    <p className="text-[10px] text-slate-500 mt-1 font-tech uppercase tracking-widest">
                        AI-POWERED OBSERVABILITY · MINISTRAL-3B · VERMEG SENTINEL v1.0
                    </p>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-tech">
                    <RefreshCw
                        size={10}
                        className={isSyncing ? 'animate-spin text-primary-400' : 'animate-spin-slow'}
                    />
                    <span>
                        {isSyncing ? (
                            <span className="text-primary-400 font-bold">Syncing…</span>
                        ) : (
                            `Live · ${refreshAge}s ago`
                        )}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    {/* KPI Cards */}
                    <SectionLabel label="Key Performance Indicators" />
                    <SummaryCards
                        latestCpu={latestCpu}
                        isDegraded={isDegraded}
                        healthLabel={healthLabel}
                        logCount={logs.length}
                        criticalCount={logs.filter(l => l.severity === 'critical' || l.severity === 'error').length}
                    />

                    {/* Metrics Chart */}
                    <SectionLabel label="Metrics Correlation" />
                    <MetricsChart cpuHistory={cpuHistory} latestCpu={latestCpu} />
                </div>

                <div className="space-y-6">
                    {/* Incident Timeline */}
                    <SectionLabel label="Incident Stream" />
                    <IncidentTimeline logs={logs} onSelect={setSelectedIncident} />
                </div>
            </div>

            {/* AI Analysis Panel */}
            <AIAnalysisPanel
                incident={selectedIncident}
                onClose={() => setSelectedIncident(null)}
            />
        </main>
    );
}
