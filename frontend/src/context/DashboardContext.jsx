import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { request, rupeesToPaise, today } from "../api/client.js";

const DashboardContext = createContext(null);

export function DashboardProvider({ children }) {
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [restock, setRestock] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [records, setRecords] = useState([]);
  const [initialLoading, setInitialLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [recordDate, setRecordDate] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [itemFilter, setItemFilter] = useState("all");
  const [restockFilter, setRestockFilter] = useState("all");
  const [itemName, setItemName] = useState("");
  const [itemCategory, setItemCategory] = useState("");
  const [restockName, setRestockName] = useState("");
  const [restockCategory, setRestockCategory] = useState("");
  const [newCustomer, setNewCustomer] = useState("");
  const [creditCustomer, setCreditCustomer] = useState("");
  const [creditAmount, setCreditAmount] = useState("");
  const [creditDescription, setCreditDescription] = useState("");
  const [creditDate, setCreditDate] = useState(today());
  const [editing, setEditing] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    { role: "assistant", text: "Hi! I can help manage your catalog, restocking list, customers, and khata." },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [pendingConfirmation, setPendingConfirmation] = useState(null);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState("");
  const firstRecordsEffect = useRef(true);

  const selectedCustomer = customers.find((customer) => customer.id === selectedCustomerId);
  const filteredItems = itemFilter === "all" ? items : items.filter((item) => item.category_id === Number(itemFilter));
  const filteredRestock = restockFilter === "all" ? restock : restock.filter((item) => item.category_id === Number(restockFilter));

  async function refreshData() {
    const [nextCategories, nextItems, nextRestock, nextCustomers] = await Promise.all([
      request("/categories"), request("/items"), request("/restock-items"), request("/customers"),
    ]);
    setCategories(nextCategories);
    setItems(nextItems);
    setRestock(nextRestock);
    setCustomers(nextCustomers);
    const defaultCategoryId = String(nextCategories.find((category) => category.name.toLowerCase() === "other")?.id || nextCategories[0]?.id || "");
    setItemCategory((current) => nextCategories.some((category) => String(category.id) === current) ? current : defaultCategoryId);
    setRestockCategory((current) => nextCategories.some((category) => String(category.id) === current) ? current : defaultCategoryId);
  }

  async function refreshRecords() {
    const params = new URLSearchParams();
    if (selectedCustomerId) params.set("customer_id", selectedCustomerId);
    if (recordDate) params.set("entry_date", recordDate);
    setRecords(await request(`/credit-records${params.size ? `?${params}` : ""}`));
  }

  useEffect(() => {
    Promise.all([refreshData(), refreshRecords()])
      .catch((reason) => setError(reason.message))
      .finally(() => setInitialLoading(false));
  }, []);
  useEffect(() => {
    if (firstRecordsEffect.current) {
      firstRecordsEffect.current = false;
      return;
    }
    refreshRecords().catch((reason) => setError(reason.message));
  }, [selectedCustomerId, recordDate]);

  async function perform(action, successMessage) {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      await action();
      await Promise.all([refreshData(), refreshRecords()]);
      setNotice(successMessage);
    } catch (reason) { setError(reason.message); }
    finally { setSaving(false); }
  }

  function addCategory(event) {
    event.preventDefault();
    perform(async () => {
      await request("/categories", { method: "POST", body: JSON.stringify({ name: categoryName }) });
      setCategoryName("");
    }, "Category added.");
  }

  function addCatalogItem(event) {
    event.preventDefault();
    perform(async () => {
      await request("/items", { method: "POST", body: JSON.stringify({ name: itemName, category_id: Number(itemCategory) }) });
      setItemName("");
    }, "Item added.");
  }

  function addRestockItem(event) {
    event.preventDefault();
    perform(async () => {
      await request("/restock-items", { method: "POST", body: JSON.stringify({ name: restockName, category_id: Number(restockCategory) }) });
      setRestockName("");
    }, "Added to the restock list.");
  }

  function addCustomer(event) {
    event.preventDefault();
    perform(async () => {
      const customer = await request("/customers", { method: "POST", body: JSON.stringify({ name: newCustomer }) });
      setNewCustomer("");
      setSelectedCustomerId(customer.id);
      setCreditCustomer(customer.name);
    }, "Customer added.");
  }

  function addCredit(event) {
    event.preventDefault();
    perform(async () => {
      await request("/credit-records", { method: "POST", body: JSON.stringify({
        customer: creditCustomer, amount_paise: rupeesToPaise(creditAmount), description: creditDescription, entry_date: creditDate || null,
      }) });
      setCreditAmount("");
      setCreditDescription("");
    }, "Credit entry added.");
  }

  function saveEdit(event) {
    event.preventDefault();
    perform(async () => {
      await request(`/credit-records/${editing.id}`, { method: "PATCH", body: JSON.stringify({
        customer: editing.customer, amount_paise: rupeesToPaise(editing.amount), entry_date: editing.entry_date, description: editing.description,
      }) });
      setEditing(null);
    }, "Credit entry updated.");
  }

  async function remove(path, successMessage, confirmText) {
    if (confirmText && !window.confirm(confirmText)) return;
    await perform(() => request(path, { method: "DELETE" }), successMessage);
  }

  function chooseCustomer(customer) {
    setSelectedCustomerId(customer.id);
    setCreditCustomer(customer.name);
    setRecordDate("");
  }

  async function sendChatMessage(eventOrMessage) {
    eventOrMessage?.preventDefault?.();
    const message = (typeof eventOrMessage === "string" ? eventOrMessage : chatInput).trim();
    if (!message || chatBusy || pendingConfirmation) return;
    setChatInput("");
    setChatError("");
    setChatMessages((current) => [...current, { role: "user", text: message }]);
    setChatBusy(true);
    try {
      const result = await request("/agent/chat", { method: "POST", body: JSON.stringify({ message }) });
      if (result.status === "confirmation_required") setPendingConfirmation(result);
      else setChatMessages((current) => [...current, { role: "assistant", text: result.reply }]);
    } catch (reason) { setChatError(reason.message); }
    finally { setChatBusy(false); }
  }

  async function sendVoiceCommand(audioFormData) {
    if (chatBusy || pendingConfirmation) return false;
    setChatInput("");
    setChatError("");
    setChatBusy(true);
    try {
      const result = await request("/speech/command", {
        method: "POST",
        body: audioFormData,
      });
      const transcript = result.transcript?.trim();
      if (!transcript) throw new Error("I could not make out the recording. Please try again.");

      if (result.status === "confirmation_required") {
        setChatMessages((current) => [...current, { role: "user", text: transcript, source: "voice" }]);
        setPendingConfirmation(result);
      } else if (result.status === "completed" && result.reply) {
        setChatMessages((current) => [
          ...current,
          { role: "user", text: transcript, source: "voice" },
          { role: "assistant", text: result.reply, source: "voice" },
        ]);
      } else {
        throw new Error("The assistant returned an unexpected response.");
      }
      return result;
    } catch (reason) {
      setChatError(reason.message);
      return null;
    } finally {
      setChatBusy(false);
    }
  }

  async function decideChatAction(approved, userUtterance = "", source = "chat") {
    if (!pendingConfirmation || chatBusy) return null;
    setChatBusy(true);
    setChatError("");
    if (userUtterance) {
      setChatMessages((current) => [...current, { role: "user", text: userUtterance, source }]);
    }
    try {
      const result = await request(`/agent/confirm/${pendingConfirmation.confirmation_id}`, {
        method: "POST", body: JSON.stringify({ approved }),
      });
      if (result.status === "confirmation_required") setPendingConfirmation(result);
      else {
        setPendingConfirmation(null);
        setChatMessages((current) => [...current, { role: "assistant", text: result.reply, source }]);
        if (approved) await Promise.all([refreshData(), refreshRecords()]);
      }
      return result;
    } catch (reason) {
      setChatError(reason.message);
      return null;
    } finally { setChatBusy(false); }
  }

  function addChatUserMessage(text, source = "chat") {
    setChatMessages((current) => [...current, { role: "user", text, source }]);
  }

  const value = {
    categories, items, restock, customers, records, initialLoading, saving, selectedCustomerId, setSelectedCustomerId, recordDate, setRecordDate,
    notice, error, setNotice, setError, categoryName, setCategoryName, itemFilter, setItemFilter, restockFilter, setRestockFilter,
    itemName, setItemName, itemCategory, setItemCategory, restockName, setRestockName, restockCategory, setRestockCategory,
    newCustomer, setNewCustomer, creditCustomer, setCreditCustomer, creditAmount, setCreditAmount,
    creditDescription, setCreditDescription, creditDate, setCreditDate, editing, setEditing, selectedCustomer,
    filteredItems, filteredRestock, addCategory, addCatalogItem, addRestockItem, addCustomer, addCredit, saveEdit,
    remove, chooseCustomer, chatMessages, chatInput, setChatInput, pendingConfirmation, chatBusy, chatError,
    sendChatMessage, sendVoiceCommand, decideChatAction, addChatUserMessage,
    refreshData, refreshRecords,
  };

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) throw new Error("useDashboard must be used inside DashboardProvider");
  return context;
}
