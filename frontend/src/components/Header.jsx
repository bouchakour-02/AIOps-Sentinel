import { Search, Bell, ChevronDown } from 'lucide-react';
import { SUMMARY_STATS } from '../data/mock_data';

export default function Header() {
    const health = SUMMARY_STATS.globalHealth;
    const isHealthy = health >= 95;

    return (
        <header className="h-14 bg-navy-900/80 backdrop-blur-sm border-b border-navy-700 flex items-center px-6 gap-4 sticky top-0 z-20">
            {/* Global Health */}
            <div className="flex items-center gap-2 bg-navy-800 border border-navy-700 rounded-lg px-3 py-1.5">
                <span
                    className={`status-dot ${isHealthy ? 'bg-success animate-pulse-slow' : 'bg-critical animate-pulse'}`}
                />
                <span className="text-xs text-slate-400">Global Health</span>
                <span
                    className={`text-sm font-bold font-tech ${isHealthy ? 'text-success' : 'text-critical'}`}
                >
                    {health}%
                </span>
            </div>

            {/* Search */}
            <div className="flex-1 max-w-md relative">
                <Search
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                />
                <input
                    type="text"
                    placeholder="Search incidents, services, logs…"
                    className="w-full bg-navy-800 border border-navy-700 rounded-lg pl-9 pr-16 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-primary-500/60 focus:ring-1 focus:ring-primary-500/20 transition-all"
                />
                <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded border border-navy-600 bg-navy-800/80 text-[9px] text-slate-500 font-tech">
                    ⌘K
                </kbd>
            </div>

            <div className="flex-1" />

            {/* Environment Badge */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-warning/10 border border-warning/20">
                <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-warning opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-warning"></span>
                </span>
                <span className="text-[10px] font-bold text-warning uppercase tracking-tighter font-tech">
                    TUNIS-STAGING-CLUSTER
                </span>
            </div>

            {/* Notifications */}
            <button className="relative btn-ghost p-2 rounded-lg">
                <Bell size={16} className="text-slate-400" />
                <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 flex items-center justify-center rounded-full bg-critical text-[9px] font-bold text-white font-tech px-1 border-2 border-navy-900">
                    3
                </span>
            </button>

            {/* Profile */}
            <button className="flex items-center gap-2 bg-navy-800 border border-navy-700 rounded-lg px-3 py-1.5 hover:border-navy-600 transition-colors">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-primary-400 to-anomaly flex items-center justify-center text-xs font-bold text-white">
                    V
                </div>
                <span className="text-sm text-slate-300 font-medium hidden sm:inline">Vermeg Admin</span>
                <ChevronDown size={12} className="text-slate-500" />
            </button>
        </header>
    );
}
