import React, { useState } from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import { money } from "../api/client.js";
import CreditTable from "../components/CreditTable.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function KhataPage() {
  const {
    customers, records, initialLoading, saving, selectedCustomerId, selectedCustomer, chooseCustomer, setSelectedCustomerId, recordDate, setRecordDate, newCustomer, setNewCustomer, addCustomer,
    creditCustomer, setCreditCustomer, creditAmount, setCreditAmount, creditDate, setCreditDate,
    creditDescription, setCreditDescription, addCredit, remove, setEditing,
  } = useDashboard();
  const [customerSearch, setCustomerSearch] = useState("");
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const visibleCustomers = customers.filter((customer) => customer.name.toLowerCase().includes(customerSearch.trim().toLowerCase()));

  return <section>
    <PageHeader eyebrow="Customer credit book" title="Khata" description="Keep track of who owes what, with a simple entry for each purchase or payment." />
    <div className="workspace-grid khata-workspace">
      <div className="workspace-main">
        <div className="panel ledger-panel customer-panel">
          <div className="section-heading">
            <div><span className="eyebrow">{selectedCustomer ? "Customer account" : "People"}</span><h3>{selectedCustomer ? selectedCustomer.name : "Customers"}</h3></div>
            <div className="list-heading-actions">
              {selectedCustomer ? <>
                <span className="count-mark" aria-label={`${records.length} credit entries`}>{initialLoading ? "—" : records.length}</span>
                <button type="button" className="secondary compact-button" onClick={() => { setSelectedCustomerId(null); setRecordDate(""); setCustomerSearch(""); }}>Back to customers</button>
              </> : <>
                <span className="count-mark" aria-label={`${customers.length} customers`}>{initialLoading ? "—" : customers.length}</span>
                <button type="button" className="secondary compact-button" aria-expanded={showCustomerForm} onClick={() => setShowCustomerForm((open) => !open)}>
                  {showCustomerForm ? "Close" : "+ Customer"}
                </button>
              </>}
            </div>
          </div>
          {selectedCustomer ? <>
            <div className="customer-record-heading">
              <span>Credit entries</span>
              <button className="text-button danger" disabled={saving || !records.length} onClick={() => remove(`/customers/${selectedCustomer.id}/credit-records`, "Customer credit entries cleared.", `Delete all credit entries for ${selectedCustomer.name}?`)}>Clear entries</button>
            </div>
            {initialLoading ? <p className="muted-copy">Loading khata entries…</p> : <CreditTable records={records} saving={saving} onEdit={setEditing}
              onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />}
          </> : <>
          {showCustomerForm && <form onSubmit={addCustomer} className="inline-create-form">
            <label className="sr-only" htmlFor="new-customer-name">Customer name</label>
            <input id="new-customer-name" required value={newCustomer} onChange={(event) => setNewCustomer(event.target.value)} placeholder="New customer name" autoFocus />
            <button disabled={saving}>{saving ? "Saving…" : "Add"}</button>
          </form>}
          <label className="search-field">
            <span className="sr-only">Search customers</span>
            <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></svg>
            <input type="search" value={customerSearch} onChange={(event) => setCustomerSearch(event.target.value)} placeholder="Search customers" />
          </label>
          {initialLoading ? <p className="muted-copy">Loading customers…</p> : visibleCustomers.length === 0
            ? <EmptyState title={customers.length ? "No matching customers" : "No customers yet"} description={customers.length ? "Try another search." : "Add a customer to start their khata."} />
            : <ul className="customer-list">{visibleCustomers.map((customer) => <li key={customer.id}>
              <button type="button" className={selectedCustomerId === customer.id ? "customer-choice selected" : "customer-choice"} onClick={() => chooseCustomer(customer)} aria-pressed={selectedCustomerId === customer.id}>
                <span className="customer-name"><span className="customer-initial" aria-hidden="true">{customer.name.charAt(0).toUpperCase()}</span>{customer.name}</span>
                <strong>{money(customer.total_paise)}</strong>
              </button>
            </li>)}</ul>}
          </>}
        </div>
      </div>
      <aside className="workspace-aside">
        <div className="panel ledger-panel entry-form-panel">
          <span className="eyebrow">Record a purchase or payment</span>
          <h3>{selectedCustomer ? `New entry for ${selectedCustomer.name}` : "Add a credit entry"}</h3>
          <form onSubmit={addCredit} className="stack-form">
            <label>Customer<input required value={creditCustomer} onChange={(event) => setCreditCustomer(event.target.value)} placeholder="Customer name" /></label>
            <div className="form-row">
              <label>Amount in rupees<input required type="number" min="0.01" step="0.01" value={creditAmount} onChange={(event) => setCreditAmount(event.target.value)} placeholder="125.50" inputMode="decimal" /></label>
              <label>Date<input type="date" value={creditDate} onChange={(event) => setCreditDate(event.target.value)} /></label>
            </div>
            <label>Note <span className="optional-label">Optional</span><input value={creditDescription} onChange={(event) => setCreditDescription(event.target.value)} placeholder="What was it for?" /></label>
            <button disabled={saving}>{saving ? "Saving…" : "Add to khata"}</button>
          </form>
        </div>
      </aside>
    </div>
  </section>;
}
