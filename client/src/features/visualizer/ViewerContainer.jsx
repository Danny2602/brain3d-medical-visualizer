import React, { Suspense } from 'react';
import ThreeViewer from './engines/ThreeViewer';

// Este componente decidirá qué motor cargar.
// Por ahora, 'engine' se defaultea a 'three'. 
// Futuro: Podría cargar 'vtk' para visualización de volúmenes.
export default function ViewerContainer({ engine = 'three' }) {
    return (
        <div className="w-full h-full relative bg-gradient-to-b from-slate-900 to-black rounded-2xl overflow-hidden">
            <Suspense fallback={
                <div className="flex items-center justify-center h-full text-blue-400 animate-pulse">
                    Cargando Motor de Visualización...
                </div>
            }>
                {engine === 'three' && <ThreeViewer />}
                {/* engine === 'vtk' && <VTKViewer /> */}
            </Suspense>

            {/* Overlay UI Controls will go here */}
            <div className="absolute top-4 right-4 pointer-events-none">
                {/* UI Overlay placeholder */}
            </div>
        </div>
    );
}
