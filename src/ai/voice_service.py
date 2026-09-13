

from src.ai.stt_model import get_stt_model


def transcribe_audio(audio_path: str):
    return get_stt_model().transcribe(audio_path)
