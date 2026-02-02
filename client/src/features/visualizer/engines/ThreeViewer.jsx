import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage, Grid, Environment } from '@react-three/drei';
import BrainModel from './BrainModel';
import { UploadCloud, FileText, CheckCircle2 } from 'lucide-react';

function ViewerOverlay({ onUpload }) {
    return (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-10 transition-all duration-500">
            <div className="bg-slate-900 border border-slate-700 p-8 rounded-2xl shadow-2xl flex flex-col items-center gap-4 max-w-md text-center">
                <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center text-blue-400 mb-2">
                    <UploadCloud size={32} />
                </div>
                <h2 className="text-2xl font-bold text-white">Cargar Segmentación</h2>
                <p className="text-slate-400 text-sm">
                    Sube tus archivos .obj, .stl o .nii.gz para visualizar el modelo 3D y detectar anomalías.
                </p>

                <button
                    onClick={onUpload}
                    className="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium flex items-center gap-2 transition-all shadow-lg shadow-blue-600/20"
                >
                    <FileText size={18} />
                    Seleccionar Archivo (Demo)
                </button>
            </div>
        </div>
    );
}

export default function ThreeViewer() {
    const [hasModel, setHasModel] = useState(false);

    // Simula la carga de un modelo
    const handleUpload = () => {
        setHasModel(true);
    };

    return (
        <div className="w-full h-full relative">
            {!hasModel && <ViewerOverlay onUpload={handleUpload} />}

            <Canvas shadows camera={{ position: [0, 0, 5], fov: 45 }}>
                <color attach="background" args={['#050b14']} />

                {/* Iluminación dramática médica */}
                <ambientLight intensity={0.2} />
                <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
                <pointLight position={[-10, -10, -10]} intensity={0.5} color="#3b82f6" />

                <group position={[0, -0.5, 0]}>
                    {hasModel ? (
                        <Stage intensity={0.5} environment="city" adjustCamera={false}>
                            <BrainModel />
                        </Stage>
                    ) : null}
                </group>

                <Grid
                    renderOrder={-1}
                    position={[0, -2, 0]}
                    infiniteGrid
                    cellSize={0.5}
                    sectionSize={2.5}
                    fadeDistance={20}
                    sectionColor="#1e293b"
                    cellColor="#0f172a"
                />

                <OrbitControls
                    makeDefault
                    autoRotate={hasModel}
                    autoRotateSpeed={0.5}
                    minDistance={2}
                    maxDistance={10}
                />

                <Environment preset="city" />
            </Canvas>

            {hasModel && (
                <div className="absolute top-4 left-4 z-10 glass-panel p-4 rounded-xl">
                    <div className="flex items-center gap-2 text-green-400 mb-1">
                        <CheckCircle2 size={16} />
                        <span className="text-xs font-bold uppercase tracking-wider">Análisis Completado</span>
                    </div>
                    <h3 className="text-lg font-bold text-white">Paciente: Juan Pérez</h3>
                    <p className="text-xs text-slate-400">ID: #8392-A2 • Scan Date: 2024-02-02</p>
                </div>
            )}
        </div>
    );
}
