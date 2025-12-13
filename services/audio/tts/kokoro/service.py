import io
class TTSService:
    _instance = None
    _pipeline = None
    _current_lang_code = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Lazy initialization
        pass

    def _initialize_pipeline(self, lang_code: str):
        # Lazy imports
        from kokoro import KPipeline
        try:
            from loguru import logger
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
        
        logger.info(f"Initializing Kokoro TTS Pipeline for language: {lang_code}...")
        try:
            # Check if running in Modal with mounted volume
            import os
            model_path = '/models/tts/Kokoro-82M'
            repo_id = 'hexgrad/Kokoro-82M'
            
            if os.path.exists(os.path.join(model_path, 'config.json')):
                logger.info(f"Found local Kokoro model at {model_path}")
                repo_id = model_path
            
            self._pipeline = KPipeline(lang_code=lang_code, repo_id=repo_id)
            self._current_lang_code = lang_code
            logger.info("Kokoro TTS Pipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Kokoro TTS Pipeline: {e}")
            raise e

    def generate_audio(self, text: str, voice: str = "af_heart", speed: float = 1.0, lang_code: str = 'a') -> io.BytesIO:
        """
        Generates audio from text using the Kokoro model.
        Returns the audio data as a BytesIO object (wav format).
        """
        # Lazy imports
        import torch
        import soundfile as sf
        try:
            from loguru import logger
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)

        # Check if we need to switch language
        if self._pipeline is None or self._current_lang_code != lang_code:
             self._initialize_pipeline(lang_code)

        logger.info(f"Generating audio for text: '{text[:20]}...' with voice: {voice}, speed: {speed}, lang: {lang_code}")

        try:
            # pipeline(text, voice, speed, split_pattern) returns a generator
            generator = self._pipeline(
                text, voice=voice,
                speed=speed, split_pattern=r'\n+'
            )

            audios = []
            for i, (gs, ps, audio) in enumerate(generator):
                if audio is not None:
                    audios.append(audio)
            
            if not audios:
                raise ValueError("No audio generated from the model.")

            # Concatenate all audio segments
            full_audio = torch.cat(audios, dim=0)

            # Convert to bytes
            # Kokoro output is 24000 Hz
            buffer = io.BytesIO()
            sf.write(buffer, full_audio.numpy(), 24000, format='WAV')
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            logger.error(f"Error during audio generation: {e}")
            raise e
