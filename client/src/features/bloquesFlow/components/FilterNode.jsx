import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Loader2, ZoomIn } from 'lucide-react';

export default function FilterNode({ data }) {
    return (
        <div className={`bg-slate-900 border-2 rounded-xl overflow-hidden shadow-2xl min-w-[180px] transition-all ${data.resultUrl ? 'border-indigo-500' : 'border-slate-700'}`}>

            {/* Entrada por ARRIBA */}
            <Handle type="target" position={Position.Top} className="w-3 h-3 bg-slate-600 border-2 border-slate-900 !-top-1.5" />

            <div className="p-2 bg-slate-800 text-[10px] font-black uppercase tracking-tighter text-slate-300 border-b border-slate-700 flex justify-between items-center">
                {data.label}
                {data.processing && <Loader2 size={10} className="animate-spin text-blue-400" />}
            </div>

            <div className="p-3 bg-slate-900/50 flex items-center justify-center min-h-[80px]">
                {data.resultUrl ? (
                    <div
                        className="relative group cursor-pointer"
                        onClick={() => data.onExpand(data.resultUrl)} // Abre el modal al hacer click
                    >
                        <img
                            src={data.resultUrl}
                            alt={data.label}
                            className="w-full h-auto max-h-32 object-contain rounded-lg border border-slate-700 hover:scale-105 transition-transform"
                        />
                        <div className="absolute inset-0 bg-indigo-500/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                            <ZoomIn size={24} className="text-white drop-shadow-lg" />
                        </div>
                    </div>
                ) : (
                    <div className="text-[9px] text-slate-600 italic">Esperando datos...</div>
                )}
            </div>

            {/* Salida por ABAJO */}
            <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-indigo-500 border-2 border-slate-900 !-bottom-1.5" />
        </div>
    );
}
