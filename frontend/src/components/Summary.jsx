import React from "react";

export default function Summary({ label, value }) {
  return <div className="summary-card"><span>{label}</span><strong>{value}</strong></div>;
}
