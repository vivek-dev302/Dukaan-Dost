const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
  });
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`);
  return data;
}

export function money(paise = 0) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(paise / 100);
}

export function rupeesToPaise(value) {
  const match = String(value).trim().match(/^(\d+)(?:\.(\d{1,2}))?$/);
  if (!match) throw new Error("Enter an amount with up to two decimal places");
  return Number(match[1]) * 100 + Number((match[2] || "").padEnd(2, "0"));
}

export function today() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}
