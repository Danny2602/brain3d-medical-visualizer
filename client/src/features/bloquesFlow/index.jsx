import React, { useState, useCallback, useRef } from 'react';
import {
    ReactFlow,
    addEdge,
    Background,
    Controls,
    applyEdgeChanges,
    applyNodeChanges,
    useReactFlow,
    ReactFlowProvider
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { FILTER_TYPES, OPERATOR_TYPES } from './context/filtersExample';
import { useSegmentacion } from './hook/UseSegementacion';
import ImageNode from './components/ImageNode';
import FilterNode from './components/FilterNode';
import SidebarItem from './components/SidebarItem';
import { Layers, Settings2, Play, AlertCircle, X } from 'lucide-react';

const nodeTypes = {
    imageInput: ImageNode,
    filterNode: FilterNode,
};

function FlowContent() {
    const reactFlowWrapper = useRef(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [activeTab, setActiveTab] = useState('filters');
    const [expandedImage, setExpandedImage] = useState(null);

    const { screenToFlowPosition } = useReactFlow();
    const { ejecutarProcesamiento, loading, error } = useSegmentacion();

    const onNodeExpand = (url) => setExpandedImage(url);

    const [nodes, setNodes] = useState([
        {
            id: 'original',
            type: 'imageInput',
            data: {
                label: 'Imagen Original',
                onImageSelect: (file) => setSelectedFile(file),
                onExpand: onNodeExpand
            },
            position: { x: 300, y: 50 },
        },
    ]);
    const [edges, setEdges] = useState([]);

    const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
    const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

    const onDragStart = (event, filterData) => {
        event.dataTransfer.setData('application/reactflow', JSON.stringify(filterData));
        event.dataTransfer.effectAllowed = 'move';
    };

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback((event) => {
        event.preventDefault();
        const dataJson = event.dataTransfer.getData('application/reactflow');
        if (!dataJson) return;

        const filter = JSON.parse(dataJson);
        const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });

        const newNode = {
            id: `${filter.name}_${Date.now()}`,
            type: 'filterNode',
            position,
            data: {
                label: filter.label,
                filterName: filter.name,
                params: filter.params,
                resultUrl: null,
                processing: false,
                onExpand: onNodeExpand
            },
        };
        setNodes((nds) => nds.concat(newNode));
    }, [screenToFlowPosition]);

    const handleProcess = async () => {
        if (!selectedFile) return;

        // Marcamos todos los nodos como "en proceso"
        setNodes(nds => nds.map(n => n.id !== 'original' ? { ...n, data: { ...n.data, processing: true } } : n));

        const flowConfig = nodes
            .filter(n => n.id !== 'original')
            .filter(n => edges.some(e => e.target === n.id))
            .map(node => {
                const incomingEdges = edges.filter(e => e.target === node.id);
                const stepParams = { ...node.data.params };

                // LÓGICA DE PUERTOS: layer_a (Textura) y layer_b (Máscara)
                const edgeA = incomingEdges.find(e => e.targetHandle === 'a');
                const edgeB = incomingEdges.find(e => e.targetHandle === 'b');

                if (edgeA) stepParams.layer_a = edgeA.source;
                if (edgeB) stepParams.layer_b = edgeB.source;

                return {
                    id: node.id,
                    filter_name: node.data.filterName,
                    // Si no hay puerto 'a' explícito, usamos la primera conexión o la original
                    input_id: edgeA ? edgeA.source : (incomingEdges[0]?.source || 'original'),
                    params: stepParams
                };
            });

        const res = await ejecutarProcesamiento(selectedFile, flowConfig);

        if (res && res.nodos) {
            setNodes((nds) => nds.map((node) => {
                const nodeResult = res.nodos.find(n => n.id === node.id);
                if (nodeResult) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            resultUrl: nodeResult.url || node.data.resultUrl,
                            processing: false
                        }
                    };
                }
                return { ...node, data: { ...node.data, processing: false } };
            }));
        } else {
            // Si hay error, quitamos los loaders
            setNodes(nds => nds.map(n => ({ ...n, data: { ...n.data, processing: false } })));
        }
    };

    return (
        <div className="flex h-full w-full bg-slate-950 text-white overflow-hidden rounded-2xl border border-slate-800 shadow-2xl relative">

            {/* BARRA LATERAL */}
            <div className="w-80 border-r border-slate-800 flex flex-col bg-slate-900/50 backdrop-blur-xl z-20">
                <div className="p-6 pb-2">
                    <h2 className="text-xl font-black bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent tracking-tighter">PIPELINE STUDIO</h2>
                    <p className="text-[9px] text-slate-500 mt-1 uppercase tracking-[0.3em]">Medical Visualizer Node Engine</p>
                </div>

                <div className="flex px-4 mt-6 gap-2">
                    <button onClick={() => setActiveTab('filters')} className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'filters' ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'bg-slate-800 text-slate-500 hover:bg-slate-700'}`}>
                        <Settings2 size={12} /> Filtros
                    </button>
                    <button onClick={() => setActiveTab('operators')} className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'operators' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'bg-slate-800 text-slate-500 hover:bg-slate-700'}`}>
                        <Layers size={12} /> Operadores
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 mt-4 custom-scrollbar">
                    {Object.entries(activeTab === 'filters' ? FILTER_TYPES : OPERATOR_TYPES).map(([key, group]) => (
                        <div key={key} className="mb-8">
                            <h3 className="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em] mb-4 flex items-center gap-2">
                                <div className={`w-1.5 h-1.5 rounded-full bg-${group.color}-500 shadow-[0_0_8px] shadow-${group.color}-500`} />
                                {group.label}
                            </h3>
                            {group.items.map(item => (
                                <SidebarItem key={item.name} item={item} color={group.color} onDragStart={onDragStart} />
                            ))}
                        </div>
                    ))}
                </div>

                <div className="p-4 bg-slate-900 border-t border-slate-800">
                    {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-xl flex items-center gap-2 text-red-500 text-[10px] font-bold"><AlertCircle size={14} /> {error}</div>}
                    <button onClick={handleProcess} disabled={loading} className={`w-full group relative overflow-hidden p-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all hover:scale-[1.02] active:scale-95 shadow-2xl ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600" />
                        <div className="relative flex items-center justify-center gap-3">
                            {loading ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Play size={16} fill="currentColor" />}
                            {loading ? 'Procesando...' : 'Lanzar Pipeline'}
                        </div>
                    </button>
                </div>
            </div>

            {/* ÁREA DEL GRAFO */}
            <div className="flex-1 h-full relative" ref={reactFlowWrapper}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    nodeTypes={nodeTypes}
                    fitView
                >
                    <Background color="#1e293b" gap={25} variant="dots" />
                    <Controls position="bottom-right" className=" !shadow-2xl !fill-black !text-black" />
                </ReactFlow>
            </div>

            {/* MODAL DE IMAGEN EXPANDIDA */}
            {expandedImage && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-10 animate-in fade-in duration-300"
                    onClick={() => setExpandedImage(null)}
                >
                    <button className="absolute top-10 right-10 text-white/50 hover:text-white transition-colors">
                        <X size={40} />
                    </button>
                    <div className="relative max-w-5xl max-h-full" onClick={e => e.stopPropagation()}>
                        <img src={expandedImage} className="w-full h-full object-contain rounded-2xl shadow-2xl border border-white/10" alt="Full View" />
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-md px-6 py-2 rounded-full text-[10px] uppercase font-black tracking-[0.2em] text-white/70 border border-white/5">
                            Visualización de Alta Definición
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function BloquesFlow() {
    return (
        <div className="h-[calc(100vh-120px)] w-full p-4">
            <ReactFlowProvider>
                <FlowContent />
            </ReactFlowProvider>
        </div>
    );
}
