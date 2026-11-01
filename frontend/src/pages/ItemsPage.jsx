import React, { useState } from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function ItemsPage() {
  const {
    categories, initialLoading, saving, categoryName, setCategoryName, addCategory, itemName, setItemName,
    itemCategory, setItemCategory, addCatalogItem, remove,
  } = useDashboard();
  const [categorySearch, setCategorySearch] = useState("");
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const visibleCategories = categories.filter((category) => category.name.toLowerCase().includes(categorySearch.trim().toLowerCase()));

  return <section>
    <PageHeader eyebrow="Your reference catalog" title="Items & categories" description="Keep a simple list of the products your shop carries. Quantities are not tracked here." />
    <div className="workspace-grid">
      <div className="workspace-main">
        <div className="panel ledger-panel">
          <div className="section-heading">
            <div><span className="eyebrow">Organize</span><h3>Categories</h3></div>
            <div className="list-heading-actions">
              <span className="count-mark" aria-label={`${categories.length} categories`}>{initialLoading ? "—" : categories.length}</span>
              <button type="button" className="secondary compact-button" aria-expanded={showCategoryForm} onClick={() => setShowCategoryForm((open) => !open)}>
                {showCategoryForm ? "Close" : "+ Category"}
              </button>
            </div>
          </div>
          {showCategoryForm && <form onSubmit={addCategory} className="inline-create-form">
            <label className="sr-only" htmlFor="new-category-name">Category name</label>
            <input id="new-category-name" required value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="New category name" autoFocus />
            <button disabled={saving}>{saving ? "Saving…" : "Add"}</button>
          </form>}
          <label className="search-field">
            <span className="sr-only">Search categories</span>
            <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></svg>
            <input type="search" value={categorySearch} onChange={(event) => setCategorySearch(event.target.value)} placeholder="Search categories" />
          </label>
          {initialLoading ? <p className="muted-copy">Loading categories…</p> : visibleCategories.length === 0
            ? <EmptyState title={categories.length ? "No matching categories" : "No categories yet"} description={categories.length ? "Try another search." : "Add a category to start organizing your catalog."} />
            : <ul className="plain-list category-list">{visibleCategories.map((category) => <li key={category.id}>
              <span className="list-primary">{category.name}{category.name.toLowerCase() === "other" && <span className="tag">Default</span>}</span>
              <button className="text-button danger" disabled={saving || category.name.toLowerCase() === "other"}
                title={category.name.toLowerCase() === "other" ? "Default category cannot be deleted" : "Delete category"}
                onClick={() => remove(`/categories/${category.id}`, "Category deleted.", `Delete category “${category.name}”? It must be empty.`)}>Delete</button>
            </li>)}</ul>}
        </div>
      </div>
      <aside className="workspace-aside">
        <div className="panel ledger-panel entry-form-panel">
          <span className="eyebrow">Add to reference</span><h3>New catalog item</h3>
          {initialLoading ? <p className="muted-copy">Loading categories…</p> : categories.length === 0
            ? <EmptyState title="Add a category first" description="Every catalog item belongs to a category." />
            : <form onSubmit={addCatalogItem} className="stack-form">
              <label>Item name<input required value={itemName} onChange={(event) => setItemName(event.target.value)} placeholder="e.g. Basmati rice" /></label>
              <label>Category<select required value={itemCategory} onChange={(event) => setItemCategory(event.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
              <button disabled={saving}>{saving ? "Saving…" : "Add item to catalog"}</button>
            </form>}
        </div>
      </aside>
    </div>
  </section>;
}
