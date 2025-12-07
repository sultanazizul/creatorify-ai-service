import modal
import os
import time
from fastapi import FastAPI
from api.v1 import projects, status, avatars, tts
from api.v1.audio import voice_library, chatterbox_tts, voice_conversion

# Define the new App class
app = modal.App("creatorify-api")

# Define persistent volumes
model_volume = modal.Volume.from_name("creatorify-models", create_if_missing=True)
output_volume = modal.Volume.from_name("creatorify-outputs", create_if_missing=True)

MODEL_DIR = "/models"
OUTPUT_DIR = "/outputs"

# Define the custom image
image = (
    modal.Image.from_registry("pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel")
    .env({"HF_HUB_ETAG_TIMEOUT": "60", "PYTHONPATH": "/root:/root/infinitetalk"})
    .add_local_dir("infinitetalk", "/root/infinitetalk", copy=True)
    .add_local_dir("api", "/root/api", copy=True)
    .add_local_dir("services", "/root/services", copy=True)
    .add_local_dir("models", "/root/models", copy=True)
    .add_local_dir("utils", "/root/utils", copy=True)
    .apt_install("git", "ffmpeg", "git-lfs", "libmagic1")
    .run_commands("sed -i 's/from inspect import ArgSpec/# from inspect import ArgSpec  # Removed for Python 3.11 compatibility/' /root/infinitetalk/wan/multitalk.py")
    .pip_install(
        "misaki[en]", "ninja", "psutil", "packaging", "flash_attn==2.7.4.post1",
        "pydantic", "python-magic", "huggingface_hub", "soundfile", "librosa",
        "xformers==0.0.28", "supabase", "cloudinary",
        "xfuser==0.4.1",
        "httpx"  # For calling Chatterbox microservice
    )
    .pip_install_from_requirements("infinitetalk/requirements.txt")
)

