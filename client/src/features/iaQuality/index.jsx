import React, { useRef } from 'react';
import { useIaQuality } from './hooks/useIaQuality';
import {
  Sparkles, UploadCloud, FileText, RefreshCw, CheckCircle2,
  Zap, Layers, ArrowRight, AlertCircle, Eye, Brain, Filter, Info
} from 'lucide-react';

export default function IAQuality() {
  const {
    selectedFile, loading, result, error,
    selectedNodeIndex, setSelectedNodeIndex,
    handleFileSelect, runAutoEnhance, resetState
  } = useIaQuality();

  const fileInputRef = useRef(null);

  const activeNode = (selectedNodeIndex !== null && result?.nodos?.[selectedNodeIndex])
    ? result.nodos[selectedNodeIndex] : null;

  // Helper para nombres legibles de filtros
  const formatFilterName = (name) => {
    if (!name) return '';
    const clean = name.replace('_filter', '').replace(/_/g, ' ');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6 text-slate-100">

      {/* Header */}
      <div className="relative bg-slate-900/80 border border-slate-800 rounded-2xl p-6 overflow-hidden">
        <div className="absolute -top-12 -right-12 w-56 h-56 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-12 -left-12 w-56 h-56 bg-indigo-500/8 rounded-full blur-3xl pointer-events-none" />
        <div className="relative flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
            <Brain className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              Acondicionamiento de Imagen Cerebral con IA
            </h1>
            <p className="text-sm text-slate-400 mt-0.5">
              Optuna explora dinámicamente el árbol de filtros DICOM en busca de la combinación óptima de mejora.
            </p>
          </div>
          {selectedFile && (
            <button onClick={resetState}
              className="ml-auto flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl transition-all">
              <RefreshCw className="w-3 h-3" /> Nueva imagen
            </button>
          )}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left: Upload + Action */}
        <div className="lg:col-span-4 space-y-4">

          {/* Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); e.dataTransfer.files?.[0] && handleFileSelect(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all min-h-[200px] flex flex-col items-center justify-center ${
              selectedFile
                ? 'border-emerald-500/50 bg-emerald-500/5 hover:border-emerald-400'
                : 'border-slate-700 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/60'
            }`}>
            <input type="file" ref={fileInputRef} className="hidden"
              accept=".dcm,.dicom,image/*"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])} />

            {selectedFile ? (
              <div className="space-y-3">
                <div className="w-14 h-14 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto">
                  <FileText className="w-7 h-7 text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-200 break-all line-clamp-2">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                </div>
                <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                  <CheckCircle2 className="w-3 h-3" /> Listo para procesar
                </span>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-14 h-14 bg-slate-800 border border-slate-700 rounded-2xl flex items-center justify-center mx-auto">
                  <UploadCloud className="w-7 h-7 text-indigo-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-300">Arrastra o selecciona un archivo DICOM</p>
                  <p className="text-xs text-slate-500 mt-1">Resonancia Magnética o TAC cerebral (.dcm)</p>
                </div>
              </div>
            )}
          </div>

          {/* AI Info Banner */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-2 text-xs text-slate-400">
            <p className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Árbol de Exploración Optuna
            </p>
            <ul className="space-y-1 list-disc list-inside text-slate-500">
              <li>Construye pipelines de 4 etapas especializadas.</li>
              <li>Calcula CNR, Nitidez y Entropía en tejido cerebral.</li>
              <li>Aplica mezcla suave para proteger el fondo negro.</li>
            </ul>
          </div>

          {/* Submit Button */}
          <button
            onClick={runAutoEnhance}
            disabled={!selectedFile || loading}
            className={`w-full py-3.5 rounded-xl font-bold text-sm tracking-wide transition-all flex items-center justify-center gap-2 ${
              !selectedFile || loading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 active:scale-[0.98]'
            }`}>
            {loading ? (
              <><RefreshCw className="w-4 h-4 animate-spin" />IA Explorando Árbol de Filtros...</>
            ) : (
              <><Zap className="w-4 h-4 fill-current" />Optimizar Imagen con IA</>
            )}
          </button>

          {/* Error */}
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-start gap-2.5 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-8 space-y-5">
          {result ? (
            <>
              {/* Quality Metrics Row */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">Puntaje IA</p>
                    <p className="text-lg font-black text-emerald-400">{result.quality_score}</p>
                  </div>
                </div>
                <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
                  <div className={`p-2 rounded-lg border ${result.from_cache ? 'bg-indigo-500/10 border-indigo-500/20' : 'bg-amber-500/10 border-amber-500/20'}`}>
                    <Zap className={`w-4 h-4 ${result.from_cache ? 'text-indigo-400' : 'text-amber-400'}`} />
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">Modo</p>
                    <p className="text-xs font-bold text-slate-200">{result.from_cache ? '⚡ Caché' : '🤖 Exploración'}</p>
                  </div>
                </div>
                <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
                  <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
                    <Layers className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">Filtros Usados</p>
                    <p className="text-lg font-black text-cyan-400">{result.optimal_flow?.length || 0}</p>
                  </div>
                </div>
              </div>

              {/* Filtros Seleccionados (Lista visible explícita de nombres) */}
              {result.optimal_flow?.length > 0 && (
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                      <Filter className="w-4 h-4 text-emerald-400" /> Receta de Filtros Aplicada por la IA
                    </h3>
                    <span className="text-[10px] text-slate-500">Secuencia de 4 Etapas</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
                    {result.optimal_flow.map((step, idx) => (
                      <div key={step.id || idx}
                        onClick={() => setSelectedNodeIndex(idx)}
                        className={`p-3 rounded-xl border transition-all cursor-pointer ${
                          selectedNodeIndex === idx
                            ? 'bg-emerald-500/10 border-emerald-500 text-emerald-300 shadow-md'
                            : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                        }`}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Etapa {idx + 1}</span>
                          <span className="w-2 h-2 rounded-full bg-emerald-400/80"></span>
                        </div>
                        <p className="text-xs font-bold text-slate-100">{formatFilterName(step.filter_name)}</p>
                        {step.params && Object.keys(step.params).length > 0 && (
                          <p className="text-[10px] text-slate-500 mt-1 truncate">
                            {Object.entries(step.params).map(([k, v]) => `${k}: ${v}`).join(', ')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Image Comparison */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Eye className="w-4 h-4 text-emerald-400" /> Comparativa Visual
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Original</p>
                    <div className="aspect-square bg-black border border-slate-800 rounded-xl overflow-hidden flex items-center justify-center">
                      <img src={result.original_url} alt="Original" className="w-full h-full object-contain" />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <p className="text-[11px] font-semibold text-emerald-500 uppercase tracking-wider">
                      {activeNode ? `Nodo: ${formatFilterName(activeNode.filtro)}` : 'Mejorada por IA (Pipeline Completo)'}
                    </p>
                    <div className="aspect-square bg-black border border-emerald-500/30 rounded-xl overflow-hidden flex items-center justify-center relative">
                      <img
                        src={activeNode?.url || result.enhanced_url}
                        alt="Enhanced"
                        className="w-full h-full object-contain"
                      />
                      {!activeNode && (
                        <div className="absolute top-2 right-2 px-2 py-0.5 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-[10px] text-emerald-400 font-semibold">
                          ✓ Óptima
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Pipeline Step Selector */}
              {result.optimal_flow?.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" /> Inspección por Etapa
                    </h3>
                    <span className="text-[10px] text-slate-500">Selecciona una etapa para ver la vista previa intermedia</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <button onClick={() => setSelectedNodeIndex(null)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                        selectedNodeIndex === null
                          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}>
                      Resultado Final
                    </button>
                    {result.optimal_flow.map((step, idx) => (
                      <React.Fragment key={step.id || idx}>
                        <ArrowRight className="w-3 h-3 text-slate-700 shrink-0" />
                        <button onClick={() => setSelectedNodeIndex(idx)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                            selectedNodeIndex === idx
                              ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300'
                              : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                          }`}>
                          <span className="text-[9px] text-slate-600 block">Etapa {idx + 1}</span>
                          {formatFilterName(step.filter_name)}
                        </button>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="min-h-[420px] bg-slate-900/20 border border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-center p-10 space-y-4">
              <div className="w-16 h-16 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-center">
                <Brain className="w-8 h-8 text-slate-700" />
              </div>
              <div className="max-w-sm space-y-1">
                <h4 className="text-base font-bold text-slate-400">Sin resultados aún</h4>
                <p className="text-xs text-slate-600">
                  Sube una imagen DICOM cerebral y presiona el botón para que la IA explore las mejores combinaciones de filtros.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
