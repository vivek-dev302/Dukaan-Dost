import React, { useEffect, useRef, useState } from "react";
import { requestAudio } from "../api/client.js";
import VoiceVisualizer from "./VoiceVisualizer.jsx";
import { useDashboard } from "../context/DashboardContext.jsx";

const SILENCE_RMS_THRESHOLD = 0.025;
const SILENCE_DURATION_MS = 2000;
const MAX_RECORDING_MS = 15000;

const APPROVAL_TEMPLATES = [
  "मैं ये change करने जा रहा हूँ: {action}. Approve करने के लिए हाँ जी कहें, cancel करने के लिए नहीं कहें.",
  "एक बार confirm कर दीजिए: {action}. अगर ठीक है तो हाँ जी बोलें, नहीं तो नहीं बोलें.",
  "आपके कहने पर मैं {action} करूँगा. आगे बढ़ने के लिए हाँ जी कहें, रोकने के लिए नहीं कहें.",
  "ये action है: {action}. क्या मैं इसे कर दूँ? हाँ जी बोलकर approve करें, या नहीं बोलकर cancel करें.",
  "मैं अभी {action} करने वाला हूँ. मंज़ूरी के लिए हाँ जी बोलें, मना करने के लिए नहीं बोलें.",
];
const UNCLEAR_TEMPLATES = [
  "माफ़ कीजिए, {heard} ठीक से समझ नहीं आया. Approve के लिए हाँ जी, cancel के लिए नहीं कहें.",
  "आपने {heard} कहा. आपका जवाब clear नहीं हुआ. क्या मैं action करूँ? हाँ जी या नहीं कहें.",
  "मुझे आपका जवाब पक्का समझ नहीं आया. Approve करना है तो हाँ जी, cancel करना है तो नहीं कहें.",
  "एक बार फिर बताइए, {heard} से आपका मतलब हाँ है या नहीं? सिर्फ हाँ जी या नहीं कहें.",
  "मैं अभी action रोककर इंतज़ार कर रहा हूँ. आगे बढ़ने के लिए हाँ जी कहें, मना करने के लिए नहीं.",
];
const RETRY_TEMPLATES = [
  "माफ़ कीजिए, {issue}. चलिए, एक बार फिर कोशिश करते हैं.",
  "थोड़ी दिक्कत आई: {issue}. आप तैयार हों तो फिर से बोलिए, मैं सुन रहा हूँ.",
  "अभी {issue}. कोई बात नहीं, दोबारा कहिए.",
  "आपकी बात पूरी नहीं हो पाई क्योंकि {issue}. चलिए फिर से try करते हैं.",
  "एक छोटी सी दिक्कत हुई: {issue}. मैं फिर से सुनने के लिए तैयार हूँ.",
];
const END_CALL_TEMPLATES = [
  "ठीक है, call यहीं खत्म करते हैं. {pending} फिर मिलेंगे.",
  "समझ गया, अभी call बंद कर रहा हूँ. {pending} धन्यवाद.",
  "बिल्कुल, Dukaan Dost call अब बंद कर रहा है. {pending} फिर बात करेंगे.",
  "ठीक है, यहीं रुकते हैं. {pending} आपका दिन अच्छा रहे.",
  "आपकी बात समझ गया, call खत्म कर रहा हूँ. {pending} अलविदा.",
];

function randomTemplate(templates, values = {}) {
  const template = templates[Math.floor(Math.random() * templates.length)];
  return template.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? "").replace(/\s+/g, " ").trim();
}

function endCallGoodbye(hasPendingApproval) {
  return randomTemplate(END_CALL_TEMPLATES, {
    pending: hasPendingApproval ? "आपका pending action dashboard पर रहेगा." : "",
  });
}

function summarizeAction({ tool = "protected action", arguments: args = {} }) {
  const amount = args.amount_rupees == null ? "" : `₹${Number(args.amount_rupees).toLocaleString("en-IN")}`;
  const details = Object.entries(args)
    .filter(([key]) => key !== "amount_rupees")
    .map(([key, value]) => `${key.replaceAll("_", " ")}: ${String(value)}`)
    .join(", ");

  switch (tool) {
    case "add_credit_record":
      return `${args.customer || "customer"} ke khata mein ${amount} add karna${args.description ? `, ${args.description} ke liye` : ""}`;
    case "update_credit_record":
      return `khata record ${args.record_id} update karna${details ? ` (${details})` : ""}`;
    case "delete_credit_record":
      return `khata record ${args.record_id} delete karna`;
    case "clear_customer_credit_records":
      return `${args.customer_name || "customer"} ke saare khata records clear karna`;
    case "delete_category":
      return `category ${args.category_id} delete karna`;
    case "delete_catalog_item":
      return `catalog item ${args.item_id} delete karna`;
    case "remove_restock_item":
      return `restock item ${args.item_id} list se remove karna`;
    case "clear_restock_list":
      return "poori restocking list clear karna";
    default:
      return `${tool.replaceAll("_", " ")}${details ? ` (${details})` : ""}`;
  }
}

