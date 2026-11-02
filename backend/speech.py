# backend/speech.py

import io
import os
import subprocess

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sarvamai import SarvamAI
from starlette.concurrency import run_in_threadpool

from .agent import run_agent_message
from .auth.dependencies import get_current_user

router = APIRouter(prefix="/speech", tags=["speech"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
TTS_SPEAKER = "shubh_enhi_ads"


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


@router.post("/transcribe")
def transcribe_audio(
    audio: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    return _transcribe_audio_bytes(audio.file.read(MAX_UPLOAD_BYTES + 1))


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
