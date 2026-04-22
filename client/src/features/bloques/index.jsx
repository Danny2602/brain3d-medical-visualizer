import React, { useState, useRef } from 'react';
import { Play, Trash2, Layers, Cpu, CheckCircle, Maximize2, X, ChevronUp, ChevronDown, Upload, ImagePlus } from 'lucide-react';
import BlockItem from './components/BlockItem';
import clsx from 'clsx';

const AVAILABLE_BLOCKS = [
  { id: 'otsu', name: 'Otsu Thresholding', info: 'Binariza la imagen usando el método de Otsu para separar el fondo.', type: 'filtro' },
  { id: 'canny', name: 'Canny Edge Detection', info: 'Detecta los bordes en la imagen utilizando el algoritmo Canny.', type: 'filtro' },
  { id: 'gaussian', name: 'Filtro Gaussiano', info: 'Aplica un desenfoque gaussiano para reducir el ruido en la imagen.', type: 'filtro' },
  { id: 'erosion', name: 'Erosión', info: 'Erosiona los bordes del objeto principal en la imagen binaria.', type: 'filtro' },
  { id: 'dilation', name: 'Dilatación', info: 'Expande los bordes del objeto en la imagen binaria.', type: 'filtro' },
  { id: 'cca', name: 'Componentes Conectados (CCA)', info: 'Encuentra y clasifica todos los componentes conectados en la imagen binaria.', type: 'filtro' },
  { id: 'fourier', name: 'Transformada de Fourier', info: 'Aplica un filtro enfatizador de altas frecuencias en el dominio de frecuencia.', type: 'filtro' }
];

const OPERATOR_BLOCKS = [
  { id: 'and', name: 'AND', info: 'Intersección: Mantiene solo lo que coincide en procesos adyacentes.', type: 'operador' },
  { id: 'or', name: 'OR', info: 'Unión: Combina y mantiene ambos procesos.', type: 'operador' }
];

