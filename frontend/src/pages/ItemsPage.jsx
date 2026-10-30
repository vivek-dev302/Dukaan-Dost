import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";

export default function ItemsPage() {
  const {
    categories, filteredItems, categoryName, setCategoryName, addCategory, itemName, setItemName,
    itemCategory, setItemCategory, addCatalogItem, itemFilter, setItemFilter, remove,
  } = useDashboard();
  return <section>
    <h2>Items</h2>
    <div className="columns">
      <div className="panel">
        <h3>Categories</h3>
        <form onSubmit={addCategory} className="inline-form">
          <input required value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="New category name" />
          <button>Add category</button>
        </form>
        {categories.length === 0 ? <p>No categories yet.</p> : <ul className="plain-list">{categories.map((category) => <li key={category.id}>
          <span>{category.name}</span><button className="danger" disabled={category.name.toLowerCase() === "other"}
            title={category.name.toLowerCase() === "other" ? "Default category cannot be deleted" : "Delete category"}
            onClick={() => remove(`/categories/${category.id}`, "Category deleted.", `Delete category “${category.name}”? It must be empty.`)}>Delete</button>
        </li>)}</ul>}
      </div>
      <div className="panel">
        <h3>Add catalog item</h3>
        {categories.length === 0 ? <p>Add a category first.</p> : <form onSubmit={addCatalogItem} className="stack-form">
          <input required value={itemName} onChange={(event) => setItemName(event.target.value)} placeholder="Item name" />
          <select required value={itemCategory} onChange={(event) => setItemCategory(event.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select>
          <button>Add item</button>
        </form>}
      </div>
    </div>
    <div className="panel">
      <div className="section-heading"><h3>Catalog</h3><select value={itemFilter} onChange={(event) => setItemFilter(event.target.value)}>
        <option value="all">All categories</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
      </select></div>
      {filteredItems.length === 0 ? <p>No items to show.</p> : <ul className="plain-list">{filteredItems.map((item) => <li key={item.id}>
        <span>{item.name} <small>({item.category_name})</small></span>
        <button className="danger" onClick={() => remove(`/items/${item.id}`, "Item deleted.", `Delete “${item.name}” from the catalog?`)}>Delete</button>
      </li>)}</ul>}
    </div>
  </section>;
}