# --- GPU Model Class ---
@app.cls(
    gpu="H100",
    enable_memory_snapshot=True,
    experimental_options={"enable_gpu_snapshot": True},
    image=image,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
    scaledown_window=2,
    timeout=2700,
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ]
)
class Model:
    def _download_and_validate(self, url: str, expected_types: list[str]) -> bytes:
        import magic
        from fastapi import HTTPException
        import urllib.request
        
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to download from URL {url}: {e}")
        
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(content)
        if detected_mime not in expected_types:
            # Allow generic octet-stream if we trust the source, but better to be strict
            # For now, just warn or fail
            pass 
        return content

    @modal.enter()
    def initialize_model(self):
        """Initialize the model and audio components when container starts."""
        # Add module paths for imports
        import sys
        from pathlib import Path
        sys.path.extend(["/root", "/root/infinitetalk"])
        
        from huggingface_hub import snapshot_download, hf_hub_download

        print("--- Container starting. Initializing model... ---")

        try:
            # --- Download models if not present using huggingface_hub ---
            model_root = Path(MODEL_DIR)
            
            # Helper function to download files with proper error handling
            def download_file(
                repo_id: str,
                filename: str,
                local_path: Path,
                revision: str = None,
                description: str = None,
                subfolder: str | None = None,
            ) -> None:
                """Download a single file with error handling and logging."""
                # local_path is the full path to where the file should be saved
                if local_path.exists():
                    print(f"--- {description or filename} already present at {local_path} ---")
                    return
                
                local_path.parent.mkdir(parents=True, exist_ok=True)

                print(f"--- Downloading {description or filename} to {local_path}... ---")
                try:
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        revision=revision,
                        local_dir=local_path.parent,
                        subfolder=subfolder,
                    )
                    print(f"--- {description or filename} downloaded successfully ---")
                except Exception as e:
                    raise RuntimeError(f"Failed to download {description or filename} from {repo_id}: {e}")
            
            def download_repo(repo_id: str, local_dir: Path, check_file: str, description: str) -> None:
                """Download entire repository with error handling and logging."""
                check_path = local_dir / check_file
                if check_path.exists():
                    print(f"--- {description} already present ---")
                    return
                
                print(f"--- Downloading {description}... ---")
                try:
                    snapshot_download(repo_id=repo_id, local_dir=local_dir)
                    print(f"--- {description} downloaded successfully ---")
                except Exception as e:
                    raise RuntimeError(f"Failed to download {description} from {repo_id}: {e}")

            try:
                # Create necessary directories
                # (model_root / "quant_models").mkdir(parents=True, exist_ok=True)
                
                # Download full Wan model for non-quantized operation with LoRA support
                wan_model_dir = model_root / "Wan2.1-I2V-14B-480P"
                wan_model_dir.mkdir(exist_ok=True)
                
                # Essential Wan model files (config and encoders)
                wan_base_files = [
                    ("config.json", "Wan model config"),
                    ("models_t5_umt5-xxl-enc-bf16.pth", "T5 text encoder weights"),
                    ("models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth", "CLIP vision encoder weights"),
                    ("Wan2.1_VAE.pth", "VAE weights")
                ]
                
                for filename, description in wan_base_files:
                    download_file(
                        repo_id="Wan-AI/Wan2.1-I2V-14B-480P",
                        filename=filename,
                        local_path=wan_model_dir / filename,
                        description=description
                    )
                
                # Download full diffusion model (7 shards) - required for non-quantized operation
                wan_diffusion_files = [
                    ("diffusion_pytorch_model-00001-of-00007.safetensors", "Wan diffusion model shard 1/7"),
                    ("diffusion_pytorch_model-00002-of-00007.safetensors", "Wan diffusion model shard 2/7"),
                    ("diffusion_pytorch_model-00003-of-00007.safetensors", "Wan diffusion model shard 3/7"),
                    ("diffusion_pytorch_model-00004-of-00007.safetensors", "Wan diffusion model shard 4/7"),
                    ("diffusion_pytorch_model-00005-of-00007.safetensors", "Wan diffusion model shard 5/7"),
                    ("diffusion_pytorch_model-00006-of-00007.safetensors", "Wan diffusion model shard 6/7"),
                    ("diffusion_pytorch_model-00007-of-00007.safetensors", "Wan diffusion model shard 7/7")
                ]
                
                for filename, description in wan_diffusion_files:
                    download_file(
                        repo_id="Wan-AI/Wan2.1-I2V-14B-480P",
                        filename=filename,
                        local_path=wan_model_dir / filename,
                        description=description
                    )
                
                # Download tokenizer directories (need full structure)
                tokenizer_dirs = [
                    ("google/umt5-xxl", "T5 tokenizer"),
                    ("xlm-roberta-large", "CLIP tokenizer")
                ]
                
                for subdir, description in tokenizer_dirs:
                    tokenizer_path = wan_model_dir / subdir
                    if not (tokenizer_path / "tokenizer_config.json").exists():
                        print(f"--- Downloading {description}... ---")
                        try:
                            snapshot_download(
                                repo_id="Wan-AI/Wan2.1-I2V-14B-480P",
                                allow_patterns=[f"{subdir}/*"],
                                local_dir=wan_model_dir
                            )
                            print(f"--- {description} downloaded successfully ---")
                        except Exception as e:
                            raise RuntimeError(f"Failed to download {description}: {e}")
                    else:
                        print(f"--- {description} already present ---")
                
                # Download chinese wav2vec2 model (need full structure for from_pretrained)
                wav2vec_model_dir = model_root / "chinese-wav2vec2-base"
                download_repo(
                    repo_id="TencentGameMate/chinese-wav2vec2-base",
                    local_dir=wav2vec_model_dir,
                    check_file="config.json",
                    description="Chinese wav2vec2-base model"
                )
                
                # Download specific wav2vec safetensors file from PR revision
                download_file(
                    repo_id="TencentGameMate/chinese-wav2vec2-base",
                    filename="model.safetensors",
                    local_path=wav2vec_model_dir / "model.safetensors",
                    revision="refs/pr/1",
                    description="wav2vec safetensors file"
                )
                
                # Download InfiniteTalk weights
                infinitetalk_dir = model_root / "InfiniteTalk" / "single"
                infinitetalk_dir.mkdir(parents=True, exist_ok=True)
                download_file(
                    repo_id="MeiGen-AI/InfiniteTalk",
                    filename="single/infinitetalk.safetensors",
                    local_path=infinitetalk_dir / "infinitetalk.safetensors",
                    description="InfiniteTalk weights file",
                )

                # Download FusioniX LoRA weights (will create FusionX_LoRa directory)
                download_file(
                    repo_id="vrgamedevgirl84/Wan14BT2VFusioniX",
                    filename="Wan2.1_I2V_14B_FusionX_LoRA.safetensors",
                    local_path=model_root / "FusionX_LoRa" / "Wan2.1_I2V_14B_FusionX_LoRA.safetensors",
                    subfolder="FusionX_LoRa",
                    description="FusioniX LoRA weights",
                )

                # Download Kokoro-82M TTS model
                kokoro_dir = model_root / "tts" / "Kokoro-82M"
                download_repo(
                    repo_id="hexgrad/Kokoro-82M",
                    local_dir=kokoro_dir,
                    check_file="config.json",
                    description="Kokoro-82M TTS model"
                )
                
                print("--- All required files present. Committing to volume. ---")
                model_volume.commit()
                print("--- Volume committed. ---")
                
            except Exception as download_error:
                print(f"--- Failed to download models: {download_error} ---")
                print("--- This repository may be private/gated or require authentication ---")
                raise RuntimeError(f"Cannot access required models: {download_error}")

            print("--- Model downloads completed successfully. ---")
            print("--- Will initialize models when generate() is called. ---")

        except Exception as e:
            print(f"--- Error during initialization: {e} ---")
            import traceback
            traceback.print_exc()
            raise

    @modal.method()
    def _generate_video(self, image: bytes, audio1: bytes, audio2: bytes = None, audio_order: str = "left_right", prompt: str | None = None, params: dict = None) -> str:
        import sys
        sys.path.extend(["/root", "/root/infinitetalk"])
        from PIL import Image as PILImage
        import io
        import tempfile
        import time
        from types import SimpleNamespace
        import uuid
        import magic
        import json
        import os
        import shutil
        from pathlib import Path
        from infinitetalk.generate_infinitetalk import generate
        import librosa

        params = params or {}
        t0 = time.time()
        
        # --- Prepare Inputs ---
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(image)
        
        if detected_mime.startswith('video/'):
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                tmp_file.write(image)
                image_path = tmp_file.name
        else:
            source_image = PILImage.open(io.BytesIO(image)).convert("RGB")
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_image:
                source_image.save(tmp_image.name, "JPEG")
                image_path = tmp_image.name

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio1:
            tmp_audio1.write(audio1)
            audio1_path = tmp_audio1.name
        
        cond_audio_dict = {"person1": audio1_path}
        
        # Handle second audio for multi-person
        audio2_path = None
        if audio2:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio2:
                tmp_audio2.write(audio2)
                audio2_path = tmp_audio2.name
            cond_audio_dict["person2"] = audio2_path

        input_data = {
            "cond_video": image_path,
            "cond_audio": cond_audio_dict,
            "prompt": prompt or "a person is talking",
        }

        input_json_data = {
            "prompt": input_data["prompt"],
            "cond_video": input_data["cond_video"],
            "cond_audio": input_data["cond_audio"]
        }
        
        # Map audio_order to audio_type
        if len(input_data["cond_audio"]) > 1:
            if audio_order == "meanwhile":
                input_json_data["audio_type"] = "para"
            elif audio_order == "right_left":
                input_json_data["audio_type"] = "reverse_add"
            else: # left_right (default)
                input_json_data["audio_type"] = "add"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as tmp_json:
            json.dump(input_json_data, tmp_json)
            input_json_path = tmp_json.name
        
        # Calculate frame_num
        duration1 = librosa.get_duration(path=audio1_path)
        total_audio_duration = duration1
        
        if audio2_path:
            duration2 = librosa.get_duration(path=audio2_path)
            if audio_order == "meanwhile":
                total_audio_duration = max(duration1, duration2)
            else: # left_right or right_left (sequential)
                total_audio_duration = duration1 + duration2
                
        audio_embedding_frames = int(total_audio_duration * 25)
        max_possible_frames = max(5, audio_embedding_frames - 5)
        # Remove hardcoded limit of 1000 frames (approx 40s)
        # calculated_frame_num = min(1000, max_possible_frames)
        calculated_frame_num = max_possible_frames
        n = (calculated_frame_num - 1) // 4
        frame_num = 4 * n + 1
        
        if frame_num >= audio_embedding_frames:
            safe_frames = audio_embedding_frames - 10
            n = max(1, (safe_frames - 1) // 4)
            frame_num = 4 * n + 1
            
        # Override frame_num if provided in params (Advanced)
        if params.get('frame_num'):
             frame_num = params['frame_num']

        if calculated_frame_num > 81:
            mode = "streaming"
            chunk_frame_num = 81
            max_frame_num = frame_num
        else:
            mode = "clip"
            chunk_frame_num = frame_num
            max_frame_num = frame_num

        output_filename = f"{uuid.uuid4()}"
        output_dir = Path(OUTPUT_DIR)
        model_root = Path(MODEL_DIR)
        
        # Map params to args
        args = SimpleNamespace(
            task="infinitetalk-14B",
            size="infinitetalk-480",
            frame_num=chunk_frame_num,
            max_frame_num=max_frame_num,
            ckpt_dir=str(model_root / "Wan2.1-I2V-14B-480P"),
            infinitetalk_dir=str(model_root / "InfiniteTalk" / "single" / "single" / "infinitetalk.safetensors"),
            quant_dir=None,
            wav2vec_dir=str(model_root / "chinese-wav2vec2-base"),
            dit_path=None,
            lora_dir=[str(model_root / "FusionX_LoRa" / "FusionX_LoRa" / "Wan2.1_I2V_14B_FusionX_LoRA.safetensors")],
            lora_scale=[params.get('lora_scale', 1.0)],
            offload_model=False,
            ulysses_size=1,
            ring_size=1,
            t5_fsdp=False,
            t5_cpu=False,
            dit_fsdp=False,
            save_file=str(output_dir / output_filename),
            audio_save_dir=str(output_dir / "temp_audio"),
            base_seed=params.get('seed', 42) or 42,
            input_json=input_json_path,
            motion_frame=25,
            mode=mode,
            sample_steps=params.get('sample_steps', 8),
            sample_shift=params.get('sample_shift', 3.0),
            sample_text_guide_scale=params.get('sample_text_guide_scale', 1.0),
            sample_audio_guide_scale=params.get('sample_audio_guide_scale', 6.0),
            num_persistent_param_in_dit=500000000,
            audio_mode="localfile",
            use_teacache=True,
            teacache_thresh=0.3,
            use_apg=True,
            apg_momentum=-0.75,
            apg_norm_threshold=55,
            color_correction_strength=params.get('color_correction_strength', 0.2),
            scene_seg=False,
            quant=None,
        )
        
        os.environ["RANK"] = "0"
        os.environ["WORLD_SIZE"] = "1"
        os.environ["LOCAL_RANK"] = "0"
        
        Path(args.audio_save_dir).mkdir(parents=True, exist_ok=True)
        generate(args)
        
        generated_file = f"{args.save_file}.mp4"
        
        # Organize outputs into folders
        output_subdir = output_dir / "talking_video"
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        final_output_path = output_subdir / f"{output_filename}.mp4"
        
        if os.path.exists(generated_file):
            os.rename(generated_file, final_output_path)
        
        output_volume.commit()
        
        os.unlink(input_json_path)
        if Path(args.audio_save_dir).exists():
            shutil.rmtree(args.audio_save_dir)
        os.unlink(audio1_path)
        if audio2_path:
            os.unlink(audio2_path)
        os.unlink(image_path)

        return output_filename + ".mp4"

    @modal.method()
    def submit(self, image_url: str, audio_url: str, audio_url_2: str = None, audio_order: str = "left_right", prompt: str = None, params: dict = None):
        # Download inputs
        image_bytes = self._download_and_validate(image_url, [
            "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
            "video/mp4", "video/avi", "video/quicktime", "video/webm"
        ])
        audio1_bytes = self._download_and_validate(audio_url, ["audio/mpeg", "audio/wav", "audio/x-wav"])
        
        audio2_bytes = None
        if audio_url_2:
            audio2_bytes = self._download_and_validate(audio_url_2, ["audio/mpeg", "audio/wav", "audio/x-wav"])
        
        # Spawn generation
        return self._generate_video.spawn(image_bytes, audio1_bytes, audio2_bytes, audio_order, prompt, params)

# --- FastAPI App ---
@app.function(
    image=image,
    volumes={OUTPUT_DIR: output_volume, MODEL_DIR: model_volume}, # Mount output volume to read results
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets"),
        modal.Secret.from_name("api-key-secret")
    ]
)
@modal.asgi_app()
def fastapi_app():
    web_app = FastAPI(title="Creatorify AI API", version="2.0.0")
    
    # Store Modal function references in app state
    web_app.state.process_tts_task = process_tts_task
    web_app.state.process_chatterbox_tts = process_chatterbox_tts
    web_app.state.process_chatterbox_multilingual = process_chatterbox_multilingual
    web_app.state.process_voice_conversion = process_voice_conversion
    
    # Include routers
    web_app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    web_app.include_router(status.router, prefix="/api/v1/projects", tags=["status"])
    web_app.include_router(avatars.router, prefix="/api/v1/avatars", tags=["avatars"])
    web_app.include_router(tts.router, prefix="/api/v1/tts", tags=["tts"])
    
    # Chatterbox routers
    web_app.include_router(voice_library.router, prefix="/api/v1/audio/voice-library", tags=["voice-library"])
    web_app.include_router(chatterbox_tts.router, prefix="/api/v1/audio/chatterbox", tags=["chatterbox"])
    web_app.include_router(voice_conversion.router, prefix="/api/v1/audio/voice-conversion", tags=["voice-conversion"])
    
    return web_app

