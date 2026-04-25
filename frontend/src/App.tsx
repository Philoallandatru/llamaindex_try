import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import IssuesPage from './pages/IssuesPage';
import AnalysisPage from './pages/AnalysisPage';
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/issues" element={<IssuesPage />} />
          <Route path="/analysis/:issueKey" element={<AnalysisPage />} />
          <Route path="/reports" element={<div style={{ padding: '40px', textAlign: 'center' }}>Reports page coming soon...</div>} />
          <Route path="/knowledge" element={<div style={{ padding: '40px', textAlign: 'center' }}>Knowledge page coming soon...</div>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
