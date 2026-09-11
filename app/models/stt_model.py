from faster_whisper import WhisperModel


class STTModel:
    def __init__(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str):
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return {
            "text": text.strip(),
            "language": info.language,
            "language_probability": info.language_probability
        }


stt_model = None


def get_stt_model():
    global stt_model

    if stt_model is None:
        stt_model = STTModel()

    return stt_model
