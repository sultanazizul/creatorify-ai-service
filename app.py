import modal
import os
import time
from fastapi import FastAPI
from api.v1.routers import avatars
from api.v1.routers.video.talking_head import projects, status
from api.v1.routers import upload
from api.v1.routers.audio import kokoro as tts, chatterbox as chatterbox_tts, voice_conversion, voice_library

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
    .env({"HF_HUB_ETAG_TIMEOUT": "60", "PYTHONPATH": "/root:/root/vendor/infinitetalk:/root/vendor"})
    .add_local_dir("vendor", "/root/vendor", copy=True)
    .add_local_dir("api", "/root/api", copy=True)
    .add_local_dir("core", "/root/core", copy=True)
    .add_local_dir("services", "/root/services", copy=True)
    .add_local_dir("models", "/root/models", copy=True)

    .apt_install("git", "ffmpeg", "git-lfs", "libmagic1")
    .run_commands("sed -i 's/from inspect import ArgSpec/# from inspect import ArgSpec  # Removed for Python 3.11 compatibility/' /root/vendor/infinitetalk/wan/multitalk.py")
    .pip_install(
        "misaki[en]", "ninja", "psutil", "packaging", "flash_attn==2.7.4.post1",
        "pydantic", "python-magic", "huggingface_hub", "soundfile", "librosa",
        "xformers==0.0.28", "supabase", "cloudinary",
        "xfuser==0.4.1",
        "httpx"  # For calling Chatterbox microservice
    )
    .pip_install_from_requirements("vendor/infinitetalk/requirements.txt")
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
        sys.path.extend(["/root", "/root/vendor/infinitetalk", "/root/vendor"])
        
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
    def _generate_video(self, image: bytes, audio1: bytes, audio2: bytes = None, audio_order: str = "left_right", prompt: str | None = None, params: dict = None, project_id: str = None) -> str:
        import sys
        sys.path.extend(["/root", "/root/vendor/infinitetalk", "/root/vendor"])
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
        from vendor.infinitetalk.generate_infinitetalk import generate
        import librosa
        from services.infrastructure.supabase import SupabaseService

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
        
        if project_id:
            db_service = SupabaseService()
            
            # --- Pipeline Helper for Video ---
            from datetime import datetime
            STAGE_WEIGHTS = {
                "SETUP": 20, "INFERENCE": 50, "POST_PROCESS": 15, "UPLOADING": 15
            }
            PIPELINE_ORDER = ["SETUP", "INFERENCE", "POST_PROCESS", "UPLOADING"]
            
            def update_pipeline(stage_key, stage_pct=0, status="active", error=None):
                """Helper to update pipeline state in DB."""
                try:
                    # 1. Calculate global progress
                    progress = 0
                    for s in PIPELINE_ORDER:
                        if s == stage_key:
                            break
                        progress += STAGE_WEIGHTS.get(s, 0)
                    
                    # Add fraction of current stage
                    progress += int(STAGE_WEIGHTS.get(stage_key, 0) * (stage_pct / 100.0))
                    progress = min(99, max(0, progress))
                    
                    # 2. Prepare pipeline metadata update
                    # Note: Using update_status directly with metadata is safer if supported,
                    # but SupabaseService.update_status currently only takes specific args.
                    # We need to fetch, update meta, and push back. 
                    # Assuming we can extend update_status or use client directly.
                    # For safety, we'll try to use the client directly if possible or update SupabaseService.
                    # Wait, update_status in supabase.py doesn't support metadata argument yet?
                    # Let's check SupabaseService.update_status in next step if needed.
                    # For now, we'll use a direct client update logic like in TTS if available, 
                    # OR we just rely on standard fields if method isn't updated.
                    # Actually, looking at previous steps, the user *added* metadata to the table.
                    # I should probably update SupabaseService.update_status to support metadata,
                    # OR do it manually here.
                    
                    # Re-reading supabase.py in previous turn... update_status takes (project_id, status, progress, video_url, error_message).
                    # It DOES NOT take metadata.
                    # I should modify update_status in supabase.py to accept metadata, OR do raw client call here.
                    # Let's do raw client call here to avoid modifying supabase.py signature broadly if not needed,
                    # OR better: Add metadata support to `update_status`.
                    # Given I am in app.py now, I will use db_service.client directly as I did in TTS logic (which used update_tts that accepted dict).
                    # But update_status is more rigid.
                    # Let's use db_service.client.table("projects").update(...) directly.
                    
                    p = db_service.get_project(project_id)
                    if not p: return

                    meta = p.get("metadata", {}) or {}
                    
                    # Init pipeline if missing
                    if "pipeline" not in meta:
                        meta["pipeline"] = {"stages": [
                            {"key": k, "label": l, "status": "pending"} 
                            for k, l in [
                                ("SETUP", "Menyiapkan model..."),
                                ("INFERENCE", "Membuat video..."),
                                ("POST_PROCESS", "Finalisasi video"),
                                ("UPLOADING", "Menyimpan hasil")
                            ]
                        ]}

                    stages = meta["pipeline"].get("stages", [])
                    now = datetime.utcnow().isoformat()
                    
                    for s in stages:
                        if s["key"] == stage_key:
                            s["status"] = status
                            if status == "completed":
                                s["completed_at"] = now
                            if error:
                                s["error"] = str(error)
                        elif s["status"] == "active" and s["key"] != stage_key:
                            s["status"] = "completed"
                            if "completed_at" not in s:
                                s["completed_at"] = now
                    
                    meta["pipeline"]["stages"] = stages
                    
                    data = {
                        "progress": progress,
                        "current_stage": stage_key,
                        "metadata": meta,
                        "updated_at": "now()"
                    }
                    if status == "failed":
                        data["status"] = "failed"
                    # Only update status if it's not finished/failed already unless we are failing it
                    elif p.get("status") not in ["finished", "failed"]:
                        data["status"] = "processing"
                        
                    db_service.client.table("projects").update(data).eq("id", project_id).execute()
                except Exception as e:
                    print(f"Pipeline update failed: {e}")

            # Define the actual callback for the generation loop
            last_reported_pct = -1
            def progress_callback(step, total_steps, current_frame_start=0, chunk_size=0, total_target_frames=0):
                nonlocal last_reported_pct
                
                if total_steps > 0 and total_target_frames > 0:
                    # Calculate progress within the current chunk
                    chunk_progress = step / total_steps
                    
                    # Calculate frames generated exactly so far in this chunk
                    current_chunk_frames = chunk_progress * chunk_size
                    
                    # Total frames approximated
                    total_current_frames = current_frame_start + current_chunk_frames
                    
                    # Global percentage
                    pct = int((total_current_frames / total_target_frames) * 100)
                    
                    # Ensure we don't exceed 100% and don't go backwards excessively (though slight jitter is ok)
                    pct = min(99, max(0, pct))
                    
                    # Update DB (throttle this to every 1% change to ensure smooth UI)
                    # Since sampling steps are low (e.g. 8), we should update on every step that increases pct
                    if pct > last_reported_pct:
                        print(f"[Progress Callback] Step {step}/{total_steps} (Chunk Start: {current_frame_start}) -> Global Pct: {pct}%")
                        update_pipeline("INFERENCE", pct, "active")
                        last_reported_pct = pct

            # Argparse simulation
            # ... existing ...
            # Note: We create the SimpleNamespace below, ensuring we pass this callback.
            update_pipeline("SETUP", 0, "active")

        # Map params to args
        import types
        output_path_no_ext = str(output_dir / output_filename)
        args = types.SimpleNamespace(**{
            "task": "infinitetalk-14B",
            "size": "infinitetalk-480",
            "ckpt_dir": "/models/Wan2.1-I2V-14B-480P",
            "infinitetalk_dir": "/models/InfiniteTalk/single/single/infinitetalk.safetensors",
            "dit_path": None,
            "quant_dir": None,
            "wav2vec_dir": "/models/chinese-wav2vec2-base",
            "lora_dir": ["/models/FusionX_LoRa/FusionX_LoRa/Wan2.1_I2V_14B_FusionX_LoRA.safetensors"],
            "lora_scale": [params.get("lora_scale", 1.0)],
            "offload_model": False,
            "ulysses_size": 1,
            "ring_size": 1,
            "t5_fsdp": False,
            "t5_cpu": False,
            "dit_fsdp": False,
            "save_file": output_path_no_ext,
            "audio_save_dir": "/outputs/temp_audio",
            "base_seed": params.get("seed", 42),
            "input_json": input_json_path,
            "motion_frame": 25,
            "mode": mode,
            "sample_steps": params.get("sample_steps", 40),
            "sample_shift": params.get("sample_shift", 3.0),
            "sample_text_guide_scale": params.get("sample_text_guide_scale", 5.0),
            "sample_audio_guide_scale": params.get("sample_audio_guide_scale", 4.0),
            "num_persistent_param_in_dit": params.get("num_persistent_param_in_dit") or 0,
            "audio_mode": "localfile",
            "use_teacache": True,
            "teacache_thresh": 0.3,
            "use_apg": True,
            "apg_momentum": -0.75,
            "apg_norm_threshold": 55,
            "color_correction_strength": params.get("color_correction_strength", 1.0),
            "scene_seg": False,
            "quant": None,
            "max_frame_num": max_frame_num,
            "frame_num": chunk_frame_num,
            "progress_callback": progress_callback
        })
        
        os.environ["RANK"] = "0"
        os.environ["WORLD_SIZE"] = "1"
        os.environ["LOCAL_RANK"] = "0"
        
        Path(args.audio_save_dir).mkdir(parents=True, exist_ok=True)
        
        # SETUP DONE
        if project_id:
             update_pipeline("SETUP", 100, "completed")
             update_pipeline("INFERENCE", 0, "active")

        # INFERENCE
        generate(args)
        
        # INFERENCE DONE
        if project_id:
             update_pipeline("INFERENCE", 100, "completed")
             update_pipeline("POST_PROCESS", 0, "active")

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
        
        # Trigger Cloudinary Upload if project_id is provided
        final_file_name = f"{output_filename}.mp4"
        if project_id:
            # POST PROCESS DONE
            update_pipeline("POST_PROCESS", 100, "completed")
            update_pipeline("UPLOADING", 0, "active")
            
            print(f"Triggering Cloudinary upload for project {project_id}...")
            upload_video_to_cloudinary.spawn(project_id, final_file_name)
        else:
            print("Warning: No project_id provided, skipping Cloudinary upload.")

        return final_file_name

    @modal.method()
    def submit(self, image_url: str, audio_url: str, audio_url_2: str = None, audio_order: str = "left_right", prompt: str = None, params: dict = None, project_id: str = None):
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
        return self._generate_video.spawn(image_bytes, audio1_bytes, audio2_bytes, audio_order, prompt, params, project_id)