@app.function(
    image=image,
    volumes={MODEL_DIR: model_volume},
    timeout=3600
)
def download_models():
    """
    Function to manually trigger model downloads to the volume.
    Run with: modal run app.py::download_models
    """
    print("Starting manual model download...")
    # We can reuse the logic from Model.initialize_model by instantiating it or extracting the logic.
    # For simplicity and to avoid instantiating the heavy Model class, I'll replicate the download logic here
    # or better, just instantiate Model and call initialize_model if possible, but Model needs secrets.
    # Let's just copy the critical download part for TTS since that's what's missing.
    
    import sys
    from pathlib import Path
    from huggingface_hub import snapshot_download, hf_hub_download
    
    model_root = Path(MODEL_DIR)
    
    def download_repo(repo_id: str, local_dir: Path, check_file: str, description: str) -> None:
        check_path = local_dir / check_file
        if check_path.exists():
            print(f"--- {description} already present ---")
            return
        print(f"--- Downloading {description}... ---")
        snapshot_download(repo_id=repo_id, local_dir=local_dir)
        print(f"--- {description} downloaded successfully ---")

    try:
        # Download Kokoro-82M TTS model
        kokoro_dir = model_root / "tts" / "Kokoro-82M"
        download_repo(
            repo_id="hexgrad/Kokoro-82M",
            local_dir=kokoro_dir,
            check_file="config.json",
            description="Kokoro-82M TTS model"
        )
        print("--- Committing volume... ---")
        model_volume.commit()
        print("--- Download complete! ---")
    except Exception as e:
        print(f"Error downloading models: {e}")
        raise e

