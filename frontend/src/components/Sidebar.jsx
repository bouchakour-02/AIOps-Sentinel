import {
    LayoutDashboard,
    AlertTriangle,
    Server,
    BrainCircuit,
    ScrollText,
    Activity,
    ChevronRight,
    ExternalLink,
    BookOpen,
} from 'lucide-react';
import clsx from 'clsx';

const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
    { id: 'services', label: 'Services', icon: Server },
    { id: 'ai-settings', label: 'AI Settings', icon: BrainCircuit },
    { id: 'logs', label: 'Logs', icon: ScrollText },
];

export default function Sidebar({ active, onNav }) {
    return (
        <aside className="w-60 shrink-0 bg-navy-900 border-r border-navy-700 flex flex-col h-screen sticky top-0 z-30">
            {/* Logo */}
            <div className="flex items-center gap-3 px-5 py-5 border-b border-navy-700">
                <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
                    <Activity size={16} className="text-white" />
                </div>
                <div>
                    <p className="text-sm font-bold text-white leading-none">Vermeg</p>
                    <p className="text-[10px] text-primary-400 font-medium leading-none mt-1 uppercase tracking-wider">
                        Sentinel v1.0
                    </p>
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest px-2 mb-3">
                    Navigation
                </p>
                {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
                    const isActive = active === id;
                    return (
                        <button
                            key={id}
                            onClick={() => onNav(id)}
                            className={clsx(
                                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group',
                                isActive
                                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20 shadow-[0_0_15px_-5px_var(--color-primary-500)]'
                                    : 'text-slate-400 hover:text-slate-100 hover:bg-navy-800'
                            )}
                        >
                            <Icon
                                size={16}
                                className={clsx(
                                    'shrink-0 transition-colors',
                                    isActive ? 'text-primary-400' : 'text-slate-500 group-hover:text-slate-300'
                                )}
                            />
                            <span className="flex-1 text-left">{label}</span>
                            {isActive && <ChevronRight size={12} className="text-primary-400/60" />}
                        </button>
                    );
                })}

                <div className="pt-6 px-2">
                    <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-3">
                        External
                    </p>
                    <a
                        href="#"
                        className="flex items-center gap-3 px-2 py-2 text-xs text-slate-400 hover:text-primary-400 transition-colors group"
                    >
                        <BookOpen size={14} />
                        <span>Vermeg Internal Docs</span>
                        <ExternalLink size={10} className="ml-auto opacity-0 group-hover:opacity-100" />
                    </a>
                </div>
            </nav>

            {/* Footer Profile */}
            <div className="px-4 py-4 border-t border-navy-700">
                <div className="flex items-center gap-2 p-2 rounded-lg bg-navy-800/50 border border-navy-700/50">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-400 to-anomaly flex items-center justify-center text-xs font-bold text-white">
                        V
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-200 truncate">Vermeg Admin</p>
                        <p className="text-[10px] text-slate-500 truncate">ops@vermeg.com</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}

