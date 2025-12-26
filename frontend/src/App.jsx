import { Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import ChatPage from './pages/ChatPage';
import ConversationsPage from './pages/ConversationsPage';
import DocumentsPage from './pages/DocumentsPage';
import ConnectorsPage from './pages/ConnectorsPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
        <Route path="/conversations" element={<ConversationsPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/connectors" element={<ConnectorsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
