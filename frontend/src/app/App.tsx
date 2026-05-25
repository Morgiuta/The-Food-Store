import { Navigate, Route, Routes } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage/LoginPage';
import { RegisterPage } from '../pages/RegisterPage/RegisterPage';
import { ProtectedRoute } from './routes/ProtectedRoute';
import { AdminLayout } from '../layouts/AdminLayout/AdminLayout';
import { StoreLayout } from '../layouts/StoreLayout/StoreLayout';
import { HomePage } from '../pages/HomePage/HomePage';
import { SuppliesPage } from '../pages/SuppliesPage/SuppliesPage';
import { CategoriasPage } from '../pages/CategoriasPage/CategoriasPage';
import { ProductosPage } from '../pages/ProductosPage/ProductosPage';
import { PedidosPage } from '../pages/PedidosPage/PedidosPage';
import { UsuariosPage } from '../pages/UsuariosPage/UsuariosPage';
import { StoreHomePage } from '../pages/StoreHomePage/StoreHomePage';
import { CartPage } from '../pages/CartPage/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage/CheckoutPage';
import { AddressesPage } from '../pages/AddressesPage/AddressesPage';
import { MyOrdersPage } from '../pages/MyOrdersPage/MyOrdersPage';

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegisterPage />} />
      
      {/* RUTAS DEL MODULO STORE */}
      <Route path="/" element={<StoreLayout />}>
        <Route index element={<StoreHomePage />} />
        <Route path="carrito" element={<CartPage />} />
        <Route
          path="checkout"
          element={
            <ProtectedRoute allowedRoles={['CLIENT']}>
              <CheckoutPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="mis-direcciones"
          element={
            <ProtectedRoute allowedRoles={['CLIENT']}>
              <AddressesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="mis-pedidos"
          element={
            <ProtectedRoute allowedRoles={['CLIENT']}>
              <MyOrdersPage />
            </ProtectedRoute>
          }
        />
      </Route>
      
      {/* RUTAS DEL MODULO ADMINISTRACION */}
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
