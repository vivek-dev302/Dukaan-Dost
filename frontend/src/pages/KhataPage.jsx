import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import { money } from "../api/client.js";
import CreditTable from "../components/CreditTable.jsx";

export default function KhataPage() {
  const {
    customers, selectedCustomerId, selectedCustomer, chooseCustomer, newCustomer, setNewCustomer, addCustomer,
    creditCustomer, setCreditCustomer, creditAmount, setCreditAmount, creditDate, setCreditDate,
    creditDescription, setCreditDescription, addCredit, recordDate, setRecordDate, setSelectedCustomerId,
    remove, records, setEditing,
  } = useDashboard();
  return <section>
    <h2>Khata</h2>
    <div className="columns khata-columns">
      <div className="panel">
        <h3>Customers</h3>
        <form onSubmit={addCustomer} className="inline-form">
          <input required value={newCustomer} onChange={(event) => setNewCustomer(event.target.value)} placeholder="Customer name" />
          <button>Add customer</button>
        </form>
        {customers.length === 0 ? <p>No customers yet.</p> : <ul className="customer-list">{customers.map((customer) => <li key={customer.id}>
          <button className={selectedCustomerId === customer.id ? "customer-choice selected" : "customer-choice"} onClick={() => chooseCustomer(customer)}>
            <span>{customer.name}</span><strong>{money(customer.total_paise)}</strong>
          </button>
        </li>)}</ul>}
      </div>
      <div className="panel">
        <h3>{selectedCustomer ? `Add credit for ${selectedCustomer.name}` : "Add a credit entry"}</h3>
        <form onSubmit={addCredit} className="stack-form">
          <input required value={creditCustomer} onChange={(event) => setCreditCustomer(event.target.value)} placeholder="Customer name" />
          <label>Amount in rupees<input required type="number" min="0.01" step="0.01" value={creditAmount} onChange={(event) => setCreditAmount(event.target.value)} placeholder="e.g. 125.50" /></label>
          <label>Date<input type="date" value={creditDate} onChange={(event) => setCreditDate(event.target.value)} /></label>
          <input value={creditDescription} onChange={(event) => setCreditDescription(event.target.value)} placeholder="Description (optional)" />
          <button>Add credit entry</button>
        </form>
      </div>
    </div>
    <div className="panel">
      <div className="section-heading">
        <h3>{selectedCustomer ? `${selectedCustomer.name}’s credit entries` : "Credit entries"}</h3>
        <div className="filters">
          <label>Date <input type="date" value={recordDate} onChange={(event) => setRecordDate(event.target.value)} /></label>
          <button className="secondary" onClick={() => { setRecordDate(""); setSelectedCustomerId(null); }}>Show all</button>
          {selectedCustomer && <button className="danger" onClick={() => remove(`/customers/${selectedCustomer.id}/credit-records`, "Customer credit entries cleared.", `Delete all credit entries for ${selectedCustomer.name}?`)}>Clear customer entries</button>}
        </div>
      </div>
      <CreditTable records={records} onEdit={setEditing}
        onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />
    </div>
  </section>;
}
