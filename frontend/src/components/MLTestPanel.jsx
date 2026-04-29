import { useState } from 'react';
import { X, BrainCircuit, Send, Loader } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';

const API_BASE = 'http://localhost:8000';

export default function MLTestPanel({ isOpen, onClose }) {
    const [activeTab, setActiveTab] = useState('log'); // log | metric | system
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);

    // Log test state
    const [logMessage, setLogMessage] = useState('');

    // Metric test state
    const [cpu, setCpu] = useState(50);
    const [memory, setMemory] = useState(50);
    const [dbErrors, setDbErrors] = useState(5);

    // System test state
    const [systemLog, setSystemLog] = useState('');
    const [systemCpu, setSystemCpu] = useState(50);
    const [systemMemory, setSystemMemory] = useState(50);
    const [systemDbErrors, setSystemDbErrors] = useState(5);

    const testLogAnomaly = async () => {
        setLoading(true);
        try {
            const { data } = await axios.post(`${API_BASE}/api/predict/log-anomaly`, {
                message: logMessage
            });
            setResults({ type: 'log', data });
        } catch (err) {
            setResults({ type: 'log', error: err.message });
        }
        setLoading(false);
    };

    const testMetricAnomaly = async () => {
        setLoading(true);
        try {
            const { data } = await axios.post(`${API_BASE}/api/predict/metric-anomaly`, {
                cpu,
                memory,
                db_errors: dbErrors
            });
            setResults({ type: 'metric', data });
        } catch (err) {
            setResults({ type: 'metric', error: err.message });
        }
        setLoading(false);
    };

    const testSystemAnalysis = async () => {
        setLoading(true);
        try {
            const { data } = await axios.post(`${API_BASE}/api/predict/system-analysis`, {
                log_message: systemLog,
                cpu: systemCpu,
                memory: systemMemory,
                db_errors: systemDbErrors
            });
            setResults({ type: 'system', data });
        } catch (err) {
            setResults({ type: 'system', error: err.message });
        }
        setLoading(false);
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 animate-fade-in"
                onClick={onClose}
            />

            {/* Panel */}
            <div className="fixed left-0 top-0 h-full w-full max-w-2xl bg-navy-900 border-r border-navy-700 z-40 flex flex-col animate-slide-in shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-5 border-b border-navy-700 shrink-0">
                    <div className="flex items-center gap-3">
                        <BrainCircuit size={18} className="text-anomaly" />
                        <h2 className="text-lg font-bold text-slate-100">ML Model Testing</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="btn-ghost p-1.5 rounded-lg text-slate-400 hover:text-white"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-navy-700 px-6 shrink-0">
                    {['log', 'metric', 'system'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => {
                                setActiveTab(tab);
                                setResults(null);
                            }}
                            className={clsx(
                                'px-4 py-3 text-xs font-medium uppercase tracking-wider border-b-2 transition-all',
                                activeTab === tab
                                    ? 'border-primary-500 text-primary-400'
                                    : 'border-transparent text-slate-500 hover:text-slate-300'
                            )}
                        >
                            {tab === 'log' && 'Log Anomaly'}
                            {tab === 'metric' && 'Metric Anomaly'}
                            {tab === 'system' && 'System Analysis'}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Log Anomaly Test */}
                    {activeTab === 'log' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">Log Message</label>
                                <textarea
                                    value={logMessage}
                                    onChange={e => setLogMessage(e.target.value)}
                                    placeholder="Enter a log message to test..."
                                    rows={4}
                                    className="w-full bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-primary-500"
                                />
                                <div className="flex gap-2 mt-2 flex-wrap text-[11px]">
                                    <button
                                        onClick={() => setLogMessage('INFO service running normally')}
                                        className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                    >
                                        Normal
                                    </button>
                                    <button
                                        onClick={() => setLogMessage('ERROR CRITICAL database connection timeout failed')}
                                        className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                    >
                                        Error
                                    </button>
                                </div>
                            </div>

                            <button
                                onClick={testLogAnomaly}
                                disabled={!logMessage || loading}
                                className={clsx(
                                    'w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-all',
                                    !logMessage || loading
                                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                        : 'btn-primary'
                                )}
                            >
                                {loading && <Loader size={14} className="animate-spin" />}
                                Test Log Anomaly
                            </button>

                            {results?.type === 'log' && (
                                <ResultBox data={results.data} error={results.error} />
                            )}
                        </div>
                    )}

                    {/* Metric Anomaly Test */}
                    {activeTab === 'metric' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    CPU: {cpu}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={cpu}
                                    onChange={e => setCpu(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    Memory: {memory}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={memory}
                                    onChange={e => setMemory(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    DB Errors: {dbErrors}
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="500"
                                    value={dbErrors}
                                    onChange={e => setDbErrors(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div className="flex gap-2 flex-wrap text-[11px]">
                                <button
                                    onClick={() => {
                                        setCpu(25);
                                        setMemory(30);
                                        setDbErrors(0);
                                    }}
                                    className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                >
                                    Normal
                                </button>
                                <button
                                    onClick={() => {
                                        setCpu(98);
                                        setMemory(95);
                                        setDbErrors(200);
                                    }}
                                    className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                >
                                    High Stress
                                </button>
                            </div>

                            <button
                                onClick={testMetricAnomaly}
                                disabled={loading}
                                className={clsx(
                                    'w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-all',
                                    loading ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'btn-primary'
                                )}
                            >
                                {loading && <Loader size={14} className="animate-spin" />}
                                Test Metric Anomaly
                            </button>

                            {results?.type === 'metric' && (
                                <ResultBox data={results.data} error={results.error} />
                            )}
                        </div>
                    )}

                    {/* System Analysis Test */}
                    {activeTab === 'system' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">Log Message</label>
                                <textarea
                                    value={systemLog}
                                    onChange={e => setSystemLog(e.target.value)}
                                    placeholder="Enter a log message..."
                                    rows={3}
                                    className="w-full bg-navy-800 border border-navy-700 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-primary-500"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    CPU: {systemCpu}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={systemCpu}
                                    onChange={e => setSystemCpu(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    Memory: {systemMemory}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={systemMemory}
                                    onChange={e => setSystemMemory(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-300 mb-2">
                                    DB Errors: {systemDbErrors}
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="500"
                                    value={systemDbErrors}
                                    onChange={e => setSystemDbErrors(Number(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div className="flex gap-2 flex-wrap text-[11px]">
                                <button
                                    onClick={() => {
                                        setSystemLog('INFO healthy');
                                        setSystemCpu(30);
                                        setSystemMemory(40);
                                        setSystemDbErrors(1);
                                    }}
                                    className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                >
                                    Healthy
                                </button>
                                <button
                                    onClick={() => {
                                        setSystemLog('ERROR critical failure');
                                        setSystemCpu(96);
                                        setSystemMemory(94);
                                        setSystemDbErrors(120);
                                    }}
                                    className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-slate-400"
                                >
                                    Critical
                                </button>
                            </div>

                            <button
                                onClick={testSystemAnalysis}
                                disabled={!systemLog || loading}
                                className={clsx(
                                    'w-full py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-all',
                                    !systemLog || loading
                                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                        : 'btn-primary'
                                )}
                            >
                                {loading && <Loader size={14} className="animate-spin" />}
                                Test System Analysis
                            </button>

                            {results?.type === 'system' && (
                                <ResultBox data={results.data} error={results.error} />
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

function ResultBox({ data, error }) {
    if (error) {
        return (
            <div className="bg-critical/10 border border-critical/30 rounded-lg p-4">
                <p className="text-sm text-critical">{error}</p>
            </div>
        );
    }

    return (
        <div className="bg-navy-800 border border-navy-700 rounded-lg p-4 space-y-3">
            {data.anomaly !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Anomaly Detected:</span>
                    <span className={clsx(
                        'text-sm font-bold font-tech',
                        data.anomaly ? 'text-critical' : 'text-success'
                    )}>
                        {data.anomaly ? 'YES' : 'NO'}
                    </span>
                </div>
            )}

            {data.similarity_score !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Similarity Score:</span>
                    <span className="text-sm font-bold font-tech text-primary-400">
                        {data.similarity_score.toFixed(4)}
                    </span>
                </div>
            )}

            {data.threshold !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Threshold:</span>
                    <span className="text-sm font-bold font-tech text-slate-300">
                        {data.threshold.toFixed(4)}
                    </span>
                </div>
            )}

            {data.isolation_forest_score !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">IF Score:</span>
                    <span className="text-sm font-bold font-tech text-slate-300">
                        {data.isolation_forest_score.toFixed(4)}
                    </span>
                </div>
            )}

            {data.risk_level !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Risk Level:</span>
                    <span className={clsx(
                        'text-sm font-bold font-tech',
                        data.risk_level === 'CRITICAL' ? 'text-critical' : 'text-warning'
                    )}>
                        {data.risk_level}
                    </span>
                </div>
            )}

            {data.anomaly_count !== undefined && (
                <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Anomalies:</span>
                    <span className="text-sm font-bold font-tech text-slate-300">
                        {data.anomaly_count}
                    </span>
                </div>
            )}

            <pre className="text-[10px] text-slate-400 bg-navy-950 rounded p-2 overflow-auto max-h-32">
                {JSON.stringify(data, null, 2)}
            </pre>
        </div>
    );
}
