import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import { money } from "../api/client.js";
import CreditTable from "../components/CreditTable.jsx";
import Summary from "../components/Summary.jsx";

export default function OverviewPage() {
  const { items, categories, restock, customers, records, setEditing, remove } = useDashboard();
  return <section>
    <h2>Overview</h2>
    <div className="summary-grid">
      <Summary label="Catalog items" value={items.length} /><Summary label="Categories" value={categories.length} />
      <Summary label="To restock" value={restock.length} /><Summary label="Customers" value={customers.length} />
      <Summary label="Total khata" value={money(customers.reduce((sum, customer) => sum + customer.total_paise, 0))} />
    </div>
    <h3>Recent credit entries</h3>
    <CreditTable records={records.slice(0, 8)} onEdit={setEditing}
      onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />
  </section>;
}
