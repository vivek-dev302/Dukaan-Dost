import React from "react";
import { money } from "../api/client.js";

export default function CreditTable({ records, onEdit, onDelete }) {
  if (!records.length) return <p>No credit entries to show.</p>;
  return <div className="table-scroll"><table><thead><tr><th>Date</th><th>Customer</th><th>Description</th><th>Amount</th><th>Actions</th></tr></thead><tbody>
    {records.map((record) => <tr key={record.id}>
      <td>{record.entry_date}</td><td>{record.customer}</td><td>{record.description || "—"}</td><td>{money(record.amount_paise)}</td>
      <td className="actions"><button className="secondary" onClick={() => onEdit({ ...record, amount: (record.amount_paise / 100).toFixed(2) })}>Edit</button>
        <button className="danger" onClick={() => onDelete(record.id)}>Delete</button></td>
    </tr>)}
  </tbody></table></div>;
}