@app.function(
    image=image,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ],
    timeout=600
)
def process_tts_task(tts_id: str, text: str, voice: str, speed: float, lang_code: str):
    """
    Background task to generate TTS audio and update Supabase.
    """
    print(f"Processing TTS task {tts_id}...")
    
    # Lazy imports to avoid top-level dependency issues
    import os
    import uuid
    import tempfile
    from pathlib import Path
    import shutil
    from services.tts_service import TTSService
    from services.supabase_service import SupabaseService
    from services.cloudinary_service import CloudinaryService
    
    try:
        # Initialize services
        tts_service = TTSService()
        db = SupabaseService()
        cloudinary = CloudinaryService()
        
        # Update: Started processing
        db.update_tts(tts_id, {"status": "processing", "progress": 10})
        
        # 1. Generate Audio
        print(f"Generating audio for {tts_id}...")
        db.update_tts(tts_id, {"progress": 30})
        
        audio_buffer = tts_service.generate_audio(
            text=text,
            voice=voice,
            speed=speed,
            lang_code=lang_code
        )
        
        # 2. Save to temp file
        db.update_tts(tts_id, {"progress": 60})
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_buffer.read())
            tmp_path = tmp_file.name
            
        # 3. Upload to Cloudinary
        print(f"Uploading to Cloudinary for {tts_id}...")
        db.update_tts(tts_id, {"progress": 80})
        
        public_id = f"tts_{uuid.uuid4()}"
        audio_url = cloudinary.upload_audio(tmp_path, public_id=public_id)
        
        if not audio_url:
            raise Exception("Failed to upload audio to Cloudinary")
            
        # 4. Save to Persistent Volume
        try:
            output_dir = Path("/outputs/tts")
            output_dir.mkdir(parents=True, exist_ok=True)
            persistent_path = output_dir / f"{public_id}.wav"
            shutil.copy(tmp_path, persistent_path)
        except Exception as e:
            print(f"Warning: Failed to save to persistent volume: {e}")
            
        # Clean up temp file
        os.unlink(tmp_path)
        
        # 5. Update Supabase
        print(f"Updating Supabase for {tts_id}...")
        db.update_tts(tts_id, {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100
        })
        
        print(f"TTS task {tts_id} completed successfully.")
        
    except Exception as e:
        print(f"Error in TTS task {tts_id}: {e}")
        # Update status to failed
        try:
            db = SupabaseService()
            db.update_tts(tts_id, {"status": "failed"})
        except Exception as db_e:
            print(f"Failed to update error status in DB: {db_e}")
        raise e

