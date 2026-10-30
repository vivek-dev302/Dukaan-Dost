import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";

export default function AssistantPage() {
  const { chatMessages, chatInput, setChatInput, pendingConfirmation, chatBusy, chatError,
    sendChatMessage, decideChatAction } = useDashboard();
  return <section>
    <h2>Shop assistant</h2>
    <div className="panel chat-panel">
      <div className="chat-messages" aria-live="polite">
        {chatMessages.map((message, index) => <div key={index} className={`chat-message ${message.role}`}>
          <strong>{message.role === "user" ? "You" : "Assistant"}</strong><p>{message.text}</p>
        </div>)}
        {chatBusy && <p role="status">Working…</p>}
      </div>
      {pendingConfirmation && <div className="confirmation-box">
        <h3>Confirm this action</h3><p>{pendingConfirmation.message}</p>
        {pendingConfirmation.actions.map((action, index) => <div className="pending-action" key={index}>
          <strong>{action.tool}</strong><pre>{JSON.stringify(action.arguments, null, 2)}</pre>
        </div>)}
        <div className="inline-form">
          <button disabled={chatBusy} onClick={() => decideChatAction(true)}>Approve</button>
          <button className="secondary" disabled={chatBusy} onClick={() => decideChatAction(false)}>Reject</button>
        </div>
      </div>}
      {chatError && <p className="chat-error" role="alert">{chatError}</p>}
      <form className="chat-form" onSubmit={sendChatMessage}>
        <input aria-label="Message the shop assistant" value={chatInput}
          onChange={(event) => setChatInput(event.target.value)}
          placeholder="Ask about your shop or request an action…"
          disabled={chatBusy || Boolean(pendingConfirmation)} />
        <button disabled={chatBusy || Boolean(pendingConfirmation) || !chatInput.trim()}>Send</button>
      </form>
    </div>
  </section>;
}
