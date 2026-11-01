import React, { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const buttonRef = useRef(null);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const { loginWithGoogle } = useAuth();
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    let timer;
    let attempts = 0;
    function initialize() {
      if (window.google?.accounts?.id && buttonRef.current) {
        if (window.__dukaanDostGoogleClientId !== clientId) {
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: async ({ credential }) => {
              setError("");
              try { await loginWithGoogle(credential); }
              catch (reason) { setError(reason.message); }
            },
          });
          window.__dukaanDostGoogleClientId = clientId;
        }
        buttonRef.current.replaceChildren();
        window.google.accounts.id.renderButton(buttonRef.current, { theme: "outline", size: "large", text: "signin_with" });
        setReady(true);
        return;
      }
      attempts += 1;
      if (attempts < 100) timer = window.setTimeout(initialize, 100);
    }
    if (clientId) initialize();
    return () => window.clearTimeout(timer);
  }, [clientId, loginWithGoogle]);

  return <main className="login-screen">
    <div className="login-paper-rule" aria-hidden="true" />
    <section className="login-panel">
      <div className="brand-lockup login-brand">
        <span className="brand-mark" aria-hidden="true">दु</span>
        <div><h1>Dukaan Dost</h1><span className="brand-caption">Your shop, in order</span></div>
      </div>
      <span className="eyebrow">A simple book for busy shops</span>
      <h2>Keep the day in hand.</h2>
      <p>Sign in to manage your items, restocking list, and customer khata.</p>
      {!clientId ? <p className="chat-error">Set VITE_GOOGLE_CLIENT_ID in the frontend environment.</p> : <div className="google-button-wrap" ref={buttonRef} />}
      {clientId && !ready && <p className="muted-copy">Loading Google sign-in…</p>}
      {error && <p className="chat-error" role="alert">{error}</p>}
      <small className="login-note">Private to your shop. Sign in with Google to continue.</small>
    </section>
  </main>;
}
