import React from 'react';
import { LayoutDashboard, Cuboid, Settings, Layers } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';

const SidebarItem = ({ icon: Icon, label, to, active }) => (
  <Link
    to={to}
    className={clsx(
      "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
      active
        ? "bg-primary/10 text-primary shadow-[0_0_15px_-5px_rgba(59,130,246,0.5)]"
        : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
    )}
  >
    <Icon size={20} className={active ? 'text-primary' : 'group-hover:text-white transition-colors'} />
    <span className="font-medium">{label}</span>
  </Link>
);

export default function MainLayout({ children }) {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-bg-darker text-text-primary font-sans">
      {/* Sidebar */}
      <aside className="w-[280px] flex flex-col p-4 gap-6 glass-panel border-r-0 m-4 rounded-3xl">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Cuboid className="text-white" size={20} />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            NeuroVis
          </span>
        </div>

        <nav className="flex-1 space-y-2">
          <SidebarItem
            icon={Cuboid}
            label="Visualizador 3D"
            to="/"
            active={location.pathname === '/'}
          />
          <SidebarItem
            icon={LayoutDashboard}
            label="Dashboard"
            to="/dashboard"
            active={location.pathname === '/dashboard'}
          />
          <SidebarItem
            icon={Layers}
            label="Segmentaciones"
            to="/layers"
            active={location.pathname === '/layers'}
          />
        </nav>

        <div className="mt-auto pt-4 border-t border-white/10">
          <SidebarItem
            icon={Settings}
            label="Configuración"
            to="/settings"
            active={location.pathname === '/settings'}
          />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 pl-0 h-screen overflow-hidden">
        <div className="h-full w-full rounded-3xl overflow-hidden glass-panel relative">
          {children}
        </div>
      </main>
    </div>
  );
}
