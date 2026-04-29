import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import IssuesPage from './pages/IssuesPage';
import AnalysisPage from './pages/AnalysisPage';
import ReportsPage from './pages/ReportsPage';
import DataSourcesPage from './pages/DataSourcesPage';
import KnowledgeBasesPage from './pages/KnowledgeBasesPage';
import ModelsPage from './pages/ModelsPage';
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
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/datasources" element={<DataSourcesPage />} />
          <Route path="/knowledge" element={<KnowledgeBasesPage />} />
          <Route path="/models" element={<ModelsPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
