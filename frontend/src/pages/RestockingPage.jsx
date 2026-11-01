import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function RestockingPage() {
  const { categories, filteredRestock, restock, initialLoading, saving, restockName, setRestockName, restockCategory, setRestockCategory,
    addRestockItem, restockFilter, setRestockFilter, remove } = useDashboard();
  return <section>
    <PageHeader eyebrow="The next trip to the wholesaler" title="Restocking list" description="Keep a running note of what the shop needs. Add anything, even if it is not in the catalog." />
    <div className="workspace-grid">
      <div className="workspace-main">
        <div className="panel ledger-panel">
          <div className="section-heading"><div><span className="eyebrow">Ready for your next order</span><h3>Items to pick up <span className="inline-count">{initialLoading ? "—" : restock.length}</span></h3></div>
            <div className="filters">
              <label className="filter-control">Filter<select value={restockFilter} onChange={(event) => setRestockFilter(event.target.value)}><option value="all">All categories</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
              <button className="text-button danger" disabled={saving || !restock.length} onClick={() => remove("/restock-items", "Restock list cleared.", "Clear the entire restock list?")}>Clear list</button>
            </div>
          </div>
          {initialLoading ? <p className="muted-copy">Loading your list…</p> : filteredRestock.length === 0
            ? <EmptyState title={restock.length ? "Nothing in this category" : "Your order list is clear"}
              description={restock.length ? "Try a different filter or add another category item." : "Add items from the form as you notice the shelves running low."} />
            : <ul className="plain-list restock-list">{filteredRestock.map((item) => <li key={item.id}>
              <span className="list-primary">{item.name}<small className="tag">{item.category_name}</small></span>
              <button className="text-button danger" disabled={saving} onClick={() => remove(`/restock-items/${item.id}`, "Restock item removed.", `Remove “${item.name}” from the restock list?`)}>Remove</button>
            </li>)}</ul>}
        </div>
      </div>
      <aside className="workspace-aside">
        <div className="panel ledger-panel entry-form-panel">
          <div className="restock-entry-copy"><span className="eyebrow">Make a note</span><h3>What should we pick up?</h3></div>
          {initialLoading ? <p className="muted-copy">Loading categories…</p> : categories.length === 0 ? <p>Add a category on the Items page first.</p> : <form onSubmit={addRestockItem} className="stack-form">
            <label>Item name<input required value={restockName} onChange={(event) => setRestockName(event.target.value)} placeholder="e.g. Cooking oil" /></label>
            <label>Category<select required value={restockCategory} onChange={(event) => setRestockCategory(event.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
            <button disabled={saving}>{saving ? "Saving…" : "Add to list"}</button>
          </form>}
        </div>
      </aside>
    </div>
  </section>;
}
