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
    <div className="login-layout">
      <section className="login-story">
        <div className="brand-lockup login-brand login-brand-light">
          <span className="brand-mark" aria-hidden="true">दु</span>
          <div><h1>Dukaan Dost</h1><span className="brand-caption">Your shop, in order</span></div>
        </div>
        <div className="login-story-copy">
          <span className="login-kicker">A simple book for busy shops</span>
          <h2>Good days start with <em>things in order.</em></h2>
          <p>Your items, restocking list, and customer khata—together in one quiet place.</p>
        </div>
        <div className="login-illustration" aria-hidden="true">
          <svg viewBox="0 0 720 440" role="presentation">
            <path className="art-halo" d="M130 367V183c0-103 81-174 203-174s203 71 203 174v184" />
            <path className="art-ground" d="M48 367h598" />
            <path className="art-shop" d="M128 198h408v169H128z" />
            <path className="art-awning" d="M105 193 151 91h363l47 102z" />
            <path className="art-awning-line" d="m105 193 46-102h55l-22 102zm102 0 22-102h56v102zm111 0V91h56l11 102zm112 0-11-102h57l46 102z" />
            <path className="art-window" d="M158 222h142v111H158z" />
            <path className="art-window-line" d="M229 222v111m-71-55h142" />
            <path className="art-counter" d="M330 263h177v104H330z" />
            <path className="art-counter-top" d="M315 252h207v20H315z" />
            <path className="art-shelf" d="M351 222h134m-134 34h134" />
            <path className="art-jar" d="M365 194h33l5 28h-43zm54-8h31l8 36h-47zm59 14h28l4 22h-36z" />
            <path className="art-ledger" d="M450 287h39v59h-39z" />
            <path className="art-ledger-line" d="M458 300h22m-22 9h22m-22 9h17" />
            <path className="art-plant" d="M564 367v-67m0 25c-24-2-30-17-31-31 18 1 29 10 31 27m0-9c1-21 12-33 31-36-1 17-9 30-31 37m-12 54h26l-4-18h-18z" />
            <circle className="art-sun" cx="570" cy="110" r="26" />
            <path className="art-spark" d="M605 158v24m-12-12h24M90 260v20m-10-10h20" />
          </svg>
        </div>
        <div className="login-story-footer"><span>Made for the everyday rhythm of your shop</span><span>01 / Your shop book</span></div>
      </section>
      <section className="login-access">
        <div className="login-panel">
          <span className="eyebrow">Welcome back</span>
          <h2>Open your shop book.</h2>
          <p>Sign in to pick up right where your day left off.</p>
          {!clientId ? <p className="chat-error">Set VITE_GOOGLE_CLIENT_ID in the frontend environment.</p> : <div className="google-button-wrap" ref={buttonRef} />}
          {clientId && !ready && <p className="muted-copy">Loading Google sign-in…</p>}
          {error && <p className="chat-error" role="alert">{error}</p>}
          <small className="login-note">Private to your shop. Sign in with Google to continue.</small>
        </div>
      </section>
    </div>
  </main>;
}
