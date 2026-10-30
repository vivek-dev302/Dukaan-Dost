import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";

export default function RestockingPage() {
  const { categories, filteredRestock, restock, restockName, setRestockName, restockCategory, setRestockCategory,
    addRestockItem, restockFilter, setRestockFilter, remove } = useDashboard();
  return <section>
    <h2>Restocking list</h2>
    <div className="panel">
      <h3>Add an item to restock</h3>
      {categories.length === 0 ? <p>Add a category on the Items page first.</p> : <form onSubmit={addRestockItem} className="inline-form wrap-form">
        <input required value={restockName} onChange={(event) => setRestockName(event.target.value)} placeholder="Item name" />
        <select required value={restockCategory} onChange={(event) => setRestockCategory(event.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select>
        <button>Add to list</button>
      </form>}
    </div>
    <div className="panel">
      <div className="section-heading"><h3>Items to order ({filteredRestock.length})</h3>
        <select value={restockFilter} onChange={(event) => setRestockFilter(event.target.value)}><option value="all">All categories</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select>
        <button className="danger" disabled={!restock.length} onClick={() => remove("/restock-items", "Restock list cleared.", "Clear the entire restock list?")}>Clear list</button>
      </div>
      {filteredRestock.length === 0 ? <p>{restock.length === 0 ? "The restock list is empty." : "No items in this category."}</p>
        : <ul className="plain-list">{filteredRestock.map((item) => <li key={item.id}>
          <span>{item.name} <small>({item.category_name})</small></span>
          <button className="danger" onClick={() => remove(`/restock-items/${item.id}`, "Restock item removed.", `Remove “${item.name}” from the restock list?`)}>Remove</button>
        </li>)}</ul>}
    </div>
  </section>;
}
