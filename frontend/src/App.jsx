import React from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import PageHeader from "./components/PageHeader.jsx";
import { DashboardProvider } from "./context/DashboardContext.jsx";
import AssistantPage from "./pages/AssistantPage.jsx";
import AgentLogsPage from "./pages/AgentLogsPage.jsx";
import ItemsPage from "./pages/ItemsPage.jsx";
import KhataPage from "./pages/KhataPage.jsx";
import OverviewPage from "./pages/OverviewPage.jsx";
import RestockingPage from "./pages/RestockingPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";

function NotFoundPage() {
  return <section><PageHeader eyebrow="Wrong turn" title="Page not found" description="That page isn’t in this shop book." action={<Link className="button-link" to="/">Back to overview</Link>} /></section>;
}

export default function App() {
  return <AuthProvider><AuthenticatedApp /></AuthProvider>;
}

function AuthenticatedApp() {
  const { user, loading } = useAuth();
  if (loading) return <main className="login-screen"><section className="login-panel">
    <div className="brand-lockup login-brand"><span className="brand-mark" aria-hidden="true">दु</span>
      <div><h1>Dukaan Dost</h1><span className="brand-caption">Your shop, in order</span></div></div>
    <span className="eyebrow">Opening your shop book</span><p className="muted-copy">Checking your sign-in…</p>
  </section></main>;
  if (!user) return <LoginPage />;

  return <DashboardProvider>
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="items" element={<ItemsPage />} />
        <Route path="restocking" element={<RestockingPage />} />
        <Route path="khata" element={<KhataPage />} />
        <Route path="assistant" element={<AssistantPage />} />
        <Route path="agent-logs" element={<AgentLogsPage />} />
        <Route path="not-found" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/not-found" replace />} />
      </Route>
    </Routes>
  </DashboardProvider>;
}
