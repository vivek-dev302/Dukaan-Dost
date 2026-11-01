import React from "react";
import { Link } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { money } from "../api/client.js";
import CreditTable from "../components/CreditTable.jsx";
import Summary from "../components/Summary.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function OverviewPage() {
  const { items, categories, restock, customers, records, initialLoading, saving, setEditing, remove } = useDashboard();
  const { user } = useAuth();
  const firstName = user?.name?.split(" ")[0] || "shopkeeper";
  const totalKhata = customers.reduce((sum, customer) => sum + customer.total_paise, 0);
  return <section>
    <PageHeader eyebrow="Your shop at a glance" title={`Welcome back, ${firstName}`} description="A quick look at the things you keep, the goods to order, and the credit on your books."
      action={<Link className="button-link" to="/assistant">Ask the assistant <span aria-hidden="true">↗</span></Link>} />
    <div className="summary-grid">
      <Summary label="Catalog items" value={initialLoading ? "—" : items.length} detail="In your item reference" />
      <Summary label="To restock" value={initialLoading ? "—" : restock.length} detail="On the next order list" />
      <Summary label="Customers" value={initialLoading ? "—" : customers.length} detail="In the khata book" />
      <Summary label="Categories" value={initialLoading ? "—" : categories.length} detail="Across your catalog" />
      <Summary label="Outstanding khata" value={initialLoading ? "—" : money(totalKhata)} detail="Total customer credit" featured />
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
