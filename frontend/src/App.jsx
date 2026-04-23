import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import ChatBot from './components/ChatBot';

export default function App() {
  const [activeNav, setActiveNav] = useState('dashboard');

  return (
    <div className="flex h-screen overflow-hidden bg-navy-950">
      <Sidebar active={activeNav} onNav={setActiveNav} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <DashboardPage />
      </div>
      <ChatBot />
    </div>
  );
}
