import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext.jsx";
import EditCreditModal from "./EditCreditModal.jsx";

const navigation = [
  ["Overview", "/"], ["Items", "/items"], ["Restocking", "/restocking"], ["Khata", "/khata"], ["Assistant", "/assistant"],
];

export default function AppLayout() {
  const { notice, error, setNotice, setError } = useDashboard();
  return <main className="app-shell">
    <header className="topbar">
      <div><h1>Dukaan Dost</h1><p>Shop dashboard</p></div>
      <nav aria-label="Main navigation">
        {navigation.map(([name, path]) => <NavLink key={path} to={path} end={path === "/"} className={({ isActive }) => isActive ? "active" : ""}>{name}</NavLink>)}
      </nav>
    </header>
    {(notice || error) && <div className={error ? "message error" : "message"} role="status">
      {error || notice}<button onClick={() => { setError(""); setNotice(""); }}>Dismiss</button>
    </div>}
    <Outlet />
    <EditCreditModal />
  </main>;
}
