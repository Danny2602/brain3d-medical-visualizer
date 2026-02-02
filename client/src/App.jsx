import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import ViewerContainer from './features/visualizer/ViewerContainer';

function App() {
  // Configuración de rutas principales
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<ViewerContainer />} />
          <Route path="/dashboard" element={<div className="p-10 text-xl font-bold text-slate-500">Dashboard en construcción</div>} />
          <Route path="/layers" element={<div className="p-10 text-xl font-bold text-slate-500">Gestión de Capas en construcción</div>} />
          <Route path="/settings" element={<div className="p-10 text-xl font-bold text-slate-500">Configuración en construcción</div>} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
