import React from "react";

export default function Summary({ label, value, detail, featured = false }) {
  return <article className={featured ? "summary-card summary-featured" : "summary-card"}>
    <span className="summary-label">{label}</span>
    <strong>{value}</strong>
    {detail && <small>{detail}</small>}
  </article>;
}
