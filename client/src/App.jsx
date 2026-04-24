import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Segmentacion from './features/segmentacion';
import Bloques from './features/bloques';
import BloquesFlow from './features/bloquesFlow';


function App() {
  // Configuración de rutas principales
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" />
          <Route path="/dashboard" element={<div className="p-10 text-xl font-bold text-slate-500">Dashboard en construcción</div>} />
          <Route path="/segmentacion" element={<div className="p-10 text-xl font-bold text-slate-500"><Segmentacion /></div>} />
          <Route path="/bloques" element={<div className="p-10 text-xl font-bold text-slate-500"><Bloques /></div>} />
          <Route path="/bloquesflow" element={<div className="p-10 text-xl font-bold text-slate-500"><BloquesFlow /></div>} />
          <Route path="/settings" element={<div className="p-10 text-xl font-bold text-slate-500">Configuración en construcción</div>} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
