import { Navigate, Route, Routes } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage/LoginPage';
import { ProtectedRoute } from './routes/ProtectedRoute';
import { AdminLayout } from '../layouts/AdminLayout/AdminLayout';
import { HomePage } from '../pages/HomePage/HomePage';
import { SuppliesPage } from '../pages/SuppliesPage/SuppliesPage';
import { CategoriasPage } from '../pages/CategoriasPage/CategoriasPage';
import { ProductosPage } from '../pages/ProductosPage/ProductosPage';
import { PedidosPage } from '../pages/PedidosPage/PedidosPage';
import { UsuariosPage } from '../pages/UsuariosPage/UsuariosPage';

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      {/* RUTAS DEL MÓDULO STORE (Públicas y Privadas de cliente) */}
      <Route path="/" element={<div className="p-8"><h1 className="text-2xl font-bold">Store Home</h1><p>Módulo de tienda en construcción...</p><a href="/admin" className="text-primary hover:underline">Ir al Panel de Admin</a></div>} />
      
      {/* RUTAS DEL MÓDULO ADMINISTRACIÓN */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK', 'PEDIDOS']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<HomePage />} />
        
        
        {/* Aquí irán las pantallas que heredaremos del parcial 1 y adaptaremos */}
        <Route path="categorias" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK', 'PEDIDOS']}>
            <CategoriasPage />
          </ProtectedRoute>
        } />
        <Route path="ingredientes" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <SuppliesPage />
          </ProtectedRoute>
        } />
        <Route path="productos" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <ProductosPage />
          </ProtectedRoute>
        } />
        
        <Route path="pedidos" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'PEDIDOS']}>
            <PedidosPage />
          </ProtectedRoute>
        } />
        <Route path="usuarios" element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <UsuariosPage />
          </ProtectedRoute>
        } />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
