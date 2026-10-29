import React from "react";
import { useEffect, useMemo, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
  });
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`);
  return data;
}

function money(paise = 0) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(paise / 100);
}

function rupeesToPaise(value) {
  const match = String(value).trim().match(/^(\d+)(?:\.(\d{1,2}))?$/);
  if (!match) throw new Error("Enter an amount with up to two decimal places");
  return Number(match[1]) * 100 + Number((match[2] || "").padEnd(2, "0"));
}

function today() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

export default function App() {
  const [page, setPage] = useState("Overview");
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [restock, setRestock] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [records, setRecords] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [recordDate, setRecordDate] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [itemFilter, setItemFilter] = useState("all");
  const [restockFilter, setRestockFilter] = useState("all");
  const [itemName, setItemName] = useState("");
  const [itemCategory, setItemCategory] = useState("");
  const [restockName, setRestockName] = useState("");
  const [restockCategory, setRestockCategory] = useState("");
  const [newCustomer, setNewCustomer] = useState("");
  const [creditCustomer, setCreditCustomer] = useState("");
  const [creditAmount, setCreditAmount] = useState("");
  const [creditDescription, setCreditDescription] = useState("");
  const [creditDate, setCreditDate] = useState(today());
  const [editing, setEditing] = useState(null);

  const selectedCustomer = customers.find((customer) => customer.id === selectedCustomerId);
  const filteredItems = useMemo(
    () => itemFilter === "all" ? items : items.filter((item) => item.category_id === Number(itemFilter)),
    [items, itemFilter],
  );

  const filteredRestock = useMemo(
    () => restockFilter === "all" ? restock : restock.filter((item) => item.category_id === Number(restockFilter)),
    [restock, restockFilter],
  );

  async function refreshData() {
    const [nextCategories, nextItems, nextRestock, nextCustomers] = await Promise.all([
      request("/categories"), request("/items"), request("/restock-items"), request("/customers"),
    ]);
    setCategories(nextCategories);
    setItems(nextItems);
    setRestock(nextRestock);
    setCustomers(nextCustomers);
    const defaultCategoryId = String(nextCategories.find((category) => category.name.toLowerCase() === "other")?.id || nextCategories[0]?.id || "");
    setItemCategory((current) => nextCategories.some((category) => String(category.id) === current) ? current : defaultCategoryId);
    setRestockCategory((current) => nextCategories.some((category) => String(category.id) === current) ? current : defaultCategoryId);
  }

  async function refreshRecords() {
    const params = new URLSearchParams();
    if (selectedCustomerId) params.set("customer_id", selectedCustomerId);
    if (recordDate) params.set("entry_date", recordDate);
    setRecords(await request(`/credit-records${params.size ? `?${params}` : ""}`));
  }

  useEffect(() => {
    refreshData().catch((reason) => setError(reason.message));
  }, []);

  useEffect(() => {
    refreshRecords().catch((reason) => setError(reason.message));
  }, [selectedCustomerId, recordDate]);

  async function perform(action, successMessage) {
    setError("");
    setNotice("");
    try {
      await action();
      await Promise.all([refreshData(), refreshRecords()]);
      setNotice(successMessage);
    } catch (reason) {
      setError(reason.message);
    }
  }

  function addCategory(event) {
    event.preventDefault();
    perform(async () => {
      await request("/categories", { method: "POST", body: JSON.stringify({ name: categoryName }) });
      setCategoryName("");
    }, "Category added.");
  }

  function addCatalogItem(event) {
    event.preventDefault();
    perform(async () => {
      await request("/items", { method: "POST", body: JSON.stringify({ name: itemName, category_id: Number(itemCategory) }) });
      setItemName("");
    }, "Item added.");
  }

  function addRestockItem(event) {
    event.preventDefault();
    perform(async () => {
      await request("/restock-items", { method: "POST", body: JSON.stringify({ name: restockName, category_id: Number(restockCategory) }) });
      setRestockName("");
    }, "Added to the restock list.");
  }

  function addCustomer(event) {
    event.preventDefault();
    perform(async () => {
      const customer = await request("/customers", { method: "POST", body: JSON.stringify({ name: newCustomer }) });
      setNewCustomer("");
      setSelectedCustomerId(customer.id);
      setCreditCustomer(customer.name);
    }, "Customer added.");
  }

  function addCredit(event) {
    event.preventDefault();
    perform(async () => {
      await request("/credit-records", {
        method: "POST",
        body: JSON.stringify({
          customer: creditCustomer,
          amount_paise: rupeesToPaise(creditAmount),
          description: creditDescription,
          entry_date: creditDate || null,
        }),
      });
      setCreditAmount("");
      setCreditDescription("");
    }, "Credit entry added.");
  }

  function saveEdit(event) {
    event.preventDefault();
    perform(async () => {
      await request(`/credit-records/${editing.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          customer: editing.customer,
          amount_paise: rupeesToPaise(editing.amount),
          entry_date: editing.entry_date,
          description: editing.description,
        }),
      });
      setEditing(null);
    }, "Credit entry updated.");
  }

  async function remove(path, successMessage, confirmText) {
    if (confirmText && !window.confirm(confirmText)) return;
    await perform(() => request(path, { method: "DELETE" }), successMessage);
  }

  function chooseCustomer(customer) {
    setSelectedCustomerId(customer.id);
    setCreditCustomer(customer.name);
    setRecordDate("");
  }

  const nav = ["Overview", "Items", "Restocking", "Khata"];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div><h1>Dukaan Dost</h1><p>Shop dashboard</p></div>
        <nav aria-label="Main navigation">
          {nav.map((name) => <button key={name} className={page === name ? "active" : ""} onClick={() => setPage(name)}>{name}</button>)}
        </nav>
      </header>

      {(notice || error) && <div className={error ? "message error" : "message"} role="status">{error || notice}<button onClick={() => { setError(""); setNotice(""); }}>Dismiss</button></div>}

      {page === "Overview" && <section>
        <h2>Overview</h2>
        <div className="summary-grid">
          <Summary label="Catalog items" value={items.length} />
          <Summary label="Categories" value={categories.length} />
          <Summary label="To restock" value={restock.length} />
          <Summary label="Customers" value={customers.length} />
          <Summary label="Total khata" value={money(customers.reduce((sum, customer) => sum + customer.total_paise, 0))} />
        </div>
        <h3>Recent credit entries</h3>
        <CreditTable records={records.slice(0, 8)} onEdit={setEditing} onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />
      </section>}

      {page === "Items" && <section>
        <h2>Items</h2>
        <div className="columns">
          <div className="panel">
            <h3>Categories</h3>
            <form onSubmit={addCategory} className="inline-form">
              <input required value={categoryName} onChange={(e) => setCategoryName(e.target.value)} placeholder="New category name" />
              <button>Add category</button>
            </form>
            {categories.length === 0 ? <p>No categories yet.</p> : <ul className="plain-list">{categories.map((category) => <li key={category.id}><span>{category.name}</span><button className="danger" disabled={category.name.toLowerCase() === "other"} title={category.name.toLowerCase() === "other" ? "Default category cannot be deleted" : "Delete category"} onClick={() => remove(`/categories/${category.id}`, "Category deleted.", `Delete category “${category.name}”? It must be empty.`)}>Delete</button></li>)}</ul>}
          </div>
          <div className="panel">
            <h3>Add catalog item</h3>
            {categories.length === 0 ? <p>Add a category first.</p> : <form onSubmit={addCatalogItem} className="stack-form">
              <input required value={itemName} onChange={(e) => setItemName(e.target.value)} placeholder="Item name" />
              <select required value={itemCategory} onChange={(e) => setItemCategory(e.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select>
              <button>Add item</button>
            </form>}
          </div>
        </div>
        <div className="panel">
          <div className="section-heading"><h3>Catalog</h3><select value={itemFilter} onChange={(e) => setItemFilter(e.target.value)}><option value="all">All categories</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></div>
          {filteredItems.length === 0 ? <p>No items to show.</p> : <ul className="plain-list">{filteredItems.map((item) => <li key={item.id}><span>{item.name} <small>({item.category_name})</small></span><button className="danger" onClick={() => remove(`/items/${item.id}`, "Item deleted.", `Delete “${item.name}” from the catalog?`)}>Delete</button></li>)}</ul>}
        </div>
      </section>}

      {page === "Restocking" && <section>
        <h2>Restocking list</h2>
        <div className="panel">
          <h3>Add an item to restock</h3>
          {categories.length === 0 ? <p>Add a category on the Items page first.</p> : <form onSubmit={addRestockItem} className="inline-form wrap-form">
            <input required value={restockName} onChange={(e) => setRestockName(e.target.value)} placeholder="Item name" />
            <select required value={restockCategory} onChange={(e) => setRestockCategory(e.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select>
            <button>Add to list</button>
          </form>}
        </div>
        <div className="panel">
          <div className="section-heading"><h3>Items to order ({filteredRestock.length})</h3><select value={restockFilter} onChange={(e) => setRestockFilter(e.target.value)}><option value="all">All categories</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select><button className="danger" disabled={!restock.length} onClick={() => remove("/restock-items", "Restock list cleared.", "Clear the entire restock list?")}>Clear list</button></div>
          {filteredRestock.length === 0 ? <p>{restock.length === 0 ? "The restock list is empty." : "No items in this category."}</p> : <ul className="plain-list">{filteredRestock.map((item) => <li key={item.id}><span>{item.name} <small>({item.category_name})</small></span><button className="danger" onClick={() => remove(`/restock-items/${item.id}`, "Restock item removed.", `Remove “${item.name}” from the restock list?`)}>Remove</button></li>)}</ul>}
        </div>
      </section>}

      {page === "Khata" && <section>
        <h2>Khata</h2>
        <div className="columns khata-columns">
          <div className="panel">
            <h3>Customers</h3>
            <form onSubmit={addCustomer} className="inline-form">
              <input required value={newCustomer} onChange={(e) => setNewCustomer(e.target.value)} placeholder="Customer name" />
              <button>Add customer</button>
            </form>
            {customers.length === 0 ? <p>No customers yet.</p> : <ul className="customer-list">{customers.map((customer) => <li key={customer.id}><button className={selectedCustomerId === customer.id ? "customer-choice selected" : "customer-choice"} onClick={() => chooseCustomer(customer)}><span>{customer.name}</span><strong>{money(customer.total_paise)}</strong></button></li>)}</ul>}
          </div>
          <div className="panel">
            <h3>{selectedCustomer ? `Add credit for ${selectedCustomer.name}` : "Add a credit entry"}</h3>
            <form onSubmit={addCredit} className="stack-form">
              <input required value={creditCustomer} onChange={(e) => setCreditCustomer(e.target.value)} placeholder="Customer name" />
              <label>Amount in rupees<input required type="number" min="0.01" step="0.01" value={creditAmount} onChange={(e) => setCreditAmount(e.target.value)} placeholder="e.g. 125.50" /></label>
              <label>Date<input type="date" value={creditDate} onChange={(e) => setCreditDate(e.target.value)} /></label>
              <input value={creditDescription} onChange={(e) => setCreditDescription(e.target.value)} placeholder="Description (optional)" />
              <button>Add credit entry</button>
            </form>
          </div>
        </div>
        <div className="panel">
          <div className="section-heading">
            <h3>{selectedCustomer ? `${selectedCustomer.name}’s credit entries` : "Credit entries"}</h3>
            <div className="filters"><label>Date <input type="date" value={recordDate} onChange={(e) => setRecordDate(e.target.value)} /></label><button className="secondary" onClick={() => { setRecordDate(""); setSelectedCustomerId(null); }}>Show all</button>{selectedCustomer && <button className="danger" onClick={() => remove(`/customers/${selectedCustomer.id}/credit-records`, "Customer credit entries cleared.", `Delete all credit entries for ${selectedCustomer.name}?`)}>Clear customer entries</button>}</div>
          </div>
          <CreditTable records={records} onEdit={setEditing} onDelete={(id) => remove(`/credit-records/${id}`, "Credit entry deleted.", "Delete this credit entry?")} />
        </div>
      </section>}

      {editing && <div className="modal-backdrop" role="presentation"><form className="panel edit-modal stack-form" onSubmit={saveEdit}>
        <h2>Edit credit entry</h2>
        <label>Customer<input required value={editing.customer} onChange={(e) => setEditing({ ...editing, customer: e.target.value })} /></label>
        <label>Amount in rupees<input required type="number" min="0.01" step="0.01" value={editing.amount} onChange={(e) => setEditing({ ...editing, amount: e.target.value })} /></label>
        <label>Date<input required type="date" value={editing.entry_date} onChange={(e) => setEditing({ ...editing, entry_date: e.target.value })} /></label>
        <label>Description<input value={editing.description} onChange={(e) => setEditing({ ...editing, description: e.target.value })} /></label>
        <div className="inline-form"><button>Save changes</button><button type="button" className="secondary" onClick={() => setEditing(null)}>Cancel</button></div>
      </form></div>}
    </main>
  );
}

function Summary({ label, value }) {
  return <div className="summary-card"><span>{label}</span><strong>{value}</strong></div>;
}

function CreditTable({ records, onEdit, onDelete }) {
  if (!records.length) return <p>No credit entries to show.</p>;
  return <div className="table-scroll"><table><thead><tr><th>Date</th><th>Customer</th><th>Description</th><th>Amount</th><th>Actions</th></tr></thead><tbody>
    {records.map((record) => <tr key={record.id}><td>{record.entry_date}</td><td>{record.customer}</td><td>{record.description || "—"}</td><td>{money(record.amount_paise)}</td><td className="actions"><button className="secondary" onClick={() => onEdit({ ...record, amount: (record.amount_paise / 100).toFixed(2) })}>Edit</button><button className="danger" onClick={() => onDelete(record.id)}>Delete</button></td></tr>)}
  </tbody></table></div>;
}





