import React from "react";
import "./VoiceVisualizer.css";

const BAR_WEIGHTS = [0.38, 0.62, 0.84, 1, 0.78, 0.56, 0.34];

export default function VoiceVisualizer({ mode, level = 0 }) {
  const amplitude = Math.min(1, Math.max(0, level));
  const labels = {
    speaking: "Dukaan Dost is speaking",
    listening: "Listening to you",
    processing: "Processing your request",
    idle: "Voice call is ready",
  };
  const label = labels[mode] || labels.idle;

  return <div className={`voice-visualizer voice-visualizer-${mode}`} role="img" aria-label={label}>
    {BAR_WEIGHTS.map((weight, index) => {
      const height = mode === "processing" ? 16 : 8 + amplitude * weight * 72;
      return <span key={index} style={{ height: `${height}%` }} />;
    })}
  </div>;
}
