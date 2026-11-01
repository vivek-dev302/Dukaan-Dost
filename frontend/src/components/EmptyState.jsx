import React from "react";

export default function EmptyState({ title, description }) {
  return <div className="empty-state">
    <span className="empty-mark" aria-hidden="true"><i /><i /><i /></span>
    <div><strong>{title}</strong>{description && <p>{description}</p>}</div>
  </div>;
}
