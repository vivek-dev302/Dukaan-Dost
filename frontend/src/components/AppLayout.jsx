import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext.jsx";
import EditCreditModal from "./EditCreditModal.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const navigation = [
  ["Overview", "/"], ["Items", "/items"], ["Restocking", "/restocking"], ["Khata", "/khata"], ["Assistant", "/assistant"], ["Agent activity", "/agent-logs"],
];

export default function AppLayout() {
  const { notice, error, setNotice, setError } = useDashboard();
  const { user, logout } = useAuth();
  return <main className="app-shell">
    <header className="topbar">
      <div><h1>Dukaan Dost</h1><p>Shop dashboard · {user?.name}</p></div>
      <nav aria-label="Main navigation">
        {navigation.map(([name, path]) => <NavLink key={path} to={path} end={path === "/"} className={({ isActive }) => isActive ? "active" : ""}>{name}</NavLink>)}
        <button className="secondary" onClick={() => logout()}>Sign out</button>
      </nav>
    </header>
    {(notice || error) && <div className={error ? "message error" : "message"} role="status">
      {error || notice}<button onClick={() => { setError(""); setNotice(""); }}>Dismiss</button>
    </div>}
    <Outlet />
    <EditCreditModal />
  </main>;
}
