import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";

export default function EditCreditModal() {
  const { editing, setEditing, saveEdit, saving } = useDashboard();
  if (!editing) return null;
  return <div className="modal-backdrop" role="presentation"><form className="panel edit-modal stack-form" onSubmit={saveEdit} role="dialog" aria-modal="true" aria-labelledby="edit-credit-title">
    <span className="eyebrow">Khata entry</span><h2 id="edit-credit-title">Edit credit entry</h2>
    <label>Customer<input required value={editing.customer} onChange={(event) => setEditing({ ...editing, customer: event.target.value })} /></label>
    <label>Amount in rupees<input required type="number" min="0.01" step="0.01" value={editing.amount} onChange={(event) => setEditing({ ...editing, amount: event.target.value })} /></label>
    <label>Date<input required type="date" value={editing.entry_date} onChange={(event) => setEditing({ ...editing, entry_date: event.target.value })} /></label>
    <label>Description<input value={editing.description} onChange={(event) => setEditing({ ...editing, description: event.target.value })} /></label>
    <div className="inline-form modal-actions"><button disabled={saving}>{saving ? "Saving…" : "Save changes"}</button><button type="button" className="secondary" disabled={saving} onClick={() => setEditing(null)}>Cancel</button></div>
  </form></div>;
}
