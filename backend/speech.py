# backend/speech.py

import io
import os
import re
import subprocess

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sarvamai import SarvamAI
from starlette.concurrency import run_in_threadpool

from .agent import resolve_agent_confirmation, run_agent_message
from .auth.dependencies import get_current_user

router = APIRouter(prefix="/speech", tags=["speech"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
TTS_SPEAKER = "shubh_enhi_ads"

AFFIRMATIVE_WORDS = {
    "yes", "yeah", "yep", "yup", "sure", "absolutely", "definitely", "right",
    "haan", "han", "ha", "haanji", "hanji", "jee", "ji", "bilkul",
    "approve", "approved", "confirm", "confirmed", "okay", "ok", "please",
    "do", "it", "this", "that", "go", "ahead", "and", "proceed", "continue",
    "now", "change", "action", "clear", "empty", "all", "whole", "entire",
    "list", "restock", "restocking", "record", "records", "khata", "customer",
    "category", "entry", "payment", "delete", "remove", "add", "update", "i",
    "kar", "karo", "kardo", "karna", "dijiye", "kijiye", "de", "den", "dena",
    "aap", "thats", "is", "fine", "हाँ",
    "हां", "हाँजी", "हांजी", "जी",
}
AFFIRMATIVE_ANCHORS = {
    "yes", "yeah", "yep", "yup", "sure", "absolutely", "definitely", "right",
    "haan", "han", "ha", "haanji", "hanji", "bilkul", "approve", "approved",
    "confirm", "confirmed", "okay", "ok", "fine", "proceed", "continue", "karo",
    "kardo", "हाँ", "हां", "हाँजी", "हांजी",
}
NEGATIVE_WORDS = {
    "no", "nope", "nah", "nahi", "nahin", "na", "cancel", "reject", "decline",
    "mat", "dont", "do", "not", "please", "it", "this", "that", "go", "ahead",
    "and", "now", "clear", "empty", "all", "whole", "entire", "list", "restock",
    "restocking", "record", "records", "khata", "customer", "category", "entry",
    "payment", "delete", "remove", "add", "update", "approve", "confirm", "karo",
    "kar", "kardo", "karna", "dijiye", "kijiye", "de", "den", "dena", "stop",
    "जी", "नहीं", "नही", "ना",
}
NEGATIVE_ANCHORS = {
    "no", "nope", "nah", "nahi", "nahin", "na", "cancel", "reject", "decline",
    "mat", "dont", "not", "stop", "नहीं", "नही", "ना",
}
END_CALL_PATTERN = re.compile(
    r"\b(?:exit|quit|hang\s+up|end\s+(?:the\s+)?call|stop\s+(?:the\s+)?call|"
    r"close\s+(?:the\s+)?call|cut\s+(?:the\s+)?call|call\s+(?:cut|kaat|band|khatam|end|stop)|"
    r"call\s+(?:ko\s+)?(?:band|khatam)\s+(?:kar|karo|kardo|do|dijiye))\b"
)


def get_sarvam_client() -> SarvamAI:
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Speech service is not configured")
    return SarvamAI(api_subscription_key=api_key)


def convert_to_wav(audio_bytes: bytes) -> io.BytesIO:
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-i", "pipe:0",
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                "-f", "wav",
                "pipe:1",
            ],
            input=audio_bytes,
            capture_output=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read this recording. Please try recording again.",
        ) from exc

    wav_file = io.BytesIO(result.stdout)
    wav_file.name = "recording.wav"
    return wav_file


def _transcribe_audio_bytes(audio_bytes: bytes) -> dict[str, str]:
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio recording is empty")
    if len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Audio recording is too large")

    wav_file = convert_to_wav(audio_bytes)

    try:
        result = get_sarvam_client().speech_to_text.transcribe(
            file=wav_file,
            model="saaras:v4",
            mode="translit",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Speech recognition failed. Please try again.",
        ) from exc

    return {
        "text": result.transcript,
        "language_code": result.language_code,
    }


def _approval_decision(transcript: str) -> bool | None:
    normalized = transcript.lower().replace("don't", "dont").replace("don’t", "dont")
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    words = normalized.split()
    if not words or len(words) > 12:
        return None
    word_set = set(words)
    has_affirmative_anchor = bool(word_set & AFFIRMATIVE_ANCHORS) or {"go", "ahead"} <= word_set or {"do", "it"} <= word_set or {"kar", "do"} <= word_set or {"kar", "dijiye"} <= word_set
    if word_set <= AFFIRMATIVE_WORDS and has_affirmative_anchor:
        return True
    if word_set <= NEGATIVE_WORDS and word_set & NEGATIVE_ANCHORS:
        return False
    return None


def _is_end_call_request(transcript: str) -> bool:
    normalized = transcript.lower().replace("don't", "dont").replace("don’t", "dont")
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    if re.search(r"\b(?:dont|do\s+not|never|not|mat)\b", normalized):
        return False
    return bool(END_CALL_PATTERN.search(normalized))


@router.post("/transcribe")
def transcribe_audio(
    audio: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    return _transcribe_audio_bytes(audio.file.read(MAX_UPLOAD_BYTES + 1))


@router.post("/confirm/{confirmation_id}")
async def voice_confirmation(
    confirmation_id: str,
    request: Request,
    audio: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    audio_bytes = await audio.read(MAX_UPLOAD_BYTES + 1)
    transcription = await run_in_threadpool(_transcribe_audio_bytes, audio_bytes)
    transcript = (transcription.get("text") or "").strip()
    if _is_end_call_request(transcript):
        return {"status": "end_call", "transcript": transcript}
    decision = _approval_decision(transcript)
    if decision is None:
        return {"status": "unclear", "transcript": transcript}

    result = await resolve_agent_confirmation(confirmation_id, decision, request, user)
    return {"transcript": transcript, "approved": decision, **result}


@router.post("/command")
async def voice_command(
    request: Request,
    audio: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    audio_bytes = await audio.read(MAX_UPLOAD_BYTES + 1)
    transcription = await run_in_threadpool(_transcribe_audio_bytes, audio_bytes)
    transcript = (transcription.get("text") or "").strip()
    if not transcript:
        raise HTTPException(status_code=422, detail="No speech could be recognized. Please try again.")
    if _is_end_call_request(transcript):
        return {"status": "end_call", "transcript": transcript}
    agent_result = await run_agent_message(transcript, request, user)
    return {
        "transcript": transcript,
        "language_code": transcription["language_code"],
        **agent_result,
    }


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2500)
    language_code: str = "en-IN"


@router.post("/speak")
def speak_text(
    data: SpeechRequest,
    user: dict = Depends(get_current_user),
):
    if data.language_code not in {"en-IN", "hi-IN"}:
        raise HTTPException(status_code=400, detail="Unsupported speech language")

    try:
        audio_chunks = get_sarvam_client().text_to_speech.convert_stream(
            text=data.text,
            language_code=data.language_code,
            model="bulbul:v4-flash",
            speaker=TTS_SPEAKER,
            output_audio_codec="mp3",
            enable_preprocessing=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Speech generation failed. Please try again.",
        ) from exc

    return StreamingResponse(audio_chunks, media_type="audio/mpeg")