# --- Chatterbox Background Processing Functions ---

@app.function(
    image=image,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ],
    timeout=600,
    gpu="A10G"
)
def process_chatterbox_tts(
    project_id: str,
    text: str,
    voice_sample_id: str,
    exaggeration: float,
    temperature: float,
    cfg_weight: float,
    repetition_penalty: float,
    min_p: float,
    top_p: float
):
    """Background task for Chatterbox TTS generation."""
    print(f"Processing Chatterbox TTS project {project_id}...")
    
    import tempfile
    import uuid
    from pathlib import Path
    import shutil
    import io
    import soundfile as sf
    import numpy as np
    from services.audio_ai.tts.chatterbox.tts_service import ChatterboxTTSService
    from services.audio_ai.voice_library.voice_manager import VoiceManager
    from services.audio_ai.tts.text_chunker import TextChunker
    from services.supabase_service import SupabaseService
    from services.cloudinary_service import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        tts_service = ChatterboxTTSService()
        voice_manager = VoiceManager()
        
        # Update: Started
        db.update_chatterbox_project(project_id, {"status": "processing", "progress": 10})
        
        # Get voice sample URL
        voice_sample = voice_manager.get_voice_sample(voice_sample_id)
        if not voice_sample:
            raise Exception(f"Voice sample {voice_sample_id} not found")
        
        voice_url = voice_sample["audio_url"]
        
        # Check if text needs chunking (> 800 chars)
        chunker = TextChunker(max_chunk_size=800)
        chunks = chunker.split_text(text)
        
        print(f"Text split into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        db.update_chatterbox_project(project_id, {"progress": 30})
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_progress = 30 + int((i / len(chunks)) * 40)  # Progress from 30% to 70%
            db.update_chatterbox_project(project_id, {"progress": chunk_progress})
            
            print(f"Generating chunk {i+1}/{len(chunks)}: '{chunk[:50]}...'")
            
            chunk_buffer = tts_service.generate_audio(
                text=chunk,
                voice_sample_url=voice_url,
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight,
                repetition_penalty=repetition_penalty,
                min_p=min_p,
                top_p=top_p
            )
            audio_chunks.append(chunk_buffer)
        
        # Concatenate audio chunks if multiple
        db.update_chatterbox_project(project_id, {"progress": 70})
        if len(audio_chunks) > 1:
            print(f"Concatenating {len(audio_chunks)} audio chunks...")
            
            # Read all chunks
            audio_arrays = []
            sample_rate = None
            for chunk_buffer in audio_chunks:
                chunk_buffer.seek(0)
                audio_data, sr = sf.read(chunk_buffer)
                audio_arrays.append(audio_data)
                if sample_rate is None:
                    sample_rate = sr
            
            # Concatenate
            combined_audio = np.concatenate(audio_arrays)
            
            # Write to buffer
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, combined_audio, sample_rate, format='WAV')
            audio_buffer.seek(0)
        else:
            audio_buffer = audio_chunks[0]
        
        # Save to temp file
        db.update_chatterbox_project(project_id, {"progress": 70})
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_buffer.read())
            audio_path = tmp_audio.name
        
        # Upload to Cloudinary
        db.update_chatterbox_project(project_id, {"progress": 85})
        public_id = f"chatterbox_tts/{project_id}"
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id)
        
        # Save to volume
        try:
            output_dir = Path("/outputs/chatterbox/tts")
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(audio_path, output_dir / f"{project_id}.wav")
        except Exception as e:
            print(f"Warning: Failed to save to volume: {e}")
        
        # Cleanup
        import os
        os.unlink(audio_path)
        
        # Update DB
        db.update_chatterbox_project(project_id, {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100
        })
        
        print(f"Chatterbox TTS project {project_id} completed")
        
    except Exception as e:
        print(f"Error in Chatterbox TTS {project_id}: {e}")
        try:
            db = SupabaseService()
            db.update_chatterbox_project(project_id, {"status": "failed", "error_message": str(e)})
        except:
            pass
        raise e