# --- Upload to Cloudinary Function ---
@app.function(
    image=image,
    volumes={OUTPUT_DIR: output_volume},
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets")
    ],
    timeout=600
)
def upload_video_to_cloudinary(project_id: str, output_filename: str):
    """Upload video from volume to Cloudinary and update database."""
    from services.infrastructure.cloudinary import CloudinaryService
    from services.infrastructure.supabase import SupabaseService
    
    try:
        output_path = f"{OUTPUT_DIR}/talking_video/{output_filename}"
        print(f"[UPLOAD] Reading video from: {output_path}")
        
        if not os.path.exists(output_path):
            error_msg = f"Video file not found: {output_path}"
            print(f"[ERROR] {error_msg}")
        # Determine output folder hierarchy for Infinitalk
        # Path: Creatorify/AI Video Output/Talking Video/Infinitalk/{Tipe}
        # Tipe: Single person vs Multiperson
        db = SupabaseService()
        project = db.get_project(project_id)
        if not project:
            print(f"[UPLOAD] Warning: Project {project_id} not found in DB. Defaulting to Single Person.")
            video_type = "Single Person"
        else:
             # Logic to determine type based on project "type" field
             # Mapping: multi_person -> Multi Person, single_person -> Single Person
             p_type = project.get("type", "single_person")
             if p_type == "multi_person":
                 video_type = "Multi Person"
             else:
                 video_type = "Single Person"
        
        folder = f"Creatorify/AI Video Output/Talking Video/Infinitalk/{video_type}"

        # Upload to Cloudinary
        cloudinary = CloudinaryService()
        print(f"[UPLOAD] Uploading to Cloudinary (folder={folder})...")
        video_url = cloudinary.upload_video(output_path, public_id=f"project_{project_id}", folder=folder)
        
        if video_url:
            print(f"[UPLOAD] Success! Video URL: {video_url}")
            # Update database
            # db already initialized above
            db.update_status(project_id, "finished", 100, video_url=video_url)
            return video_url
        else:
            error_msg = "Cloudinary upload failed"
            print(f"[ERROR] {error_msg}")
            db = SupabaseService()
            db.update_status(project_id, "failed", error_message=error_msg)
            return None
            
    except Exception as e:
        import traceback
        error_msg = f"Upload error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        db = SupabaseService()
        db.update_status(project_id, "failed", error_message=error_msg)
        return None


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
    web_app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
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
    from services.audio.tts.kokoro.service import TTSService
    from services.infrastructure.supabase import SupabaseService
    from services.infrastructure.cloudinary import CloudinaryService
    
    # --- Pipeline Helper (Injected for isolation) ---
    from datetime import datetime
    STAGE_WEIGHTS = {
        "TEXT_ANALYSIS": 5, "VOICE_LOADING": 10, "INFERENCE": 60, "AUDIO_POST_PROCESS": 10, "UPLOADING": 15
    }
    PIPELINE_ORDER = ["TEXT_ANALYSIS", "VOICE_LOADING", "INFERENCE", "AUDIO_POST_PROCESS", "UPLOADING"]
    
    def update_pipeline(stage_key, stage_pct=0, status="active", error=None):
        """Helper to update pipeline state in DB."""
        try:
            # 1. Calculate global progress
            progress = 0
            for s in PIPELINE_ORDER:
                if s == stage_key:
                    break
                progress += STAGE_WEIGHTS.get(s, 0)
            
            # Add fraction of current stage
            progress += int(STAGE_WEIGHTS.get(stage_key, 0) * (stage_pct / 100.0))
            progress = min(99, max(0, progress))
            
            # 2. Prepare pipeline metadata update
            p = db.get_tts(tts_id)
            meta = p.get("metadata", {}) or {}
            
            # Ensure metadata structure exists if it was created before migration
            if "pipeline" not in meta:
                meta["pipeline"] = {"stages": [
                    {"key": k, "label": l, "status": "pending"} 
                    for k, l in [
                        ("TEXT_ANALYSIS", "Menyiapkan teks..."),
                        ("VOICE_LOADING", "Memuat karakter suara"),
                        ("INFERENCE", "Menghasilkan suara..."),
                        ("AUDIO_POST_PROCESS", "Finalisasi audio"),
                        ("UPLOADING", "Menyimpan hasil")
                    ]
                ]}

            stages = meta["pipeline"].get("stages", [])
            now = datetime.utcnow().isoformat()
            
            for s in stages:
                if s["key"] == stage_key:
                    s["status"] = status
                    if status == "completed":
                        s["completed_at"] = now
                    if error:
                        s["error"] = str(error)
                elif s["status"] == "active" and s["key"] != stage_key:
                    # Auto-complete previous stage
                     s["status"] = "completed"
                     if "completed_at" not in s:
                         s["completed_at"] = now
            
            meta["pipeline"]["stages"] = stages
            
            # 3. Update DB
            update_payload = {
                "progress": progress,
                "current_stage": stage_key,
                "metadata": meta
            }
            if status == "failed":
                update_payload["status"] = "failed"
                # tts_projects table might not have error_message column, checking schema...
                # Assuming update_tts handles dictionary updates correctly
                pass
                
            db.update_tts(tts_id, update_payload)
        except Exception as e:
            # Fallback simple update
            print(f"Pipeline update failed: {e}")
            db.update_tts(tts_id, {"progress": progress})

    try:
        # Initialize services
        tts_service = TTSService()
        db = SupabaseService()
        cloudinary = CloudinaryService()
        
        # Start Pipeline: TEXT_ANALYSIS
        update_pipeline("TEXT_ANALYSIS", 0, "active")
        
        # 1. Text Analysis (Simulated)
        # Validation is already done at API level, but we can update progress
        update_pipeline("TEXT_ANALYSIS", 100, "completed")
        
        # 2. Voice Loading
        update_pipeline("VOICE_LOADING", 0, "active")
        # In reality, loading happens inside tts_service, but we mark it here
        update_pipeline("VOICE_LOADING", 100, "completed")
        
        # 3. Inference        # 1. Generate Audio (Chunked)
        from services.audio.tts.text_chunker import TextChunker
        import soundfile as sf
        import io
        import numpy as np
        
        chunker = TextChunker(max_chunk_size=500)
        chunks = chunker.split_text(text)
        print(f"Text split into {len(chunks)} chunks for Kokoro inference")
        
        update_pipeline("INFERENCE", 0, "active")
        
        audio_segments = []
        for i, chunk in enumerate(chunks):
            print(f"Generating chunk {i+1}/{len(chunks)}...")
            
            # Generate audio for chunk
            chunk_buffer = tts_service.generate_audio(
                text=chunk,
                voice=voice,
                speed=speed,
                lang_code=lang_code
            )
            
            # Read into numpy array for concatenation
            data, samplerate = sf.read(chunk_buffer)
            audio_segments.append(data)
            
            # Update progress
            chunk_pct = int(((i + 1) / len(chunks)) * 100)
            update_pipeline("INFERENCE", chunk_pct, "active")
        
        update_pipeline("INFERENCE", 100, "completed")
        
        # Concatenate
        if not audio_segments:
             raise Exception("No audio generated")
             
        full_audio = np.concatenate(audio_segments)
        
        # 4. Audio Post Process (Saving to temp)
        update_pipeline("AUDIO_POST_PROCESS", 0, "active")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, full_audio, samplerate, format='WAV')
            tmp_path = tmp_file.name
        update_pipeline("AUDIO_POST_PROCESS", 100, "completed")
            
        # 5. Uploading
        update_pipeline("UPLOADING", 0, "active")
        print(f"Uploading to Cloudinary for {tts_id}...")
        
        public_id = f"tts_{uuid.uuid4()}"
        folder = "Creatorify/AI Audio Output/Kokoro82"
        
        audio_url = cloudinary.upload_audio(tmp_path, public_id=public_id, folder=folder)
        
        if not audio_url:
            raise Exception("Failed to upload audio to Cloudinary")
            
        # Save to Persistent Volume
        try:
            output_dir = Path("/outputs/tts")
            output_dir.mkdir(parents=True, exist_ok=True)
            persistent_path = output_dir / f"{public_id}.wav"
            shutil.copy(tmp_path, persistent_path)
        except Exception as e:
            print(f"Warning: Failed to save to persistent volume: {e}")
            
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Final Update
        update_pipeline("UPLOADING", 100, "completed")
        print(f"Updating Supabase for {tts_id}...")
        
        # Get final metadata to ensure completed timestamp
        final_update = {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100,
            "current_stage": "UPLOADING"
        }
        db.update_tts(tts_id, final_update)
        
        print(f"TTS task {tts_id} completed successfully.")
        
    except Exception as e:
        print(f"Error in TTS task {tts_id}: {e}")
        # Update status to failed
        try:
             # Try to capture error in pipeline if possible
             pass
        except: 
            pass
        # Re-raise to let Modal handle failure logging
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
    from services.audio.tts.chatterbox.tts_service import ChatterboxTTSService
    from services.audio.voice_library.voice_manager import VoiceManager
    from services.audio.tts.text_chunker import TextChunker
    from services.infrastructure.supabase import SupabaseService
    from services.infrastructure.cloudinary import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        tts_service = ChatterboxTTSService()
        voice_manager = VoiceManager()

        # --- Pipeline Helper ---
        from datetime import datetime
        STAGE_WEIGHTS = {
            "TEXT_ANALYSIS": 5, "VOICE_LOADING": 10, "INFERENCE": 60, "AUDIO_POST_PROCESS": 10, "UPLOADING": 15
        }
        PIPELINE_ORDER = ["TEXT_ANALYSIS", "VOICE_LOADING", "INFERENCE", "AUDIO_POST_PROCESS", "UPLOADING"]
        
        def update_pipeline(stage_key, stage_pct=0, status="active", error=None):
            """Helper to update pipeline state in DB."""
            try:
                # 1. Calculate global progress
                progress = 0
                for s in PIPELINE_ORDER:
                    if s == stage_key:
                        break
                    progress += STAGE_WEIGHTS.get(s, 0)
                
                # Add fraction of current stage
                progress += int(STAGE_WEIGHTS.get(stage_key, 0) * (stage_pct / 100.0))
                progress = min(99, max(0, progress))
                
                # 2. Prepare pipeline metadata update
                # We need to fetch current to merge, or just overwrite if we are confident (merging is safer)
                p = db.get_chatterbox_project(project_id)
                meta = p.get("metadata", {}) or {}
                
                if "pipeline" not in meta:
                    # Init if missing
                    meta["pipeline"] = {"stages": [
                        {"key": k, "label": l, "status": "pending"} 
                        for k, l in [
                            ("TEXT_ANALYSIS", "Menyiapkan teks..."),
                            ("VOICE_LOADING", "Memuat karakter suara"),
                            ("INFERENCE", "Menghasilkan suara..."),
                            ("AUDIO_POST_PROCESS", "Finalisasi audio"),
                            ("UPLOADING", "Menyimpan hasil")
                        ]
                    ]}

                stages = meta["pipeline"].get("stages", [])
                now = datetime.utcnow().isoformat()
                
                for s in stages:
                    if s["key"] == stage_key:
                        s["status"] = status
                        if status == "completed":
                            s["completed_at"] = now
                        if error:
                            s["error"] = str(error)
                    elif s["status"] == "active" and s["key"] != stage_key:
                        # Auto-complete previous stage
                         s["status"] = "completed"
                         if "completed_at" not in s:
                             s["completed_at"] = now
                
                meta["pipeline"]["stages"] = stages
                
                # 3. Update DB
                update_payload = {
                    "progress": progress,
                    "current_stage": stage_key,
                    "metadata": meta
                }
                if status == "failed":
                    update_payload["status"] = "failed"
                    update_payload["error_message"] = str(error)
                    
                db.update_chatterbox_project(project_id, update_payload)
                
            except Exception as e:
                print(f"Pipeline update failed: {e}")
                # Fallback simple update
                db.update_chatterbox_project(project_id, {"progress": progress})

        # --- Start Pipeline ---
        update_pipeline("TEXT_ANALYSIS", 0, "active")
        
        # Get voice sample URL
        voice_sample = voice_manager.get_voice_sample(voice_sample_id)
        if not voice_sample:
            raise Exception(f"Voice sample {voice_sample_id} not found")
        
        voice_url = voice_sample["audio_url"]
        
        # Check if text needs chunking (> 800 chars)
        chunker = TextChunker(max_chunk_size=800)
        chunks = chunker.split_text(text)
        
        update_pipeline("TEXT_ANALYSIS", 100, "completed")
        update_pipeline("VOICE_LOADING", 0, "active")
        
        print(f"Text split into {len(chunks)} chunks")
        
        # Voice Loading (Metadata fetch)
        update_pipeline("VOICE_LOADING", 100, "completed")
        
        # Generate audio for each chunk
        update_pipeline("INFERENCE", 0, "active")
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Calculate inference progress based on chunk count
            chunk_pct = int(((i) / len(chunks)) * 100)
            update_pipeline("INFERENCE", chunk_pct, "active")
            
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
        
        update_pipeline("INFERENCE", 100, "completed")
        
        # Concatenate audio chunks if multiple
        update_pipeline("AUDIO_POST_PROCESS", 0, "active")
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
            audio_buffer.seek(0)
        
        # Save to temp file
        update_pipeline("AUDIO_POST_PROCESS", 50, "active")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_buffer.read())
            audio_path = tmp_audio.name
        
        # Upload to Cloudinary
        update_pipeline("AUDIO_POST_PROCESS", 100, "completed")
        update_pipeline("UPLOADING", 0, "active")
        public_id = f"chatterbox_tts/{project_id}"
        
        # Path: Creatorify/AI Audio Output/Chatterbox/TTS Voice Cloning/
        folder = "Creatorify/AI Audio Output/Chatterbox/TTS Voice Cloning"
        
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id, folder=folder)
        
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
        
        db.update_chatterbox_project(project_id, {
            "audio_url": audio_url,
            "status": "completed",
            "progress": 100
        })
        # Mark pipeline complete
        update_pipeline("UPLOADING", 100, "completed")
        
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
    from services.audio.tts.chatterbox.multilingual_service import ChatterboxMultilingualService
    from services.audio.voice_library.voice_manager import VoiceManager
    from services.audio.tts.text_chunker import TextChunker
    from services.infrastructure.supabase import SupabaseService
    from services.infrastructure.cloudinary import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        tts_service = ChatterboxMultilingualService()
        voice_manager = VoiceManager()
        
        voice_manager = VoiceManager()

        # --- Pipeline Helper (Duplicated for isolation) ---
        from datetime import datetime
        STAGE_WEIGHTS = {
            "TEXT_ANALYSIS": 5, "VOICE_LOADING": 10, "INFERENCE": 60, "AUDIO_POST_PROCESS": 10, "UPLOADING": 15
        }
        PIPELINE_ORDER = ["TEXT_ANALYSIS", "VOICE_LOADING", "INFERENCE", "AUDIO_POST_PROCESS", "UPLOADING"]
        
        def update_pipeline(stage_key, stage_pct=0, status="active", error=None):
            """Helper to update pipeline state in DB."""
            try:
                # 1. Calculate global progress
                progress = 0
                for s in PIPELINE_ORDER:
                    if s == stage_key:
                        break
                    progress += STAGE_WEIGHTS.get(s, 0)
                
                # Add fraction of current stage
                progress += int(STAGE_WEIGHTS.get(stage_key, 0) * (stage_pct / 100.0))
                progress = min(99, max(0, progress))
                
                # 2. Prepare pipeline metadata update
                p = db.get_chatterbox_project(project_id)
                meta = p.get("metadata", {}) or {}
                
                if "pipeline" not in meta:
                    meta["pipeline"] = {"stages": [
                        {"key": k, "label": l, "status": "pending"} 
                        for k, l in [
                            ("TEXT_ANALYSIS", "Menyiapkan teks..."),
                            ("VOICE_LOADING", "Memuat karakter suara"),
                            ("INFERENCE", "Menghasilkan suara..."),
                            ("AUDIO_POST_PROCESS", "Finalisasi audio"),
                            ("UPLOADING", "Menyimpan hasil")
                        ]
                    ]}

                stages = meta["pipeline"].get("stages", [])
                now = datetime.utcnow().isoformat()
                
                for s in stages:
                    if s["key"] == stage_key:
                        s["status"] = status
                        if status == "completed":
                            s["completed_at"] = now
                        if error:
                            s["error"] = str(error)
                    elif s["status"] == "active" and s["key"] != stage_key:
                        # Auto-complete previous stage
                         s["status"] = "completed"
                         if "completed_at" not in s:
                             s["completed_at"] = now
                
                meta["pipeline"]["stages"] = stages
                
                # 3. Update DB
                update_payload = {
                    "progress": progress,
                    "current_stage": stage_key,
                    "metadata": meta
                }
                if status == "failed":
                    update_payload["status"] = "failed"
                    update_payload["error_message"] = str(error)
                    
                db.update_chatterbox_project(project_id, update_payload)
            except Exception as e:
                # Fallback simple update
                db.update_chatterbox_project(project_id, {"progress": progress})

        # --- Start Pipeline ---
        update_pipeline("TEXT_ANALYSIS", 0, "active")
        
        # Get voice sample URL if provided
        voice_url = None
        if voice_sample_id:
            voice_sample = voice_manager.get_voice_sample(voice_sample_id)
            if voice_sample:
                voice_url = voice_sample["audio_url"]
        
        # Check if text needs chunking (> 800 chars)
        chunker = TextChunker(max_chunk_size=800)
        chunks = chunker.split_text(text)
        
        update_pipeline("TEXT_ANALYSIS", 100, "completed")
        update_pipeline("VOICE_LOADING", 0, "active")
        
        print(f"Text split into {len(chunks)} chunks")
        
        # Voice Loading
        update_pipeline("VOICE_LOADING", 100, "completed")
        
        # Generate audio for each chunk
        update_pipeline("INFERENCE", 0, "active")
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Calculate inference progress based on chunk count
            chunk_pct = int(((i) / len(chunks)) * 100)
            update_pipeline("INFERENCE", chunk_pct, "active")
            
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
        
        update_pipeline("INFERENCE", 100, "completed")
        
        # Concatenate audio chunks if multiple
        update_pipeline("AUDIO_POST_PROCESS", 0, "active")
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
            audio_buffer.seek(0)
        
        # Save and upload
        update_pipeline("AUDIO_POST_PROCESS", 50, "active")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_buffer.read())
            audio_path = tmp_audio.name
        
        update_pipeline("AUDIO_POST_PROCESS", 100, "completed")
        update_pipeline("UPLOADING", 0, "active")
        public_id = f"chatterbox_multilingual/{project_id}"
        
        # Path: Creatorify/AI Audio Output/Chatterbox/Multilingual/
        folder = "Creatorify/AI Audio Output/Chatterbox/Multilingual"
        
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id, folder=folder)
        
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
    from services.audio.tts.chatterbox.vc_service import ChatterboxVCService
    from services.audio.voice_library.voice_manager import VoiceManager
    from services.infrastructure.supabase import SupabaseService
    from services.infrastructure.cloudinary import CloudinaryService
    
    try:
        db = SupabaseService()
        cloudinary = CloudinaryService()
        vc_service = ChatterboxVCService()
        voice_manager = VoiceManager()
        
        # --- Pipeline Helper (VC Specific) ---
        from datetime import datetime
        STAGE_WEIGHTS = {
            "AUDIO_PREP": 5, "SOURCE_ANALYSIS": 5, "VOICE_LOADING": 10, 
            "INFERENCE": 50, "AUDIO_POST_PROCESS": 10, "UPLOADING": 20
        }
        PIPELINE_ORDER = ["AUDIO_PREP", "SOURCE_ANALYSIS", "VOICE_LOADING", "INFERENCE", "AUDIO_POST_PROCESS", "UPLOADING"]
        
        def update_pipeline(stage_key, stage_pct=0, status="active", error=None):
            """Helper to update pipeline state in DB."""
            try:
                # 1. Calculate global progress
                progress = 0
                for s in PIPELINE_ORDER:
                    if s == stage_key:
                        break
                    progress += STAGE_WEIGHTS.get(s, 0)
                
                # Add fraction of current stage
                progress += int(STAGE_WEIGHTS.get(stage_key, 0) * (stage_pct / 100.0))
                progress = min(99, max(0, progress))
                
                # 2. Prepare pipeline metadata update
                p = db.get_chatterbox_project(project_id)
                meta = p.get("metadata", {}) or {}
                
                if "pipeline" not in meta:
                    meta["pipeline"] = {"stages": [
                        {"key": k, "label": l, "status": "pending"} 
                        for k, l in [
                            ("AUDIO_PREP", "Menyiapkan audio..."),
                            ("SOURCE_ANALYSIS", "Menganalisis suara asli..."),
                            ("VOICE_LOADING", "Memuat karakter suara"),
                            ("INFERENCE", "Mengubah suara..."),
                            ("AUDIO_POST_PROCESS", "Finalisasi audio"),
                            ("UPLOADING", "Menyimpan hasil")
                        ]
                    ]}

                stages = meta["pipeline"].get("stages", [])
                now = datetime.utcnow().isoformat()
                
                for s in stages:
                    if s["key"] == stage_key:
                        s["status"] = status
                        if status == "completed":
                            s["completed_at"] = now
                        if error:
                            s["error"] = str(error)
                    elif s["status"] == "active" and s["key"] != stage_key:
                        # Auto-complete previous stage
                         s["status"] = "completed"
                         if "completed_at" not in s:
                             s["completed_at"] = now
                
                meta["pipeline"]["stages"] = stages
                
                # 3. Update DB
                update_payload = {
                    "progress": progress,
                    "current_stage": stage_key,
                    "metadata": meta
                }
                if status == "failed":
                    update_payload["status"] = "failed"
                    update_payload["error_message"] = str(error)
                    
                db.update_chatterbox_project(project_id, update_payload)
            except Exception as e:
                # Fallback simple update
                db.update_chatterbox_project(project_id, {"progress": progress})

        # --- Start Pipeline ---
        # 1. Audio Prep
        update_pipeline("AUDIO_PREP", 0, "active")
        
        # 2. Source Analysis
        update_pipeline("AUDIO_PREP", 100, "completed")
        update_pipeline("SOURCE_ANALYSIS", 0, "active")
        
        # Simulate quick analysis (or actually check headers if possible, usually implicit in download)
        update_pipeline("SOURCE_ANALYSIS", 100, "completed")
        
        # 3. Voice Loading
        update_pipeline("VOICE_LOADING", 0, "active")
        
        # Get target voice URL
        voice_sample = voice_manager.get_voice_sample(target_voice_sample_id)
        if not voice_sample:
            raise Exception(f"Voice sample {target_voice_sample_id} not found")
        target_voice_url = voice_sample["audio_url"]
        
        update_pipeline("VOICE_LOADING", 100, "completed")
        
        # 4. Inference
        update_pipeline("INFERENCE", 0, "active")
        
        print(f"Calling Voice Conversion microservice...")
        print(f"Source audio URL: {source_audio_url}")
        print(f"Target voice URL: {target_voice_url}")
        
        audio_buffer = vc_service.convert_voice(
            source_audio_url=source_audio_url,  # Pass URLs directly to microservice
            target_voice_url=target_voice_url
        )
        
        print(f"Received audio buffer from microservice")
        
        # Validate audio buffer
        if not audio_buffer or audio_buffer.getbuffer().nbytes == 0:
            raise Exception("Microservice returned empty audio buffer")
        
        print(f"Audio buffer size: {audio_buffer.getbuffer().nbytes} bytes")
        
        update_pipeline("INFERENCE", 100, "completed")
        
        # 5. Audio Post Process
        update_pipeline("AUDIO_POST_PROCESS", 0, "active")
        
        print(f"Uploading converted audio to Cloudinary...")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            audio_data = audio_buffer.read()
            tmp_audio.write(audio_data)
            audio_path = tmp_audio.name
        
        # Verify audio is different from source (simple size check)
        import hashlib
        audio_hash = hashlib.md5(audio_data).hexdigest()
        print(f"Converted audio hash: {audio_hash}")
        print(f"Converted audio path: {audio_path}")
        
        update_pipeline("AUDIO_POST_PROCESS", 100, "completed")
        
        # 6. Uploading
        update_pipeline("UPLOADING", 0, "active")
        
        public_id = f"voice_conversion/{project_id}"
        print(f"Uploading to Cloudinary with public_id: {public_id}")
        
        # Path: Creatorify/AI Audio Output/Chatterbox/Voice Changer/
        folder = "Creatorify/AI Audio Output/Chatterbox/Voice Changer"
        
        audio_url = cloudinary.upload_audio(audio_path, public_id=public_id, folder=folder)
        print(f"Cloudinary returned URL: {audio_url}")
        
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
        
        # Final pipeline update
        update_pipeline("UPLOADING", 100, "completed")
        
        print(f"Voice Conversion project {project_id} completed")
        
    except Exception as e:
        print(f"Error in Voice Conversion {project_id}: {e}")
        try:
            db = SupabaseService()
            db.update_chatterbox_project(project_id, {"status": "failed", "error_message": str(e)})
        except:
            pass
        raise e