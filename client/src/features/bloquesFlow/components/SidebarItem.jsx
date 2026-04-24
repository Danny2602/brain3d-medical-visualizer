import React, { useState } from 'react';
import { ChevronDown, ChevronUp, GripVertical, Info } from 'lucide-react';

export default function SidebarItem({ item, color, onDragStart }) {
    const [isOpen, setIsOpen] = useState(false);

    // Mapeo de colores de Tailwind para los bordes/fondos
    const colorMap = {
        emerald: 'border-emerald-500/30 hover:border-emerald-500 bg-emerald-500/5',
        amber: 'border-amber-500/30 hover:border-amber-500 bg-amber-500/5',
        rose: 'border-rose-500/30 hover:border-rose-500 bg-rose-500/5',
        indigo: 'border-indigo-500/30 hover:border-indigo-500 bg-indigo-500/5',
        purple: 'border-purple-500/30 hover:border-purple-500 bg-purple-500/5',
    };

    return (
        <div
            draggable
            onDragStart={(e) => onDragStart(e, item)}
            className={`group border rounded-xl mb-3 transition-all cursor-grab active:cursor-grabbing overflow-hidden ${colorMap[color] || 'border-slate-700 bg-slate-800/50'}`}
        >
            <div className="p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <GripVertical size={14} className="text-slate-600 group-hover:text-slate-400" />
                    <span className="text-xs font-bold uppercase tracking-tight text-slate-200">{item.label}</span>
                </div>
                <button
                    onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
                    className="text-slate-500 hover:text-white transition-colors"
                >
                    {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
            </div>

            {isOpen && (
                <div className="px-3 pb-3 text-[10px] text-slate-400 leading-relaxed border-t border-white/5 pt-2 flex gap-2">
                    <Info size={12} className="shrink-0 mt-0.5 text-blue-400" />
                    <p>{item.desc}</p>
                </div>
            )}
        </div>
    );
}
