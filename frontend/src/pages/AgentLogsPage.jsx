import React, { useEffect, useRef, useState } from "react";
import { request } from "../api/client.js";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";

const PAGE_SIZE = 100;

function displayTime(value) {
  const timestamp = value.trim().replace(" ", "T");
  const hasTimezone = /(?:Z|[+-]\d{2}(?::?\d{2})?)$/i.test(timestamp);
  const isoTimestamp = timestamp
    .replace(/([+-]\d{2})(\d{2})$/, "$1:$2")
    .replace(/([+-]\d{2})$/, "$1:00");
  const parsed = new Date(hasTimezone ? isoTimestamp : `${isoTimestamp}Z`);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function AgentLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasMore, setHasMore] = useState(true);
  const initialLoadStarted = useRef(false);

  async function loadMore(offset = logs.length) {
    setLoading(true);
    setError("");
    try {
      const next = await request(`/agent-logs?limit=${PAGE_SIZE}&offset=${offset}`);
      setLogs((current) => offset === 0 ? next : [...current, ...next]);
      setHasMore(next.length === PAGE_SIZE);
    } catch (reason) {
      setError(reason.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!initialLoadStarted.current) {
      initialLoadStarted.current = true;
      loadMore(0);
    }
  }, []);

  return <section className="agent-logs-page">
    <PageHeader eyebrow="A record of changes" title="Agent activity" description="Review the updates your assistant has made to the shop's records."
      action={<button className="secondary" disabled={loading} onClick={() => loadMore(0)}>Refresh</button>} />
    {error && <p role="alert">{error}</p>}
    {!logs.length && loading && <div className="loading-line" role="status">Loading activity…</div>}
    {!logs.length && !loading && !error && <EmptyState title="No activity yet" description="When the assistant changes a shop record, it will be noted here." />}
    {!!logs.length && <div className="panel ledger-panel activity-panel"><div className="table-scroll"><table className="activity-table">
      <thead><tr><th>When</th><th>Action</th><th>What changed</th></tr></thead>
      <tbody>{logs.map((log) => <tr key={log.id}>
        <td data-label="When">{displayTime(log.created_at)}</td><td data-label="Action">{log.action.replaceAll("_", " ").replaceAll(".", " · ")}</td><td data-label="What changed">{log.description}</td>
      </tr>)}</tbody>
    </table></div></div>}
    {hasMore && !!logs.length && <button className="secondary load-more" disabled={loading} onClick={loadMore}>
      {loading ? "Loading…" : "Load more"}
    </button>}
  </section>;
}
