import React from "react";
import { money } from "../api/client.js";

export default function CreditTable({ records, onEdit, onDelete, saving = false }) {
  if (!records.length) return <p className="empty-table">No credit entries to show.</p>;
  return <div className="table-scroll"><table className="credit-table" aria-label="Credit entries"><thead><tr><th>Date</th><th>Customer</th><th>Description</th><th className="amount-cell">Amount</th><th>Actions</th></tr></thead><tbody>
    {records.map((record) => <tr key={record.id}>
      <td className="date-cell">{record.entry_date}</td><td className="customer-cell">{record.customer}</td><td>{record.description || <span className="muted-dash">No note</span>}</td><td className="amount-cell">{money(record.amount_paise)}</td>
      <td className="actions"><button className="secondary" disabled={saving} onClick={() => onEdit({ ...record, amount: (record.amount_paise / 100).toFixed(2) })}>Edit</button>
        <button className="text-button danger" disabled={saving} onClick={() => onDelete(record.id)}>Delete</button></td>
    </tr>)}
  </tbody></table></div>;
}