export default function Bloques() {
  const [pipeline, setPipeline] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [activeTab, setActiveTab] = useState('filtros');
  const [isGenerated, setIsGenerated] = useState(false);
  const [isImageMaximized, setIsImageMaximized] = useState(false);
  const [isBaseImageMaximized, setIsBaseImageMaximized] = useState(false);
  
  // Novedades: Imagen base
  const [baseImage, setBaseImage] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setBaseImage(file);
      setShowWarning(false);
      setIsGenerated(false); // Reset earlier generation if image changes
    }
  };

  // Funciones de Drag and Drop
  const handleDragStart = (e, item) => {
    e.dataTransfer.setData('blockId', item.id);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);

    if (!baseImage) {
      setShowWarning(true);
      setTimeout(() => setShowWarning(false), 2500); // advertencia dura 2.5s
      return;
    }
    
    const blockId = e.dataTransfer.getData('blockId');
    const block = [...AVAILABLE_BLOCKS, ...OPERATOR_BLOCKS].find((b) => b.id === blockId);
    
    if (block) {
      const newBlock = { ...block, uniqueId: `${block.id}-${Date.now()}` };
      setPipeline((prev) => [...prev, newBlock]);
      setIsGenerated(false); // Resetear estado cuando se añade un nuevo bloque
    }
  };

  const removeBlock = (uniqueId) => {
    setPipeline((prev) => prev.filter((b) => b.uniqueId !== uniqueId));
    setIsGenerated(false);
  };

  const moveBlockUp = (index) => {
    if (index === 0) return;
    const newPipeline = [...pipeline];
    [newPipeline[index - 1], newPipeline[index]] = [newPipeline[index], newPipeline[index - 1]];
    setPipeline(newPipeline);
    setIsGenerated(false);
  };

  const moveBlockDown = (index) => {
    if (index === pipeline.length - 1) return;
    const newPipeline = [...pipeline];
    [newPipeline[index + 1], newPipeline[index]] = [newPipeline[index], newPipeline[index + 1]];
    setPipeline(newPipeline);
    setIsGenerated(false);
  };

  const handleGenerate = () => {
    if (pipeline.length > 0) {
      setIsGenerated(true);
    }
  };

  const currentList = activeTab === 'filtros' ? AVAILABLE_BLOCKS : OPERATOR_BLOCKS;

  return (
    <div className="absolute inset-0 flex flex-col gap-6 w-full text-text-primary p-2">
      <div className="flex justify-between items-center px-4 pt-2">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Constructor de Secuencia
          </h1>
          <p className="text-text-secondary mt-1">Arma tu secuencia de procesamiento de imágenes arrastrando bloques desde el origen al plano.</p>
        </div>
        
        <button 
          className={clsx(
            "flex items-center gap-2 px-6 py-2.5 text-white rounded-xl font-medium shadow-lg transition-all duration-200 active:scale-95",
            isGenerated 
              ? "bg-green-500/20 text-green-400 border border-green-500/50 hover:bg-green-500/30 shadow-green-500/10 cursor-default"
              : "bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 shadow-blue-500/25"
          )}
          onClick={handleGenerate}
        >
          {isGenerated ? <CheckCircle size={18} /> : <Play size={18} className="fill-white/80" />}
          <span>{isGenerated ? "Generado" : "Generar Secuencia"}</span>
        </button>
      </div>

      <div className="flex-1 flex gap-6 min-h-0 mx-2 pb-2">
        {/* Panel izquierdo: Catálogo con Tabs */}
        <div className="w-[300px] flex flex-col glass-panel rounded-3xl p-5 border border-white/10 shrink-0">
          <div className="flex bg-bg-darker/50 rounded-xl p-1 mb-5 border border-white/5">
            <button
              onClick={() => setActiveTab('filtros')}
              className={clsx(
                "flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                activeTab === 'filtros' ? "bg-white/10 text-white shadow-sm" : "text-text-secondary hover:text-white hover:bg-white/5"
              )}
            >
              <Layers size={16} /> Filtros
            </button>
            <button
              onClick={() => setActiveTab('operadores')}
              className={clsx(
                "flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                activeTab === 'operadores' ? "bg-white/10 text-white shadow-sm" : "text-text-secondary hover:text-white hover:bg-white/5"
              )}
            >
              <Cpu size={16} /> Operadores
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
            {currentList.map((block) => (
              <div key={block.id} className="relative hover:z-[100] transition-all">
                <BlockItem 
                  item={block} 
                  onDragStart={handleDragStart} 
                />
              </div>
            ))}
          </div>
        </div>

        {/* Panel derecho: Contenedor de la secuencia (Dropzone) */}
        <div className="flex-1 flex flex-col glass-panel rounded-3xl p-5 border border-white/10 relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 px-1 gap-3">
            <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
              Plano de Trabajo
              {pipeline.length > 0 && (
                <span className="text-xs bg-primary/20 text-blue-400 px-2 py-0.5 rounded-full border border-primary/30">
                  {pipeline.length}
                </span>
              )}
            </h2>

            {pipeline.length > 0 && (
              <button 
                onClick={() => { setPipeline([]); setIsGenerated(false); }}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-400 bg-red-500/10 hover:bg-red-500/20 rounded-lg border border-red-500/20 transition-all active:scale-95 shrink-0"
              >
                <Trash2 size={14} /> Limpiar Todas las Capas
              </button>
            )}
          </div>
          
          <div 
            className={clsx(
              "flex-1 rounded-2xl border-2 border-dashed transition-all duration-200 p-6 overflow-y-auto custom-scrollbar relative",
              isDragOver && baseImage
                ? "border-blue-500 bg-blue-500/10 shadow-[inset_0_0_50px_rgba(59,130,246,0.1)]" 
                : isDragOver && !baseImage
                  ? "border-red-500 bg-red-500/5 shadow-[inset_0_0_50px_rgba(239,68,68,0.1)] cursor-not-allowed"
                  : "border-white/10 bg-white/5"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col gap-2 max-w-3xl mx-auto pb-10">
              
              {/* Bloque Inicial Fijo: Imagen de Entrada */}
              <div className="flex flex-col font-sans">
                <div className="flex items-center gap-4 relative">
                  {/* Step Indicator 0 */}
                  <div className={clsx(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border shrink-0 shadow-lg relative z-10 z-[1] transition-colors duration-300",
                    isGenerated 
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-[0_0_10px_-2px_rgba(6,182,212,0.3)]"
                      : "bg-blue-500/20 text-blue-300 border-blue-500/40 shadow-[0_0_10px_-2px_rgba(59,130,246,0.2)]"
                  )}>
                    0
                  </div>

                  {/* Block Wrapper */}
                  <div className={clsx(
                    "flex-1 bg-bg-darker/50 rounded-xl relative z-10 glass-panel p-3.5 flex items-center justify-between shadow-sm transition-all duration-300 border",
                    showWarning ? "border-red-500/80 shadow-[0_0_20px_-5px_rgba(239,68,68,0.6)]" : "border-blue-500/20"
                  )}>
                    <div className="flex items-center gap-3">
                      {baseImage ? (
                        <div 
                          className="w-10 h-10 rounded-lg overflow-hidden border border-white/10 shrink-0 relative group/baseimg cursor-pointer shadow-md"
                          onClick={() => setIsBaseImageMaximized(true)}
                          title="Agrandar imagen original"
                        >
                          <img src={URL.createObjectURL(baseImage)} alt="Input preview" className="w-full h-full object-cover" />
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover/baseimg:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                            <Maximize2 size={16} className="text-white" />
                          </div>
                        </div>
                      ) : (
                        <ImagePlus size={20} className={clsx("transition-colors", showWarning ? "text-red-400" : isGenerated ? "text-cyan-400" : "text-blue-400")} />
                      )}
                      
                      <div className="flex flex-col">
                        <span className={clsx("font-medium text-sm transition-colors", showWarning ? "text-red-300" : isGenerated ? "text-cyan-300" : "text-blue-300")}>
                          {baseImage ? "Imagen Cargada Exitosamente" : "Imagen Base de Entrada"}
                        </span>
                        {baseImage && (
                          <span className="text-xs text-text-secondary truncate max-w-[150px] sm:max-w-[300px]">
                            {baseImage.name}
                          </span>
                        )}
                        {!baseImage && showWarning && (
                          <span className="text-xs text-red-400 mt-0.5 animate-pulse font-medium">¡Requiere imagen primero!</span>
                        )}
                      </div>
                    </div>
                    
                    <input 
                      type="file" 
                      ref={fileInputRef} 
                      className="hidden" 
                      accept="image/*" 
                      onChange={handleFileChange} 
                    />
                    <button 
                      onClick={() => fileInputRef.current.click()}
                      className={clsx(
                        "flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border transition-colors shrink-0",
                        showWarning 
                          ? "bg-red-500/10 hover:bg-red-500/20 text-red-400 border-red-500/20" 
                          : "bg-blue-500/10 hover:bg-blue-500/20 active:bg-blue-500/30 text-blue-400 border-blue-500/20"
                      )}
                    >
                      <Upload size={14} /> {baseImage ? "Cambiar Imagen" : "Cargar Imagen"}
                    </button>
                  </div>
                  
                  {/* Espacio vacío para alinear con los botones de borrar/mover */}
                  <div className="w-[72px] shrink-0 opacity-0 pointer-events-none"></div>
                </div>

                {/* Connecting line */}
                <div className="h-6 flex items-center w-8 justify-center shrink-0">
                  <div className={clsx(
                    "w-0.5 h-full relative -top-1 transition-all duration-300",
                    isGenerated ? "bg-cyan-500/40 shadow-[0_0_8px_rgba(6,182,212,0.5)]" : "bg-white/10"
                  )}></div>
                </div>
              </div>

              {/* El Pipeline / Secuencia */}
              {pipeline.map((block, index) => {
                const isOperator = block.type === 'operador';
                
                return (
                  <div key={block.uniqueId} className="flex flex-col group relative hover:z-[100] animate-in fade-in slide-in-from-bottom-4 duration-300">
                    {isOperator ? (
                      <div className="flex items-center justify-center my-1 relative z-10 w-full ml-10">
                        <div className={clsx(
                          "px-4 py-1.5 rounded-full font-bold text-xs uppercase tracking-widest shadow-lg backdrop-blur-md border flex items-center justify-center w-20 text-center transition-all duration-300",
                          isGenerated 
                            ? "bg-green-500/20 text-green-300 border-green-500/40 shadow-[0_0_15px_-3px_rgba(34,197,94,0.3)]" 
                            : "bg-purple-500/20 text-purple-400 border-purple-500/30"
                        )}>
                          {block.name}
                        </div>
                        
                        {/* Wrapper for Delete Actions */}
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all mr-14">
                          <button 
                            onClick={() => removeBlock(block.uniqueId)}
                            className="p-1.5 text-text-secondary hover:text-red-400 hover:bg-red-400/10 rounded-lg shrink-0 transition-colors"
                            title="Eliminar operador"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-4 relative">
                        {/* Step Indicator */}
                        <div className={clsx(
                          "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border shrink-0 shadow-lg relative z-10 z-[1] transition-all duration-300",
                          isGenerated 
                            ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-[0_0_10px_-2px_rgba(6,182,212,0.3)]"
                            : "bg-bg-darker text-text-primary border-white/20 group-hover:border-primary/50 group-hover:text-primary"
                        )}>
                          {index + 1}
                        </div>

                        {/* Block Item */}
                        <div className="flex-1 bg-bg-darker/50 rounded-xl relative z-10">
                          <BlockItem 
                            item={block} 
                            isDraggable={false} 
                            isPipelineBlock={true}
                            isGenerated={isGenerated}
                          />
                        </div>
                        
                        {/* Control Actions (Move Up/Down & Delete) */}
                        <div className="flex items-center gap-1 shrink-0">
                          <div className="flex flex-col opacity-0 group-hover:opacity-100 transition-opacity justify-center">
                            <button 
                              onClick={() => moveBlockUp(index)} 
                              disabled={index === 0}
                              className="p-1 text-text-secondary hover:text-white disabled:opacity-30 disabled:hover:text-text-secondary transition-colors"
                              title="Subir"
                            >
                              <ChevronUp size={16} />
                            </button>
                            <button 
                              onClick={() => moveBlockDown(index)} 
                              disabled={index === pipeline.length - 1}
                              className="p-1 text-text-secondary hover:text-white disabled:opacity-30 disabled:hover:text-text-secondary transition-colors"
                              title="Bajar"
                            >
                              <ChevronDown size={16} />
                            </button>
                          </div>
                          
                          <button 
                            onClick={() => removeBlock(block.uniqueId)}
                            className="p-2 text-text-secondary hover:text-red-400 hover:bg-red-400/10 rounded-xl opacity-0 group-hover:opacity-100 transition-all"
                            title="Eliminar bloque"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Connecting line */}
                    {index < pipeline.length - 1 && (
                      <div className="h-6 flex items-center w-8 justify-center shrink-0">
                         <div className={clsx(
                           "w-0.5 h-full relative -top-1 transition-all duration-300",
                           isGenerated ? "bg-cyan-500/40 shadow-[0_0_8px_rgba(6,182,212,0.5)]" : "bg-white/10 group-hover:bg-primary/30"
                         )}></div>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Empty state hint */}
              {pipeline.length === 0 && (
                !baseImage ? (
                  <div className={clsx(
                    "flex items-center justify-center p-8 mt-2 flex-col border-2 border-dashed rounded-2xl transition-colors duration-300",
                    showWarning ? "border-red-500/50 bg-red-500/5" : "border-white/5 bg-white/[0.02] animate-in fade-in duration-500"
                  )}>
                    <div className={clsx(
                      "w-14 h-14 rounded-full flex items-center justify-center border shadow-inner mb-3 transition-colors",
                      showWarning ? "border-red-500/30 bg-red-400/20 text-red-400" : "border-white/10 bg-bg-darker/40 text-white/20"
                    )}>
                      <ImagePlus size={20} />
                    </div>
                    <p className={clsx(
                      "font-medium mb-1 transition-colors",
                      showWarning ? "text-red-400" : "text-text-primary"
                    )}>
                      Requiere Imagen de Entrada
                    </p>
                    <p className={clsx(
                      "text-sm text-center",
                      showWarning ? "text-red-400/70" : "text-text-secondary"
                    )}>
                      Usa el bloque superior para subir la imagen de base médica y comenzar.
                    </p>
                  </div>
                ) : (
                  <div className="flex items-center justify-center p-8 mt-2 flex-col text-text-secondary border-2 border-dashed border-cyan-500/20 rounded-2xl bg-cyan-500/5 animate-in fade-in duration-500">
                    <div className="w-14 h-14 rounded-full flex items-center justify-center border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.1)] bg-bg-darker/80 mb-3">
                      <Layers size={20} className="text-cyan-400" />
                    </div>
                    <p className="font-medium text-cyan-300 mb-1">Imagen Lista</p>
                    <p className="text-sm text-cyan-400/70 text-center">Arrastra bloques para añadirlos a la secuencia de procesamiento.</p>
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Panel derecho adicional: Vista Previa Final (aparece al Generar) */}
        {isGenerated && (
          <div className="w-[380px] flex flex-col glass-panel rounded-3xl p-5 border border-white/10 shrink-0 animate-in slide-in-from-right-8 duration-500 fade-in">
            <h2 className="text-lg font-semibold mb-4 text-text-primary flex items-center gap-2">
              Resultado Generado
              <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse"></div>
            </h2>
            
            <div className="flex-1 bg-black/60 rounded-2xl border border-white/10 overflow-hidden relative group">
              <img 
                src="https://images.unsplash.com/photo-1530497610245-94d3c16cda28?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                alt="Imagen procesada" 
                className="w-full h-full object-cover opacity-90 transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-bg-darker via-transparent opacity-80 pointer-events-none" />
              
              <button 
                onClick={() => setIsImageMaximized(true)}
                className="absolute top-4 right-4 p-2.5 bg-black/50 hover:bg-black/70 text-white rounded-xl border border-white/20 opacity-0 group-hover:opacity-100 transition-all backdrop-blur-md z-20 hover:scale-110 shadow-lg"
                title="Agrandar imagen"
              >
                <Maximize2 size={18} />
              </button>

              <div className="absolute bottom-4 left-4 right-4">
                <div className="text-sm font-medium text-white mb-1">Cerebro_Segmentado_Final.png</div>
                <div className="text-xs text-green-300 flex items-center gap-1.5">
                  <CheckCircle size={12} />
                  Procesamiento completado por la secuencia
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal Expandido de Imagen */}
      {isImageMaximized && (
        <div className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-300">
          <div className="relative w-full max-w-6xl bg-bg-darker border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full max-h-[90vh] animate-in zoom-in-95 duration-300">
            {/* Header del Modal */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <CheckCircle size={20} className="text-green-500" />
                Vista Detallada - Cerebro Segmentado Final
              </h3>
              <button 
                onClick={() => setIsImageMaximized(false)}
                className="text-text-secondary hover:text-red-400 p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                title="Cerrar vista"
              >
                <X size={24} />
              </button>
            </div>
            
            {/* Contenido de la Imagen */}
            <div className="flex-1 overflow-hidden p-6 bg-black/40 flex items-center justify-center dashboard-pattern">
              <img 
                src="https://images.unsplash.com/photo-1530497610245-94d3c16cda28?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80" 
                alt="Vista expandida de la segmentación" 
                className="max-w-full max-h-full object-contain rounded-xl shadow-2xl border border-white/10"
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal Expandido de Imagen Base Original */}
      {isBaseImageMaximized && baseImage && (
        <div className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-300">
          <div className="relative w-full max-w-6xl bg-bg-darker border border-white/10 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full max-h-[90vh] animate-in zoom-in-95 duration-300">
            {/* Header del Modal */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/20">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <ImagePlus size={20} className="text-blue-400" />
                Vista Detallada - Imagen Base Original
              </h3>
              <button 
                onClick={() => setIsBaseImageMaximized(false)}
                className="text-text-secondary hover:text-red-400 p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                title="Cerrar vista"
              >
                <X size={24} />
              </button>
            </div>
            
            {/* Contenido de la Imagen base expandida */}
            <div className="flex-1 overflow-hidden p-6 bg-black/40 flex items-center justify-center dashboard-pattern">
              <img 
                src={URL.createObjectURL(baseImage)} 
                alt="Vista expandida de la imagen original" 
                className="max-w-full max-h-full object-contain rounded-xl shadow-2xl border border-white/10"
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}