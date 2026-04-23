import React, { useState } from 'react';
import { Trash2, Maximize2, X, Image as ImageIcon } from 'lucide-react';
import clsx from 'clsx';

/**
 * Bloque visual para operadores lógicos (AND / OR).
 * Muestra: cápsula de nombre, dropdowns de Capa A y Capa B,
 * advertencia de configuración pendiente y miniatura del resultado generado.
 */
export default function OperatorBlock({
    block,
    index,
    pipeline,
    isGenerated,
    resultImage,
    onRemove,
    onParamsChange,
}) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Solo listar filtros (no operadores) que están antes de este bloque
    const stepsAntes = pipeline
        .slice(0, index)
        .filter((b) => b.type !== 'operador');

    const layerAOk = !!block.params?.layer_a;
    const layerBOk = !!block.params?.layer_b;
    const isConfigured = layerAOk && layerBOk;

    return (
        <>
            <div className="flex flex-col items-start my-2 relative z-10 w-full pl-12 gap-2">

                {/* Fila superior: Cápsula + botón borrar */}
                <div className="flex items-center gap-3">
                    <div className={clsx(
                        "px-4 py-1.5 rounded-full font-bold text-xs uppercase tracking-widest shadow-lg backdrop-blur-md border transition-all duration-300",
                        isGenerated
                            ? "bg-green-500/20 text-green-300 border-green-500/40 shadow-[0_0_15px_-3px_rgba(34,197,94,0.3)]"
                            : isConfigured
                                ? "bg-purple-500/30 text-purple-300 border-purple-400/50"
                                : "bg-red-500/20 text-red-400 border-red-500/30"
                    )}>
                        {block.name}
                    </div>

                    <button
                        onClick={() => onRemove(block.uniqueId)}
                        className="p-1.5 text-text-secondary hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                        title="Eliminar operador"
                    >
                        <Trash2 size={14} />
                    </button>
                </div>

                {/* Dropdowns de Capa A y Capa B */}
                <div className="flex flex-wrap gap-3 items-end">
                    {/* Capa A */}
                    <div className="flex flex-col gap-1">
                        <label className="text-[10px] font-semibold uppercase tracking-widest text-purple-400">
                            Capa A
                        </label>
                        <select
                            className={clsx(
                                "text-xs rounded-lg px-2 py-1.5 border bg-bg-darker/80 backdrop-blur-sm outline-none cursor-pointer transition-all",
                                layerAOk ? "border-purple-500/40 text-purple-200" : "border-red-500/40 text-red-400"
                            )}
                            value={block.params?.layer_a || ""}
                            onChange={(e) => onParamsChange(block.uniqueId, { layer_a: e.target.value })}
                        >
                            <option value="">-- Elige un paso --</option>
                            {stepsAntes.map((s) => (
                                <option key={s.uniqueId} value={s.name_api}>{s.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* Capa B */}
                    <div className="flex flex-col gap-1">
                        <label className="text-[10px] font-semibold uppercase tracking-widest text-purple-400">
                            Capa B
                        </label>
                        <select
                            className={clsx(
                                "text-xs rounded-lg px-2 py-1.5 border bg-bg-darker/80 backdrop-blur-sm outline-none cursor-pointer transition-all",
                                layerBOk ? "border-purple-500/40 text-purple-200" : "border-red-500/40 text-red-400"
                            )}
                            value={block.params?.layer_b || ""}
                            onChange={(e) => onParamsChange(block.uniqueId, { layer_b: e.target.value })}
                        >
                            <option value="">-- Elige un paso --</option>
                            {stepsAntes.map((s) => (
                                <option key={s.uniqueId} value={s.name_api}>{s.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* Advertencia si faltan selecciones */}
                    {!isConfigured && (
                        <span className="text-[10px] text-red-400/80 mb-1.5">
                            ⚠ Selecciona las dos capas para generar
                        </span>
                    )}
                </div>

                {/* Miniatura del Resultado (igual que los filtros normales) */}
                {isGenerated && resultImage && (
                    <div className="w-full mt-1">
                        <div className="text-[10px] font-semibold uppercase tracking-widest text-green-400 mb-1">
                            Resultado del Paso
                        </div>
                        <div className="rounded-lg overflow-hidden border border-white/10 relative h-28 bg-black/50 group/image w-48">
                            <img
                                src={resultImage}
                                alt={`Resultado ${block.name}`}
                                className="w-full h-full object-cover opacity-90"
                            />
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/image:opacity-100 transition-opacity flex items-center justify-center">
                                <button
                                    onClick={() => setIsModalOpen(true)}
                                    className="p-2 bg-white/10 hover:bg-white/20 rounded-full text-white backdrop-blur-md transition-all hover:scale-110"
                                    title="Agrandar imagen de paso"
                                >
                                    <Maximize2 size={16} />
                                </button>
                            </div>
                        </div>
                        <p className="text-[10px] text-text-secondary mt-1">Fusión aplicada exitosamente.</p>
                    </div>
                )}
            </div>

            {/* Modal expandido del resultado */}
            {isModalOpen && (
                <div className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-300">
                    <div className="relative w-full max-w-5xl bg-bg-darker border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full max-h-[85vh] animate-in zoom-in-95 duration-300">
                        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
                            <h3 className="text-lg font-medium text-white flex items-center gap-2">
                                <ImageIcon size={20} className="text-green-400" />
                                Vista Expandida — {block.name}
                            </h3>
                            <button
                                onClick={() => setIsModalOpen(false)}
                                className="text-text-secondary hover:text-red-400 p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                            >
                                <X size={24} />
                            </button>
                        </div>
                        <div className="flex-1 overflow-hidden p-6 bg-black/40 flex items-center justify-center dashboard-pattern">
                            <img
                                src={resultImage}
                                alt={`Vista expandida ${block.name}`}
                                className="max-w-full max-h-full object-contain rounded-xl shadow-2xl border border-white/10"
                            />
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
