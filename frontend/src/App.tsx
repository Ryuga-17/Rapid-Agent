import React from 'react';
import { SSEProvider } from './context/SSEContext';
import { DashboardLayout } from './components/DashboardLayout';

function App() {
  return (
    <SSEProvider>
      <DashboardLayout />
    </SSEProvider>
  );
}

export default App;
