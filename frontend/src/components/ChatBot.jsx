import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, BrainCircuit, Minimize2 } from 'lucide-react';
import { CHAT_SEED } from '../data/mock_data';
import clsx from 'clsx';

const AI_RESPONSES = [
    "Based on the current metrics, I can see elevated CPU usage across the Payment-API cluster. The anomaly score of 0.88 indicates high confidence in this being a genuine incident.",
    "The correlation between the CPU spike and the OutOfMemoryError suggests the JVM heap is under pressure. I recommend applying the kubectl patch shown in the analysis panel.",
    "Comparing this incident to historical patterns, similar events occurred on 2025-11-14 and 2025-12-03 — both resolved by increasing heap size and enabling G1GC.",
    "The Auth-Service latency degradation (INC-002) may be a downstream effect of the Payment-API incident. Redis connection pool exhaustion often cascades from upstream timeouts.",
    "I'm monitoring all 5 services. Currently, API-Gateway and Notification-Svc are within normal bounds. Order-Service shows residual error rate elevation.",
];

let aiIdx = 0;

export default function ChatBot() {
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState(CHAT_SEED);
    const [input, setInput] = useState('');
    const [typing, setTyping] = useState(false);
    const [unread, setUnread] = useState(0);
    const bottomRef = useRef(null);
    const prevCountRef = useRef(messages.length);

    useEffect(() => {
        if (open) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
            setUnread(0);
        }
    }, [messages, open]);

    // Track unread messages when chat is closed
    useEffect(() => {
        if (!open && messages.length > prevCountRef.current) {
            const newOnes = messages.slice(prevCountRef.current).filter(m => m.role === 'assistant');
            if (newOnes.length > 0) setUnread(u => u + newOnes.length);
        }
        prevCountRef.current = messages.length;
    }, [messages, open]);

    function sendMessage() {
        const text = input.trim();
        if (!text) return;
        const userMsg = { id: Date.now(), role: 'user', text, ts: new Date().toISOString() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setTyping(true);
        setTimeout(() => {
            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                text: AI_RESPONSES[aiIdx % AI_RESPONSES.length],
                ts: new Date().toISOString(),
            };
            aiIdx++;
            setMessages(prev => [...prev, aiMsg]);
            setTyping(false);
        }, 1200 + Math.random() * 800);
    }

    function formatTime(iso) {
        return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    }

    return (
        <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
            {/* Chat window */}
            {open && (
                <div className="w-80 bg-navy-900 border border-navy-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in">
                    {/* Header */}
                    <div className="flex items-center gap-3 px-4 py-3 bg-navy-800 border-b border-navy-700">
                        <div className="w-7 h-7 rounded-full bg-anomaly/20 border border-anomaly/30 flex items-center justify-center">
                            <BrainCircuit size={13} className="text-anomaly" />
                        </div>
                        <div className="flex-1">
                            <p className="text-xs font-semibold text-slate-200">AIOps Assistant</p>
                            <p className="text-[10px] text-success flex items-center gap-1">
                                <span className="status-dot bg-success animate-pulse-slow" /> Online · Ministral-3B
                            </p>
                        </div>
                        <button onClick={() => setOpen(false)} className="btn-ghost p-1 rounded-lg text-slate-500 hover:text-white">
                            <Minimize2 size={13} />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 max-h-72">
                        {messages.map(msg => (
                            <div
                                key={msg.id}
                                className={clsx('flex flex-col gap-0.5', msg.role === 'user' ? 'items-end' : 'items-start')}
                            >
                                <div
                                    className={clsx(
                                        'max-w-[85%] px-3 py-2 rounded-xl text-xs leading-relaxed',
                                        msg.role === 'user'
                                            ? 'bg-primary-500 text-white rounded-br-sm'
                                            : 'bg-navy-800 border border-navy-700 text-slate-300 rounded-bl-sm'
                                    )}
                                >
                                    {msg.text}
                                </div>
                                <span className="text-[9px] text-slate-600 font-tech">{formatTime(msg.ts)}</span>
                            </div>
                        ))}

                        {/* Typing indicator */}
                        {typing && (
                            <div className="flex items-start">
                                <div className="bg-navy-800 border border-navy-700 rounded-xl rounded-bl-sm px-3 py-2.5 flex items-center gap-1">
                                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
                                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
                                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-slate-400" />
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    {/* Input */}
                    <div className="px-3 py-3 border-t border-navy-700 flex items-center gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && sendMessage()}
                            placeholder="Ask about incidents…"
                            className="flex-1 bg-navy-800 border border-navy-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 placeholder-slate-600 focus:outline-none focus:border-primary-500/60 focus:ring-1 focus:ring-primary-500/20 transition-all"
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!input.trim()}
                            className="w-8 h-8 rounded-lg bg-primary-500 hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                        >
                            <Send size={13} className="text-white" />
                        </button>
                    </div>
                </div>
            )}

            {/* FAB */}
            <button
                onClick={() => setOpen(o => !o)}
                className={clsx(
                    'relative w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-200',
                    open
                        ? 'bg-navy-700 hover:bg-navy-600 rotate-0'
                        : 'bg-primary-500 hover:bg-primary-600 shadow-primary-500/30'
                )}
            >
                {open ? <X size={18} className="text-white" /> : <MessageSquare size={18} className="text-white" />}
                {!open && unread > 0 && (
                    <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-critical text-[9px] font-bold text-white font-tech px-1 border-2 border-navy-950 animate-bounce">
                        {unread}
                    </span>
                )}
            </button>
        </div>
    );
}
