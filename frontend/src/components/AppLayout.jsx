import React, { useEffect, useState } from "react";
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
  const [confirmingLogout, setConfirmingLogout] = useState(false);
  const toastMessage = error || notice;

  useEffect(() => {
    if (!toastMessage) return undefined;
    const timer = window.setTimeout(() => {
      setError("");
      setNotice("");
    }, error ? 6500 : 3500);
    return () => window.clearTimeout(timer);
  }, [toastMessage, error, setError, setNotice]);

  useEffect(() => {
    if (!confirmingLogout) return undefined;
    function handleKeyDown(event) {
      if (event.key === "Escape") setConfirmingLogout(false);
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [confirmingLogout]);

  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">दु</span>
          <div><h1>Dukaan Dost</h1><span className="brand-caption">Your shop, in order</span></div>
        </div>
        <div className="account-tools">
          <span className="account-indicator" aria-hidden="true" />
          <div className="account-name"><small>Shopkeeper</small><strong>{user?.name}</strong></div>
          <button className="sign-out" onClick={() => setConfirmingLogout(true)}>Sign out</button>
        </div>
      </div>
    </header>
    <nav className="primary-nav" aria-label="Main navigation">
      <div className="nav-inner">
        {navigation.map(([name, path], index) => <NavLink
          key={path} to={path} end={path === "/"} data-index={String(index + 1).padStart(2, "0")}
          className={({ isActive }) => isActive ? "active" : ""}
        >{name}</NavLink>)}
      </div>
    </nav>
    <div className="content-wrap">
      {toastMessage && <div className={error ? "toast toast-error" : "toast"} role={error ? "alert" : "status"}>
        <span className="toast-mark" aria-hidden="true">{error
          ? <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" /><path d="M12 8v5m0 3.5h.01" /></svg>
          : <svg viewBox="0 0 24 24"><path d="m5 12 4.5 4.5L19 7" /></svg>}</span>
        <span className="toast-copy">{toastMessage}</span>
        <button className="toast-dismiss" aria-label="Dismiss notification" onClick={() => { setError(""); setNotice(""); }}>×</button>
      </div>}
      <main className="page-content" id="main-content"><Outlet /></main>
    </div>
    <EditCreditModal />
    {confirmingLogout && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setConfirmingLogout(false); }}>
      <section className="panel logout-dialog" role="dialog" aria-modal="true" aria-labelledby="logout-title" aria-describedby="logout-description">
        <span className="eyebrow">Dukaan Dost</span>
        <h2 id="logout-title">Sign out of your shop?</h2>
        <p id="logout-description">You’ll need to sign in again to open your shop dashboard.</p>
        <div className="inline-form modal-actions">
          <button type="button" className="secondary" autoFocus onClick={() => setConfirmingLogout(false)}>Stay signed in</button>
          <button type="button" className="logout-confirm" onClick={() => logout()}>Sign out</button>
        </div>
      </section>
    </div>}
  </div>;
}
