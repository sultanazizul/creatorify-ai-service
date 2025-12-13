import sys
import os

# Add the project root to sys.path to allow imports
sys.path.append(os.getcwd())

from services.audio.tts.kokoro.service import TTSService
import soundfile as sf

def test_tts():
    print("Initializing TTS Service...")
    try:
        service = TTSService()
        print("Service initialized.")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        return

    text = "Hello, this is a test of the Kokoro TTS service."
    print(f"Generating audio for text: '{text}'")

    try:
        audio_buffer = service.generate_audio(text)
        print("Audio generated successfully.")
        
        output_file = "test_output.wav"
        with open(output_file, "wb") as f:
            f.write(audio_buffer.read())
        
        print(f"Audio saved to {output_file}")
        
        # Verify file exists and has size
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print("Verification PASSED: Output file exists and is not empty.")
        else:
            print("Verification FAILED: Output file is missing or empty.")
            
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    test_tts()