function approvalPrompt(pending) {
  const actions = (pending.actions || []).map(summarizeAction);
  const summary = actions.length ? actions.join("; और ") : "यह change";
  return randomTemplate(APPROVAL_TEMPLATES, { action: summary });
}

export default function VoiceCallButton({ prominent = false }) {
  const {
    pendingConfirmation,
    chatBusy,
    sendVoiceCommand,
    sendVoiceApproval,
  } = useDashboard();
  const [open, setOpen] = useState(false);
  const [phase, setPhase] = useState("closed");
  const [error, setError] = useState("");
  const [lastTranscript, setLastTranscript] = useState("");
  const [audioLevel, setAudioLevel] = useState(0);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const playbackContextRef = useRef(null);
  const playbackAnalyserRef = useRef(null);
  const playbackSourceRef = useRef(null);
  const playbackFrameRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const maxTimerRef = useRef(null);
  const audioRef = useRef(null);
  const audioUrlRef = useRef(null);
  const callOpenRef = useRef(false);
  const sendingRef = useRef(false);
  const modeRef = useRef("command");
  const pendingConfirmationRef = useRef(pendingConfirmation);
  pendingConfirmationRef.current = pendingConfirmation;

  function stopRecording() {
    if (silenceTimerRef.current) window.clearInterval(silenceTimerRef.current);
    if (maxTimerRef.current) window.clearTimeout(maxTimerRef.current);
    silenceTimerRef.current = null;
    maxTimerRef.current = null;
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    recorderRef.current = null;
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
    }
    audioContextRef.current = null;
    setAudioLevel(0);
  }

  function stopSpeech() {
    if (playbackFrameRef.current) cancelAnimationFrame(playbackFrameRef.current);
    playbackFrameRef.current = null;
    playbackSourceRef.current?.disconnect();
    playbackAnalyserRef.current?.disconnect();
    playbackSourceRef.current = null;
    playbackAnalyserRef.current = null;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    audioUrlRef.current = null;
    setAudioLevel(0);
  }

  function endCall() {
    callOpenRef.current = false;
    stopRecording();
    stopSpeech();
    playbackContextRef.current?.close().catch(() => {});
    playbackContextRef.current = null;
    setOpen(false);
    setPhase("closed");
    setError("");
  }

  async function speak(text) {
    setPhase("preparing_speech");
    try {
      const hasHindiScript = /[\u0900-\u097F]/.test(text);
      const blob = await requestAudio("/speech/speak", {
        text,
        language_code: hasHindiScript ? "hi-IN" : "en-IN",
      });
      if (!callOpenRef.current) return false;
      stopSpeech();
      const url = URL.createObjectURL(blob);
      const player = new Audio(url);
      audioUrlRef.current = url;
      audioRef.current = player;
      const playbackContext = playbackContextRef.current;
      try {
        if (playbackContext) {
          const analyser = playbackContext.createAnalyser();
          analyser.fftSize = 256;
          const source = playbackContext.createMediaElementSource(player);
          source.connect(analyser);
          analyser.connect(playbackContext.destination);
          playbackAnalyserRef.current = analyser;
          playbackSourceRef.current = source;
          const samples = new Uint8Array(analyser.fftSize);
          const updateLevel = () => {
            if (playbackAnalyserRef.current !== analyser) return;
            analyser.getByteTimeDomainData(samples);
            let energy = 0;
            for (const sample of samples) {
              const normalized = (sample - 128) / 128;
              energy += normalized * normalized;
            }
            setAudioLevel(Math.min(1, Math.sqrt(energy / samples.length) * 7));
            playbackFrameRef.current = requestAnimationFrame(updateLevel);
          };
          playbackFrameRef.current = requestAnimationFrame(updateLevel);
          await playbackContext.resume();
        }
      } catch {
        playbackSourceRef.current?.disconnect();
        playbackAnalyserRef.current?.disconnect();
        playbackSourceRef.current = null;
        playbackAnalyserRef.current = null;
      }
      return await new Promise((resolve) => {
        const finish = (played) => {
          if (audioUrlRef.current === url) {
            if (playbackFrameRef.current) cancelAnimationFrame(playbackFrameRef.current);
            playbackFrameRef.current = null;
            playbackSourceRef.current?.disconnect();
            playbackAnalyserRef.current?.disconnect();
            playbackSourceRef.current = null;
            playbackAnalyserRef.current = null;
            URL.revokeObjectURL(url);
            audioUrlRef.current = null;
            audioRef.current = null;
            setAudioLevel(0);
          }
          resolve(played);
        };
        player.onended = () => finish(true);
        player.onerror = () => finish(false);
        setPhase("speaking");
        player.play().catch(() => finish(false));
      });
    } catch {
      stopSpeech();
      return false;
    }
  }

  async function speakAndListen(text, mode) {
    modeRef.current = mode;
    const played = await speak(text);
    if (!callOpenRef.current) return;
    if (!played) {
      setError("Voice playback failed. Listening will continue.");
    }
    await startRecording(mode);
  }

  async function recoverAndListen(issue, mode, values = {}) {
    await speakAndListen(randomTemplate(RETRY_TEMPLATES, { issue, ...values }), mode);
  }

  async function askForApproval(pending) {
    await speakAndListen(approvalPrompt(pending), "approval");
  }

  async function startRecording(mode) {
    if (!callOpenRef.current) return;
    stopRecording();
    setError("");
    modeRef.current = mode;
    setPhase(mode === "approval" ? "approval_listening" : "listening");
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        throw new Error("Audio recording is not supported in this browser.");
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!callOpenRef.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) throw new Error("Audio level detection is not supported in this browser.");
      const audioContext = new AudioContextClass();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      audioContext.createMediaStreamSource(stream).connect(analyser);
      await audioContext.resume();

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "";
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunksRef.current.push(event.data);
      };
      recorder.start();
      recorderRef.current = recorder;

      const samples = new Uint8Array(analyser.fftSize);
      let speechDetected = false;
      let silenceStartedAt = null;
      silenceTimerRef.current = window.setInterval(() => {
        if (recorder.state !== "recording" || sendingRef.current) return;
        analyser.getByteTimeDomainData(samples);
        let energy = 0;
        for (const sample of samples) {
          const normalized = (sample - 128) / 128;
          energy += normalized * normalized;
        }
        const rms = Math.sqrt(energy / samples.length);
        setAudioLevel(Math.min(1, rms * 7));
        if (rms >= SILENCE_RMS_THRESHOLD) {
          speechDetected = true;
          silenceStartedAt = null;
        } else if (speechDetected) {
          silenceStartedAt ??= Date.now();
          if (Date.now() - silenceStartedAt >= SILENCE_DURATION_MS) void sendRecording(mode);
        }
      }, 100);
      maxTimerRef.current = window.setTimeout(() => {
        if (speechDetected) void sendRecording(mode);
        else {
          stopRecording();
          void recoverAndListen("आवाज़ सुनाई नहीं दी", mode);
        }
      }, MAX_RECORDING_MS);
    } catch (reason) {
      stopRecording();
      setPhase("error");
      setError(reason.message || "Could not start microphone recording.");
      const message = randomTemplate(RETRY_TEMPLATES, {
        issue: "माइक access नहीं मिला. Browser settings में microphone permission allow करके call फिर से शुरू करें",
      });
      await speak(message);
      if (callOpenRef.current) setPhase("error");
    }
  }

  async function submitCommand(formData) {
    setPhase("sending");
    const result = await sendVoiceCommand(formData);
    if (!callOpenRef.current) return;
    if (!result) {
      await recoverAndListen("आपकी बात process नहीं हो पाई", "command");
      return;
    }
    setLastTranscript(result.transcript);
    if (result.status === "end_call") {
      await speak(endCallGoodbye(Boolean(pendingConfirmationRef.current)));
      endCall();
      return;
    }
    if (result.status === "confirmation_required") {
      pendingConfirmationRef.current = result;
      await askForApproval(result);
    } else {
      await speakAndListen(result.reply, "command");
    }
  }

  async function submitApproval(formData) {
    setPhase("checking_approval");
    const confirmationId = pendingConfirmationRef.current?.confirmation_id;
    const result = await sendVoiceApproval(formData, confirmationId);
    if (!callOpenRef.current) return;
    if (result?.status === "confirmation_required") pendingConfirmationRef.current = result;
    else if (result && result.status !== "unclear" && result.status !== "end_call") pendingConfirmationRef.current = null;
    if (result?.transcript) setLastTranscript(result.transcript);
    if (result?.status === "end_call") {
      await speak(endCallGoodbye(true));
      endCall();
      return;
    }
    if (result?.status === "unclear") {
      await speakAndListen(randomTemplate(UNCLEAR_TEMPLATES, { heard: result.transcript || "आपका जवाब" }), "approval");
      return;
    }
    if (!result) {
      await recoverAndListen("आपका approval save नहीं हो पाया", pendingConfirmation ? "approval" : "command");
    } else if (result.status === "expired" || result.status === "missing_confirmation") {
      await speakAndListen("यह confirmation expire हो गया है. कृपया अपना request फिर से बताइए.", "command");
    } else if (result.status === "confirmation_required") {
      await askForApproval(result);
    } else {
      await speakAndListen(result.reply, "command");
    }
  }

  async function sendRecording(mode = modeRef.current) {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state !== "recording" || sendingRef.current) return;
    sendingRef.current = true;
    if (silenceTimerRef.current) window.clearInterval(silenceTimerRef.current);
    if (maxTimerRef.current) window.clearTimeout(maxTimerRef.current);
    silenceTimerRef.current = null;
    maxTimerRef.current = null;
    try {
      const blob = await new Promise((resolve) => {
        recorder.onstop = () => resolve(new Blob(chunksRef.current, { type: recorder.mimeType }));
        recorder.stop();
      });
      stopRecording();
      if (!blob.size) throw new Error("No audio was recorded.");
      const formData = new FormData();
      formData.append("audio", blob, blob.type.includes("webm") ? "recording.webm" : "recording.mp4");
      if (mode === "approval") await submitApproval(formData);
      else await submitCommand(formData);
    } catch {
      if (callOpenRef.current) {
        const issue = mode === "approval" ? "आपका जवाब process नहीं हो पाया" : "आपकी बात process नहीं हो पाई";
        await recoverAndListen(issue, mode);
      }
    } finally {
      sendingRef.current = false;
    }
  }

  async function beginCall() {
    callOpenRef.current = true;
    setOpen(true);
    setLastTranscript("");
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      playbackContextRef.current ??= new AudioContextClass();
      await playbackContextRef.current.resume().catch(() => {});
    }
    if (pendingConfirmation) await askForApproval(pendingConfirmation);
    else await startRecording("command");
  }

  useEffect(() => () => {
    callOpenRef.current = false;
    stopRecording();
    stopSpeech();
    playbackContextRef.current?.close().catch(() => {});
    playbackContextRef.current = null;
  }, []);

  const phaseText = {
    listening: "Listening. I’ll send after 2 seconds of silence, or tap Send now.",
    approval_listening: "Say yes to approve or no to cancel. You can also use the chat buttons.",
    sending: "Sending your command…",
    checking_approval: "Checking your answer…",
    preparing_speech: "Dukaan Dost is preparing a reply…",
    speaking: "Dukaan Dost is speaking…",
    error,
  }[phase];
  const visualizerMode = phase === "speaking" ? "speaking"
    : phase === "listening" || phase === "approval_listening" ? "listening"
    : phase === "sending" || phase === "checking_approval" || phase === "preparing_speech" ? "processing"
    : "idle";

  return <>
    <button className={prominent ? "voice-launch-button" : "secondary mic-button"} type="button" aria-label="Start voice call"
      title="Start voice call" disabled={chatBusy} onClick={beginCall}>
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="2.5" width="6" height="12" rx="3" /><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.5M8.5 21.5h7" /></svg>
      {prominent && <><span>Talk to your assistant</span><span className="voice-launch-hint">Start a voice call</span></>}
    </button>
    {open && <div className="voice-overlay">
      <section className="voice-dialog" role="dialog" aria-modal="true" aria-labelledby="voice-call-title">
        <button className="text-button voice-close" type="button" aria-label="End voice call" onClick={endCall}>×</button>
        <VoiceVisualizer mode={visualizerMode} level={audioLevel} />
        <h2 id="voice-call-title">Dukaan Dost voice call</h2>
        <p className="voice-help" role="status">{phaseText}</p>
        {lastTranscript && <p className="voice-transcript">Heard: {lastTranscript}</p>}
        {error && <p className="chat-error voice-error" role="alert">{error}</p>}
        <div className="voice-actions">
          {(phase === "listening" || phase === "approval_listening") && <button type="button" onClick={() => sendRecording(modeRef.current)}>
            {phase === "approval_listening" ? "Send answer" : "Send now"}
          </button>}
          <button className="secondary" type="button" onClick={endCall}>End call</button>
        </div>
      </section>
    </div>}
  </>;
}
