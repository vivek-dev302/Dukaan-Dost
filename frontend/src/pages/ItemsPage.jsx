import React, { useState } from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function ItemsPage() {
  const {
    categories, items, initialLoading, saving, categoryName, setCategoryName, addCategory, itemName, setItemName,
    itemCategory, setItemCategory, addCatalogItem, remove,
  } = useDashboard();
  const [categorySearch, setCategorySearch] = useState("");
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const selectedCategory = categories.find((category) => category.id === selectedCategoryId);
  const visibleCategories = categories.filter((category) => category.name.toLowerCase().includes(categorySearch.trim().toLowerCase()));
  const categoryItems = items.filter((item) => item.category_id === selectedCategoryId);
  const visibleItems = categoryItems.filter((item) => item.name.toLowerCase().includes(categorySearch.trim().toLowerCase()));

  return <section className="items-page">
    <PageHeader eyebrow="Your reference catalog" title="Items & categories" description="Keep a simple list of the products your shop carries. Quantities are not tracked here." />
    <div className="workspace-grid">
      <div className="workspace-main">
        <div className="panel ledger-panel">
          <div className="section-heading">
            <div><span className="eyebrow">{selectedCategory ? "Category contents" : "Organize"}</span><h3>{selectedCategory ? selectedCategory.name : "Categories"}</h3></div>
            <div className="list-heading-actions">
              {selectedCategory ? <>
                <span className="count-mark" aria-label={`${categoryItems.length} items`}>{initialLoading ? "—" : categoryItems.length}</span>
                <button type="button" className="secondary compact-button" onClick={() => { setSelectedCategoryId(null); setCategorySearch(""); }}>Back to categories</button>
              </> : <>
                <span className="count-mark" aria-label={`${categories.length} categories`}>{initialLoading ? "—" : categories.length}</span>
                <button type="button" className="secondary compact-button" aria-expanded={showCategoryForm} onClick={() => setShowCategoryForm((open) => !open)}>
                  {showCategoryForm ? "Close" : "+ Category"}
                </button>
              </>}
            </div>
          </div>
          {!selectedCategory && showCategoryForm && <form onSubmit={addCategory} className="inline-create-form">
            <label className="sr-only" htmlFor="new-category-name">Category name</label>
            <input id="new-category-name" required value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="New category name" autoFocus />
            <button disabled={saving}>{saving ? "Saving…" : "Add"}</button>
          </form>}
          <label className="search-field">
            <span className="sr-only">{selectedCategory ? "Search items in category" : "Search categories"}</span>
            <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></svg>
            <input type="search" value={categorySearch} onChange={(event) => setCategorySearch(event.target.value)} placeholder={selectedCategory ? "Search items" : "Search categories"} />
          </label>
          {initialLoading ? <p className="muted-copy">{selectedCategory ? "Loading items…" : "Loading categories…"}</p> : selectedCategory
            ? visibleItems.length === 0
              ? <EmptyState title={categoryItems.length ? "No matching items" : "No items in this category yet"} description={categoryItems.length ? "Try another search." : "Add an item from the form to get started."} />
              : <ul className="plain-list">{visibleItems.map((item) => <li key={item.id}>
                <span className="list-primary">{item.name}</span>
                <button className="text-button danger" disabled={saving} onClick={() => remove(`/items/${item.id}`, "Item deleted.", `Delete “${item.name}” from the catalog?`)}>Remove</button>
              </li>)}</ul>
            : visibleCategories.length === 0
              ? <EmptyState title={categories.length ? "No matching categories" : "No categories yet"} description={categories.length ? "Try another search." : "Add a category to start organizing your catalog."} />
              : <ul className="plain-list category-list">{visibleCategories.map((category) => <li key={category.id}>
                <button type="button" className="category-choice" onClick={() => { setSelectedCategoryId(category.id); setItemCategory(String(category.id)); setCategorySearch(""); }}>
                  <span className="list-primary">{category.name}{category.name.toLowerCase() === "other" && <span className="tag">Default</span>}</span><span className="category-open-hint">View items ›</span>
                </button>
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
