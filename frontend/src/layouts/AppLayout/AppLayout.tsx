import { Outlet } from 'react-router-dom';
import { Header } from '../../components/layout/Header/Header';
import { Sidebar } from '../../components/layout/Sidebar/Sidebar';
import './AppLayout.css';

export function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-layout__main">
        <Header />
        <main className="app-layout__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
