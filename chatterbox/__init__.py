try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # For Python <3.8

try:
    __version__ = version("chatterbox-tts")
except Exception:
    # Fallback if package metadata not found (e.g., when copied as directory)
    __version__ = "0.0.0-dev"


from .tts import ChatterboxTTS
from .vc import ChatterboxVC
from .mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES