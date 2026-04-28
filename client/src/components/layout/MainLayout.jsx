import React, { useState } from 'react';

import { LayoutDashboard, Cuboid, Settings, Layers, ChevronLeft, ChevronRight, TrendingUpDown, BetweenHorizontalStart } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';

const SidebarItem = ({ icon: Icon, label, to, active, collapsed }) => (
  <Link
    to={to}
    className={clsx(
      "flex items-center rounded-xl transition-all duration-200 group relative",
      collapsed ? "justify-center p-3" : "gap-3 px-4 py-3",
      active
        ? "bg-primary/10 text-primary shadow-[0_0_15px_-5px_rgba(59,130,246,0.5)]"
        : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
    )}
    title={collapsed ? label : undefined}
  >
    <Icon size={20} className={active ? 'text-primary min-w-[20px]' : 'group-hover:text-white transition-colors min-w-[20px]'} />
    {!collapsed && <span className="font-medium whitespace-nowrap overflow-hidden transition-all duration-300">{label}</span>}
  </Link>
);

export default function MainLayout({ children }) {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-bg-darker text-text-primary font-sans">
      {/* Sidebar */}
      <aside className={clsx(
        "flex flex-col p-4 gap-6 glass-panel border-r-0 m-4 rounded-3xl transition-all duration-300 relative",
        collapsed ? "w-[88px]" : "w-[280px]"
      )}>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-4 top-8 bg-bg-darker border border-white/10 rounded-full p-1.5 text-text-secondary hover:text-white transition-colors z-10 shadow-lg hover:bg-white/10"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>

        <div className={clsx("flex items-center transition-all duration-300", collapsed ? "justify-center px-0 py-2" : "gap-3 px-2 py-2")}>
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 min-w-[32px]">
            <Cuboid className="text-white" size={20} />
          </div>
          {!collapsed && (
            <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent whitespace-nowrap overflow-hidden">
              NeuroVis
            </span>
          )}
        </div>

        <nav className="flex-1 space-y-2">
          <SidebarItem
            icon={Cuboid}
            label="Inicio"
            to="/"
            active={location.pathname === '/'}
            collapsed={collapsed}
          />
          <SidebarItem
            icon={LayoutDashboard}
            label="Segmentacion"
            to="/segmentacion"
            active={location.pathname === '/segmentacion'}
            collapsed={collapsed}
          />
          <SidebarItem
            icon={BetweenHorizontalStart}
            label="Bloques"
            to="/bloques"
            active={location.pathname === '/bloques'}
            collapsed={collapsed}
          />
          <SidebarItem
            icon={TrendingUpDown}
            label="BloquesFlow"
            to="/bloquesflow"
            active={location.pathname === '/bloquesflow'}
            collapsed={collapsed}
          />

        </nav>

        <div className="mt-auto pt-4 border-t border-white/10">
          <SidebarItem
            icon={Settings}
            label="Configuración"
            to="/settings"
            active={location.pathname === '/settings'}
            collapsed={collapsed}
          />
        </div>
      </aside>


      <main className="flex-1 p-4 pl-0 h-screen overflow-hidden">
        <div className="h-full w-full rounded-3xl overflow-y-auto glass-panel relative">
          {children}
        </div>
      </main>
    </div>
  );
}
