import React, { useEffect, useRef, useState } from "react";
import { request } from "../api/client.js";

const PAGE_SIZE = 100;

function displayTime(value) {
  return new Date(`${value.replace(" ", "T")}Z`).toLocaleString();
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

  return <section>
    <div className="section-heading">
      <h2>Agent activity</h2>
      <button className="secondary" disabled={loading} onClick={() => loadMore(0)}>Refresh</button>
    </div>
    <p>Changes made by the assistant are listed here.</p>
    {error && <p role="alert">{error}</p>}
    {!logs.length && !loading && !error && <p>No agent actions have been recorded yet.</p>}
    {!!logs.length && <div className="table-scroll"><table>
      <thead><tr><th>Time</th><th>Action</th><th>Details</th></tr></thead>
      <tbody>{logs.map((log) => <tr key={log.id}>
        <td>{displayTime(log.created_at)}</td><td>{log.action.replaceAll("_", " ").replaceAll(".", " · ")}</td><td>{log.description}</td>
      </tr>)}</tbody>
    </table></div>}
    {hasMore && <button className="secondary" disabled={loading} onClick={loadMore}>
      {loading ? "Loading…" : "Load more"}
    </button>}
  </section>;
}
