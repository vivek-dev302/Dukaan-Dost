import React from "react";
import { useDashboard } from "../context/DashboardContext.jsx";
import PageHeader from "../components/PageHeader.jsx";
import VoiceCallButton from "../components/VoiceCallButton.jsx";

const suggestions = ["What is on my restocking list?", "Show today's khata entries"];

function readableLabel(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function AssistantPage() {
  const { chatMessages, chatInput, setChatInput, pendingConfirmation, chatBusy, chatError,
    sendChatMessage, decideChatAction } = useDashboard();

  return <section>
    <PageHeader eyebrow="A helping hand at the counter" title="Shop assistant" description="Ask about your shop or give a task. Changes to your records wait for your approval." />
    <div className="panel assistant-panel">
      <div className="assistant-heading">
        <span className="assistant-mark" aria-hidden="true">दु</span>
        <div><strong>Dukaan Dost</strong><span>Ready when you are</span></div>
        <span className="assistant-status"><i /> Online</span>
      </div>
      <div className="chat-messages" aria-live="polite" aria-relevant="additions text">
        {chatMessages.map((message, index) => <div key={index} className={`chat-message ${message.role}`}>
          <span className="message-author">{message.role === "user" ? "You" : "Dukaan Dost"}</span><p>{message.text}</p>
        </div>)}
        {chatBusy && <p className="working-indicator" role="status"><i /> Thinking through it…</p>}
      </div>
      {pendingConfirmation && <div className="confirmation-box">
        <span className="eyebrow">Your approval is needed</span><h3>Review this change</h3><p>{pendingConfirmation.message}</p>
        {pendingConfirmation.actions.map((action, index) => <div className="pending-action" key={index}>
          <strong>{readableLabel(action.tool || "Protected action")}</strong>
          <dl>{Object.entries(action.arguments || {}).filter(([, value]) => value != null).map(([key, value]) => <div key={key}>
            <dt>{readableLabel(key)}</dt><dd>{typeof value === "object" && value !== null ? JSON.stringify(value) : String(value)}</dd>
          </div>)}</dl>
        </div>)}
        <div className="inline-form">
          <button disabled={chatBusy} onClick={() => decideChatAction(true)}>{chatBusy ? "Saving…" : "Approve change"}</button>
          <button className="secondary" disabled={chatBusy} onClick={() => decideChatAction(false)}>Reject</button>
        </div>
      </div>}
      {chatError && <p className="chat-error" role="alert">{chatError}</p>}
      {chatMessages.length === 1 && !pendingConfirmation && <div className="suggestion-row" aria-label="Suggested questions">
        <span>Try asking</span>{suggestions.map((suggestion) => <button className="suggestion-chip" key={suggestion}
          onClick={() => setChatInput(suggestion)}>{suggestion}</button>)}
      </div>}
      <form className="chat-form" onSubmit={sendChatMessage}>
        <input aria-label="Message the shop assistant" value={chatInput}
          onChange={(event) => setChatInput(event.target.value)}
          placeholder="Write a message to your assistant…"
          disabled={chatBusy || Boolean(pendingConfirmation)} />
        <VoiceCallButton />
        <button aria-label="Send message" disabled={chatBusy || Boolean(pendingConfirmation) || !chatInput.trim()}><span>Send</span><span aria-hidden="true">↗</span></button>
      </form>
      <p className="assistant-footnote">Your shop data stays in your account. You’ll be asked before a protected change is made.</p>
    </div>
  </section>;
}