@app.function(
    image=image,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ],
    timeout=600,
    gpu="A10G"
)
def process_chatterbox_multilingual(
    project_id: str,
    text: str,
    language_id: str,
    voice_sample_id: str,
    exaggeration: float,
    temperature: float,
    cfg_weight: float,
    repetition_penalty: float,
    min_p: float,
    top_p: float
):
    """Background task for Chatterbox Multilingual TTS."""
    print(f"Processing Chatterbox Multilingual project {project_id} ({language_id})...")
    
    import tempfile
    import uuid
    from pathlib import Path
    import shutil
    import io
    import soundfile as sf
    import numpy as np
    from services.audio_ai.tts.chatterbox.multilingual_service import ChatterboxMultilingualService
    from services.audio_ai.voice_library.voice_manager import VoiceManager
    from services.audio_ai.tts.text_chunker import TextChunker
    from services.supabase_service import SupabaseService
    from services.cloudinary_service import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        tts_service = ChatterboxMultilingualService()
        voice_manager = VoiceManager()
        
        db.update_chatterbox_project(project_id, {"status": "processing", "progress": 10})
        
        # Get voice sample URL if provided
        voice_url = None
        if voice_sample_id:
            voice_sample = voice_manager.get_voice_sample(voice_sample_id)
            if voice_sample:
                voice_url = voice_sample["audio_url"]
        
        # Check if text needs chunking (> 800 chars)
        chunker = TextChunker(max_chunk_size=800)
        chunks = chunker.split_text(text)
        
        print(f"Text split into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        db.update_chatterbox_project(project_id, {"progress": 30})
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_progress = 30 + int((i / len(chunks)) * 40)  # Progress from 30% to 70%
            db.update_chatterbox_project(project_id, {"progress": chunk_progress})
            
            print(f"Generating chunk {i+1}/{len(chunks)}: '{chunk[:50]}...'")
            
            chunk_buffer = tts_service.generate_audio(
                text=chunk,
                language_id=language_id,
                voice_sample_url=voice_url,
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight,
                repetition_penalty=repetition_penalty,
                min_p=min_p,
                top_p=top_p
            )
            audio_chunks.append(chunk_buffer)
        
        # Concatenate audio chunks if multiple
        db.update_chatterbox_project(project_id, {"progress": 70})
        if len(audio_chunks) > 1:
            print(f"Concatenating {len(audio_chunks)} audio chunks...")
            
            # Read all chunks
            audio_arrays = []
            sample_rate = None
            for chunk_buffer in audio_chunks:
                chunk_buffer.seek(0)
                audio_data, sr = sf.read(chunk_buffer)
                audio_arrays.append(audio_data)
                if sample_rate is None:
                    sample_rate = sr
            
            # Concatenate
            combined_audio = np.concatenate(audio_arrays)
            
            # Write to buffer
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, combined_audio, sample_rate, format='WAV')
            audio_buffer.seek(0)
        else:
            audio_buffer = audio_chunks[0]
        
        # Save and upload
        db.update_chatterbox_project(project_id, {"progress": 70})
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_buffer.read())
            audio_path = tmp_audio.name
        
        db.update_chatterbox_project(project_id, {"progress": 85})
        public_id = f"chatterbox_multilingual/{project_id}"
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id)
        
        # Save to volume
        try:
            output_dir = Path("/outputs/chatterbox/multilingual")
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(audio_path, output_dir / f"{project_id}.wav")
        except Exception as e:
            print(f"Warning: Failed to save to volume: {e}")
        
        # Cleanup
        import os
        os.unlink(audio_path)
        
        # Update DB
        db.update_chatterbox_project(project_id, {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100
        })
        
        print(f"Multilingual TTS project {project_id} completed")
        
    except Exception as e:
        print(f"Error in Multilingual TTS {project_id}: {e}")
        try:
            db = SupabaseService()
            db.update_chatterbox_project(project_id, {"status": "failed", "error_message": str(e)})
        except:
            pass
        raise e

