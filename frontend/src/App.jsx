import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import { DashboardProvider } from "./context/DashboardContext.jsx";
import AssistantPage from "./pages/AssistantPage.jsx";
import ItemsPage from "./pages/ItemsPage.jsx";
import KhataPage from "./pages/KhataPage.jsx";
import OverviewPage from "./pages/OverviewPage.jsx";
import RestockingPage from "./pages/RestockingPage.jsx";

function NotFoundPage() {
  return <section><h2>Page not found</h2><p>The page you requested does not exist.</p></section>;
}

export default function App() {
  return <DashboardProvider>
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="items" element={<ItemsPage />} />
        <Route path="restocking" element={<RestockingPage />} />
        <Route path="khata" element={<KhataPage />} />
        <Route path="assistant" element={<AssistantPage />} />
        <Route path="not-found" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/not-found" replace />} />
      </Route>
    </Routes>
  </DashboardProvider>;
}
