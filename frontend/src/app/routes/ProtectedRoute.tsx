import { Navigate, useLocation } from 'react-router-dom';
import type { PropsWithChildren } from 'react';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps extends PropsWithChildren {
  allowedRoles?: string[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    if (!allowedRoles.includes(user.role)) {
      // Si el rol no está permitido, lo mandamos al inicio (o una página de error)
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
}
