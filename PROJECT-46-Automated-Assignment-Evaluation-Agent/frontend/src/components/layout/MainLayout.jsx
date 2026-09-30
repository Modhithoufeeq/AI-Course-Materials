import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const MainLayout = () => {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content-wrapper">
        <Topbar />
        <main className="page-viewport">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
