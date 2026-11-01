import React from "react";

export default function PageHeader({ eyebrow, title, description, action }) {
  return <header className="page-heading">
    <div>
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
    {action && <div className="page-heading-action">{action}</div>}
  </header>;
}
