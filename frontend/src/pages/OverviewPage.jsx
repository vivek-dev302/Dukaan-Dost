import React from "react";
import { Link } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { money } from "../api/client.js";
import CreditTable from "../components/CreditTable.jsx";
import Summary from "../components/Summary.jsx";
import EmptyState from "../components/EmptyState.jsx";
import VoiceCallButton from "../components/VoiceCallButton.jsx";

export default function OverviewPage() {
  const { items, categories, restock, customers, records, initialLoading, saving, setEditing, remove } = useDashboard();
  const { user } = useAuth();
  const firstName = user?.name?.split(" ")[0] || "shopkeeper";
  const totalKhata = customers.reduce((sum, customer) => sum + customer.total_paise, 0);
  return <section className="overview-page">
    <header className="overview-hero">
      <div className="overview-welcome">
        <span className="overview-brand-mark" aria-hidden="true">दु</span>
        <div>
          <h2>Welcome back, {firstName}</h2>
          <p>A quick look at the things you keep, the goods to order, and the credit on your books.</p>
        </div>
      </div>
      <div className="overview-voice">
        <span>Ready when you are</span>
        <VoiceCallButton prominent />
      </div>
    </header>
    <div className="overview-priorities">
      <article className="priority-card khata-priority">
        <div><span className="priority-label">Outstanding khata</span>
          <strong>{initialLoading ? "—" : money(totalKhata)}</strong>
          <small>Total customer credit</small></div>
        <Link className="priority-link" to="/khata">Open khata <span aria-hidden="true">→</span></Link>
      </article>
      <article className="priority-card restock-priority">
        <div><span className="priority-label">To restock</span>
          <strong>{initialLoading ? "—" : restock.length}</strong>
          <small>On the next order list</small></div>
        <Link className="priority-link" to="/restocking">Review list <span aria-hidden="true">→</span></Link>
      </article>
    </div>
    <div className="summary-grid overview-supporting-metrics">
      <Summary label="Catalog items" value={initialLoading ? "—" : items.length} detail="In your item reference" />
      <Summary label="Customers" value={initialLoading ? "—" : customers.length} detail="In the khata book" />
      <Summary label="Categories" value={initialLoading ? "—" : categories.length} detail="Across your catalog" />
    </div>
    <section className="panel recent-panel">
      <div className="section-heading">
        <div><span className="eyebrow">From the khata book</span><h3>Recent credit entries</h3></div>
        <Link className="text-link" to="/khata">View all entries <span aria-hidden="true">→</span></Link>
      </div>
      {initialLoading ? <div className="loading-line" role="status">Loading your latest entries…</div>
        : records.length ? <CreditTable records={records.slice(0, 8)} saving={saving} onEdit={setEditing}
          onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />
          : <EmptyState title="The khata is quiet" description="Credit entries will appear here as you add them." />}
    </section>
  </section>;
}
