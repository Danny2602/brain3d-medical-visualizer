import React from 'react';
import { Handle, Position, useReactFlow } from '@xyflow/react';
import { Loader2, ZoomIn, Layers, Image as ImageIcon } from 'lucide-react';


export default function FilterNode({ id, data }) {
    const isClipping = data.filterName === 'mask_clipping';
    const isLogic = data.filterName.startsWith('logic_');
    const isOperator = isClipping || isLogic;

    const { updateNodeData } = useReactFlow();

    const handleInputChange = (paramName, newValue) => {
        updateNodeData(id, {
            params: {
                ...data.params,
                [paramName]: newValue
            }
        });
    }

    return (
        /* Eliminamos overflow-hidden para que los conectores funcionen perfecto */
        <div className={`bg-slate-900 border-2 rounded-xl shadow-2xl min-w-[200px] transition-all relative ${data.resultUrl ? 'border-indigo-500' : 'border-slate-700'}`}>

            {/* ENTRADAS (HANDLES) */}
            {isOperator ? (
                <>
                    {/* Etiquetas dinámicas sobre los conectores */}
                    <div className="absolute -top-6 left-0 right-0 flex justify-around text-[7px] font-black uppercase tracking-widest text-slate-500 pointer-events-none">
                        <span>{isClipping ? 'Textura' : 'Entrada A'}</span>
                        <span>{isClipping ? 'Máscara' : 'Entrada B'}</span>
                    </div>
                    <Handle
                        type="target"
                        position={Position.Top}
                        id="a"
                        style={{ left: '30%', width: '12px', height: '12px' }}
                        className="bg-blue-500 border-2 border-slate-900 !-top-2 z-50 hover:scale-125 transition-transform"
                    />
                    <Handle
                        type="target"
                        position={Position.Top}
                        id="b"
                        style={{ left: '70%', width: '12px', height: '12px' }}
                        className="bg-purple-500 border-2 border-slate-900 !-top-2 z-50 hover:scale-125 transition-transform"
                    />
                </>
            ) : (
                <Handle
                    type="target"
                    position={Position.Top}
                    style={{ width: '12px', height: '12px' }}
                    className="bg-slate-600 border-2 border-slate-900 !-top-2 z-50 hover:scale-125 transition-transform"
                />
            )}

            {/* CABECERA */}
            <div className="p-2 bg-slate-800 rounded-t-lg text-[10px] font-black uppercase tracking-tighter text-slate-300 border-b border-slate-700 flex justify-between items-center">
                <span className="truncate max-w-[140px] flex items-center gap-2">
                    <div className="w-1 h-1 rounded-full bg-indigo-500 shadow-[0_0_5px_rgba(99,102,241,1)]" />
                    {data.label}
                </span>
                {data.processing && <Loader2 size={10} className="animate-spin text-blue-400" />}
            </div>
            {/* PARAMS */}
            {data.params && Object.keys(data.params).length > 0 && (
                <div className="p-3 bg-slate-800/80 border-b border-slate-700 flex flex-col gap-2">
                    {Object.entries(data.params).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center text-[10px]">
                            <label className="text-slate-400 font-bold uppercase">{key}</label>

                            {key === 'mode' ? (
                                <select
                                    value={value}
                                    onChange={(e) => handleInputChange(key, e.target.value)}
                                    className="w-24 bg-slate-900 text-white rounded px-1 py-1 border border-slate-700 focus:border-blue-500 focus:outline-none text-[10px]"
                                >
                                    {/* Cambia estos valores por los 3 modos reales que tienes en tu backend */}
                                    <option value="triangular">Triangular</option>
                                    <option value="campana">Campana</option>
                                    <option value="sigmoide">Sigmoide</option>
                                </select>
                            ) : (
                                <input
                                    type="text"
                                    value={value}
                                    onChange={(e) => handleInputChange(key, e.target.value)}
                                    className="w-16 bg-slate-900 text-white rounded px-2 py-1 border border-slate-700 focus:border-blue-500 focus:outline-none"
                                />
                            )}

                        </div>
                    ))}

                </div>
            )}


            {/* VISTA PREVIA */}
            <div className="p-3 flex items-center justify-center min-h-[100px] bg-gradient-to-b from-slate-900 to-slate-950">
                {data.resultUrl ? (
                    <div className="relative group cursor-pointer" onClick={() => data.onExpand(data.resultUrl)}>
                        <img
                            src={data.resultUrl}
                            alt={data.label}
                            className="w-full h-auto max-h-32 object-contain rounded-lg border border-slate-800 shadow-inner group-hover:border-indigo-500/30 transition-all"
                        />
                        <div className="absolute inset-0 bg-indigo-600/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg backdrop-blur-[1px]">
                            <ZoomIn size={20} className="text-white drop-shadow-lg" />
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-2 opacity-10 py-4">
                        <ImageIcon size={28} strokeWidth={1} />
                        <div className="text-[7px] uppercase font-black tracking-widest">Awaiting Data</div>
                    </div>
                )}
            </div>

            {/* SALIDA */}
            <Handle
                type="source"
                position={Position.Bottom}
                style={{ width: '12px', height: '12px' }}
                className="bg-indigo-500 border-2 border-slate-900 !-bottom-2 z-50 hover:scale-125 transition-transform shadow-[0_0_10px_rgba(99,102,241,0.5)]"
            />
        </div>
    );
}
