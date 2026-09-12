"""
app/core/state.py
=================
Thread-safe session state cache for the KalaConnect AI Pipeline.
Automatically captures the latest Vision analysis and Voice transcription,
so that the Price Prediction model can extract them automatically without manual copy-pasting.
"""

import threading
from typing import Any, Dict, Optional


class PipelineState:
    def __init__(self):
        self._lock = threading.Lock()
        self.latest_vision: Optional[Dict[str, Any]] = None
        self.latest_voice: Optional[Dict[str, Any]] = None

    def set_vision(self, data: Dict[str, Any]):
        with self._lock:
            self.latest_vision = data

    def get_vision(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return dict(self.latest_vision) if self.latest_vision else None

    def set_voice(self, data: Dict[str, Any]):
        with self._lock:
            self.latest_voice = data

    def get_voice(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return dict(self.latest_voice) if self.latest_voice else None

    def get_combined_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "vision": dict(self.latest_vision) if self.latest_vision else None,
                "voice": dict(self.latest_voice) if self.latest_voice else None,
            }

    def clear(self):
        with self._lock:
            self.latest_vision = None
            self.latest_voice = None


pipeline_state = PipelineState()
