import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import LogsStream from './components/LogsStream';
import ChatBot from './components/ChatBot';
import { X } from 'lucide-react';

export default function App() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [showLogsModal, setShowLogsModal] = useState(false);

  const handleNav = (id) => {
    if (id === 'logs') {
      setShowLogsModal(true);
    } else {
      setActiveNav(id);
      setShowLogsModal(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-navy-950">
      <Sidebar active={activeNav} onNav={handleNav} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        {!showLogsModal && <DashboardPage />}
      </div>
      <ChatBot />

      {/* Logs Modal */}
      {showLogsModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-40">
          <div className="w-[95vw] h-[95vh] bg-navy-900 border border-navy-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-navy-700 bg-navy-800">
              <div>
                <h2 className="text-lg font-bold text-white">All Logs Stream</h2>
                <p className="text-[10px] text-slate-500 mt-1 font-tech uppercase tracking-widest">
                  Real-time logs from Elasticsearch
                </p>
              </div>
              <button
                onClick={() => {
                  setShowLogsModal(false);
                  setActiveNav('dashboard');
                }}
                className="p-2 hover:bg-navy-700 rounded-lg transition-colors text-slate-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
              <LogsStream />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
