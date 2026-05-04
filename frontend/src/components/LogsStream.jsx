import { useState, useEffect, useRef } from 'react';
import { AlertCircle, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';

const API_BASE = 'http://localhost:8000';

const SEVERITY_COLORS = {
    critical: { bg: 'bg-red-900/40', border: 'border-red-700', badge: 'bg-red-600', text: 'text-red-300' },
    error: { bg: 'bg-red-900/40', border: 'border-red-700', badge: 'bg-red-600', text: 'text-red-300' },
    warning: { bg: 'bg-amber-900/40', border: 'border-amber-700', badge: 'bg-amber-600', text: 'text-amber-300' },
    info: { bg: 'bg-blue-900/40', border: 'border-blue-700', badge: 'bg-blue-600', text: 'text-blue-300' },
};

export default function LogsStream() {
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const scrollRef = useRef(null);

    const fetchLogs = async () => {
        try {
            setIsRefreshing(true);
            const { data } = await axios.get(`${API_BASE}/api/logs`);
            if (data.logs && data.logs.length > 0) {
                const sortedLogs = [...data.logs].sort((a, b) => {
                    const timeA = new Date(a.timestamp).getTime();
                    const timeB = new Date(b.timestamp).getTime();
                    return timeB - timeA;
                });
                setLogs(sortedLogs);
            }
            setIsLoading(false);
        } catch (err) {
            console.error('[Logs] Fetch failed:', err.message);
            setIsLoading(false);
        } finally {
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 15000);
        return () => clearInterval(interval);
    }, []);

    const scroll = (direction) => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({
                left: direction === 'left' ? -600 : 600,
                behavior: 'smooth',
            });
        }
    };

    const formatTime = (iso) => {
        if (!iso) return 'N/A';
        return new Date(iso).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit', 
            hour12: false 
        });
    };

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center">
                    <div className="w-10 h-10 border-3 border-blue-500/40 border-t-blue-400 rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-sm text-slate-400">Loading logs from Elasticsearch…</p>
                </div>
            </div>
        );
    }

    if (logs.length === 0) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle size={40} className="text-slate-500 mx-auto mb-2 opacity-50" />
                    <p className="text-sm text-slate-400">No logs available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-navy-950 p-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-navy-700">
                <div>
                    <h3 className="text-base font-bold text-white">Log Stream</h3>
                    <p className="text-xs text-slate-400">{logs.length} logs from Elasticsearch</p>
                </div>
                <button
                    onClick={fetchLogs}
                    disabled={isRefreshing}
                    className={clsx(
                        'flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
                        isRefreshing 
                            ? 'bg-blue-600/30 text-blue-300 cursor-not-allowed'
                            : 'bg-blue-600/40 hover:bg-blue-600/60 text-blue-200 border border-blue-500/30'
                    )}
                >
                    <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
                    {isRefreshing ? 'Refreshing…' : 'Refresh'}
                </button>
            </div>

            {/* Horizontal Scroll Container */}
            <div className="flex-1 relative group">
                {/* Left Button */}
                <button
                    onClick={() => scroll('left')}
                    className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-1 bg-navy-800/90 hover:bg-navy-700 border border-navy-600 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-200"
                >
                    <ChevronLeft size={16} className="text-slate-300" />
                </button>

                {/* Scrollable Area */}
                <div
                    ref={scrollRef}
                    className="h-full overflow-x-auto overflow-y-hidden scroll-smooth hide-scrollbar flex gap-3 px-10"
                >
                    {logs.map((log, idx) => {
                        const config = SEVERITY_COLORS[log.severity] || SEVERITY_COLORS.info;
                        const truncateMsg = log.message?.substring(0, 200).replace(/\n/g, ' ') || 'Empty log';

                        return (
                            <div
                                key={`${log.timestamp}-${idx}`}
                                className={clsx(
                                    'shrink-0 w-80 p-3 rounded-lg border transition-all duration-200',
                                    'hover:shadow-lg hover:shadow-blue-500/20 hover:scale-105',
                                    'backdrop-blur-sm',
                                    config.bg,
                                    config.border
                                )}
                            >
                                {/* Service + Severity */}
                                <div className="flex items-center justify-between gap-2 mb-2">
                                    <span className="text-xs font-bold text-white truncate">
                                        {log.service || 'unknown'}
                                    </span>
                                    <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full text-white', config.badge)}>
                                        {log.severity?.toUpperCase() || 'INFO'}
                                    </span>
                                </div>

                                {/* Message */}
                                <p className="text-xs text-slate-200 mb-2 leading-relaxed line-clamp-3 font-mono">
                                    {truncateMsg}
                                </p>

                                {/* Footer */}
                                <div className="flex items-center justify-between pt-2 border-t border-white/10">
                                    <span className="text-[10px] text-slate-500">
                                        {formatTime(log.timestamp)}
                                    </span>
                                    <div className={clsx('w-2 h-2 rounded-full', config.badge)} />
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Right Button */}
                <button
                    onClick={() => scroll('right')}
                    className="absolute right-0 top-1/2 -translate-y-1/2 z-10 p-1 bg-navy-800/90 hover:bg-navy-700 border border-navy-600 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-200"
                >
                    <ChevronRight size={16} className="text-slate-300" />
                </button>
            </div>
        </div>
    );
}