@app.function(
    image=image,
    volumes={MODEL_DIR: model_volume, OUTPUT_DIR: output_volume},
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ],
    timeout=600,
    gpu="A10G"
)
def process_voice_conversion(
    project_id: str,
    source_audio_url: str,
    target_voice_sample_id: str
):
    """Background task for Voice Conversion."""
    print(f"Processing Voice Conversion project {project_id}...")
    
    import tempfile
    from pathlib import Path
    import shutil
    from services.audio_ai.tts.chatterbox.vc_service import ChatterboxVCService
    from services.audio_ai.voice_library.voice_manager import VoiceManager
    from services.supabase_service import SupabaseService
    from services.cloudinary_service import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        vc_service = ChatterboxVCService()
        voice_manager = VoiceManager()
        
        db.update_chatterbox_project(project_id, {"status": "processing", "progress": 10})
        
        # Get target voice URL
        voice_sample = voice_manager.get_voice_sample(target_voice_sample_id)
        if not voice_sample:
            raise Exception(f"Voice sample {target_voice_sample_id} not found")
        
        target_voice_url = voice_sample["audio_url"]
        
        # Convert voice via microservice
        db.update_chatterbox_project(project_id, {"progress": 50})
        audio_buffer = vc_service.convert_voice(
            source_audio_url=source_audio_url,  # Pass URLs directly to microservice
            target_voice_url=target_voice_url
        )
        
        # Save and upload
        db.update_chatterbox_project(project_id, {"progress": 80})
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_buffer.read())
            audio_path = tmp_audio.name
        
        public_id = f"voice_conversion/{project_id}"
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id)
        
        # Save to volume
        try:
            output_dir = Path("/outputs/chatterbox/vc")
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(audio_path, output_dir / f"{project_id}.wav")
        except Exception as e:
            print(f"Warning: Failed to save to volume: {e}")
        
        # Cleanup
        import os
        os.unlink(audio_path)
        
        # Update DB
        db.update_chatterbox_project(project_id, {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100
        })
        
        print(f"Voice Conversion project {project_id} completed")
        
    except Exception as e:
        print(f"Error in Voice Conversion {project_id}: {e}")
        try:
            db = SupabaseService()
            db.update_chatterbox_project(project_id, {"status": "failed", "error_message": str(e)})
        except:
            pass
        raise e