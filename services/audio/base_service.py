"""
Base service class for all audio AI services.
Provides common functionality for audio processing, validation, and storage.
"""
from pathlib import Path
import tempfile
import os
from typing import Optional, Tuple


class BaseAudioService:
    """Base class for audio AI services with common utilities."""
    
    # Supported audio formats
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    # Audio constraints
    MIN_DURATION = 0.5  # seconds
    MAX_DURATION = 300  # seconds (5 minutes)
    TARGET_SAMPLE_RATE = 24000
    
    def __init__(self):
        self.temp_files = []
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file format and duration.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Lazy import
            import librosa
            
            # Check file exists
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            # Check extension
            ext = Path(file_path).suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported format. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            
            # Load and check duration
            audio, sr = librosa.load(file_path, sr=None)
            duration = len(audio) / sr
            
            if duration < self.MIN_DURATION:
                return False, f"Audio too short. Minimum: {self.MIN_DURATION}s"
            
            if duration > self.MAX_DURATION:
                return False, f"Audio too long. Maximum: {self.MAX_DURATION}s"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating audio: {str(e)}"
    
    def load_and_resample(self, file_path: str, target_sr: int = None) -> Tuple[any, int]:
        """
        Load audio file and resample to target sample rate.
        
        Returns:
            (audio_array, sample_rate)
        """
        import librosa
        
        if target_sr is None:
            target_sr = self.TARGET_SAMPLE_RATE
        
        audio, sr = librosa.load(file_path, sr=target_sr)
        return audio, sr
    
    def save_audio(self, audio, sample_rate: int, output_path: str = None) -> str:
        """
        Save audio array to file.
        
        Returns:
            path to saved file
        """
        import soundfile as sf
        
        if output_path is None:
            # Create temp file
            fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            self.temp_files.append(output_path)
        
        sf.write(output_path, audio, sample_rate)
        return output_path
    
    def cleanup_temp_files(self):
        """Remove all temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Failed to delete temp file {temp_file}: {e}")
        self.temp_files = []
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup_temp_files()
