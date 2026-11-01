import React, { createContext, useContext, useEffect, useState } from "react";
import { request } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    request("/auth/me")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function loginWithGoogle(credential) {
    const result = await request("/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    });
    setUser(result.user);
  }

  async function logout() {
    try { await request("/auth/logout", { method: "POST" }); }
    finally { setUser(null); }
  }

  return <AuthContext.Provider value={{ user, loading, loginWithGoogle, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
