import React, { useState } from 'react';
import { Info, GripVertical, Image as ImageIcon, Maximize2, X } from 'lucide-react';
import clsx from 'clsx';

export default function BlockItem({
  item,
  resultImage,
  isDraggable = true,
  onDragStart,
  isPipelineBlock = false,
  isGenerated = false,
  generatedColorClass = "border-cyan-500/50 bg-cyan-500/10 shadow-[0_0_15px_-3px_rgba(6,182,212,0.3)]",
  // Props para connect_comp (selector de capa de textura)
  pipeline = [],
  blockIndex = 0,
  onParamsChange = null,
}) {
  const [showInfo, setShowInfo] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Mostrar acordeón si: estamos en catálogo, ya fue generado, o es connect_comp (necesita configuración antes de generar)
  const isConnectComp = isPipelineBlock && item.name_api === 'connect_comp' && onParamsChange;
  const canShowInfo = !isPipelineBlock || (isPipelineBlock && isGenerated) || isConnectComp;

  return (
    <>
      <div
        draggable={isDraggable}
        onDragStart={(e) => isDraggable && onDragStart && onDragStart(e, item)}
        onMouseEnter={() => canShowInfo && setShowInfo(true)}
        onMouseLeave={() => canShowInfo && setShowInfo(false)}
        className={clsx(
          "flex flex-col p-3 rounded-xl border glass-panel shadow-sm relative transition-all duration-300",
          isDraggable ? "cursor-grab active:cursor-grabbing hover:bg-white/5" : "cursor-default",
          isGenerated && isPipelineBlock ? generatedColorClass : "border-white/10",
          showInfo && canShowInfo ? "z-[10]" : "z-0"
        )}
      >
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-3">
            {isDraggable && <GripVertical size={16} className="text-text-secondary" />}
            <span className={clsx(
              "font-medium text-sm transition-colors",
              isGenerated && isPipelineBlock ? "text-cyan-300" : "text-text-primary"
            )}>
              {item.name}
            </span>
          </div>

          {canShowInfo && (
            <div className="flex items-center justify-center p-1.5 rounded-full hover:bg-white/10 transition-colors cursor-help">
              {isPipelineBlock && isGenerated ? (
                <ImageIcon size={16} className="text-cyan-400" />
              ) : (
                <Info size={16} className="text-blue-400" />
              )}
            </div>
          )}
        </div>

        {/* Tarjeta de Información Expandible en Línea (Acordeón) */}
            <div
            className={clsx(
              "w-full transition-all duration-300 overflow-hidden",
              showInfo ? "max-h-[400px] mt-3 opacity-100" : "max-h-0 mt-0 opacity-0"
            )}
          >
            <div className="p-3 bg-bg-darker/60 backdrop-blur-sm rounded-lg border border-white/5 text-xs text-text-secondary">
              {isPipelineBlock && isGenerated ? (
                <div className="flex flex-col gap-2">
                  <div className="text-xs font-semibold text-cyan-300 uppercase tracking-wider">Resultado del Paso</div>
                  <div className="rounded-lg overflow-hidden border border-white/10 relative h-28 bg-black/50 group/image">
                    <img
                      src={resultImage || "https://images.unsplash.com/photo-1559757175-5700dde675bc?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"}
                      alt="Procesamiento"
                      className="w-full h-full object-cover opacity-90 mx-auto"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/image:opacity-100 transition-opacity flex items-center justify-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsModalOpen(true);
                        }}
                        className="p-2 bg-white/10 hover:bg-white/20 rounded-full text-white backdrop-blur-md transition-all hover:scale-110"
                        title="Agrandar imagen de paso"
                      >
                        <Maximize2 size={16} />
                      </button>
                    </div>
                  </div>
                  <p className="text-xs mt-1 text-center">Filtro aplicado exitosamente.</p>
                </div>
              ) : isPipelineBlock && item.name_api === 'connect_comp' && onParamsChange ? (
                // Selector especial para el filtro final: ¿Sobre qué imagen pintar el tumor?
                <div className="flex flex-col gap-3">
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-semibold uppercase tracking-widest text-cyan-400">
                      🎨 Capa de Textura (¿Sobre qué imagen pintar?)
                    </label>
                    <select
                      className={clsx(
                        "text-xs rounded-lg px-2 py-1.5 border bg-bg-darker/80 backdrop-blur-sm outline-none cursor-pointer transition-all",
                        item.params?.original_layer_name
                          ? "border-cyan-500/40 text-cyan-200"
                          : "border-red-500/40 text-red-400"
                      )}
                      value={item.params?.original_layer_name || ""}
                      onChange={(e) => onParamsChange(item.uniqueId, { original_layer_name: e.target.value })}
                    >
                      <option value="">-- Elige la base visual --</option>
                      <option value="original">📷 Original (imagen cruda)</option>
                      {pipeline
                        .slice(0, blockIndex)
                        .filter((b) => b.type !== 'operador')
                        .map((s) => (
                          <option key={s.uniqueId} value={s.name_api}>{s.name}</option>
                        ))}
                    </select>
                    {!item.params?.original_layer_name && (
                      <span className="text-[10px] text-red-400/80">⚠ Recomendado: Filtro Laplaciano (super_detail)</span>
                    )}
                  </div>
                  <p className="text-xs leading-relaxed opacity-75">{item.info}</p>
                </div>
              ) : (
                <div className="flex flex-col gap-1 text-sm">
                  <strong className="text-text-primary mb-1">{item.name}</strong>
                  <span className="text-xs leading-relaxed opacity-90">{item.info}</span>
                </div>
              )}
            </div>
          </div>
      </div>

      {/* Modal Expandido del Paso */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-300">
          <div className="relative w-full max-w-5xl bg-bg-darker border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full max-h-[85vh] animate-in zoom-in-95 duration-300">
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <ImageIcon size={20} className="text-cyan-400" />
                Vista Expandida - {item.name}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-text-secondary hover:text-red-400 p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                title="Cerrar vista"
              >
                <X size={24} />
              </button>
            </div>

            <div className="flex-1 overflow-hidden p-6 bg-black/40 flex items-center justify-center dashboard-pattern">
              <img
                src={resultImage || "https://images.unsplash.com/photo-1559757175-5700dde675bc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"}
                alt={`Procesamiento de ${item.name}`}
                className="max-w-full max-h-full object-contain rounded-xl shadow-2xl border border-white/10"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
