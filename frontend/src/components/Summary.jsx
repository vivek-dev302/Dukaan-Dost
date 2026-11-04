import React from "react";

export default function Summary({ label, value, detail }) {
  return <article className="summary-card">
    <span className="summary-label">{label}</span>
    <strong>{value}</strong>
    {detail && <small>{detail}</small>}
  </article>;
}
