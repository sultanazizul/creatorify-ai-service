import modal
import os
import time
from fastapi import FastAPI
from api.v1 import projects, status, avatars

# Define the new App class
app = modal.App("infinitetalk-api")

# Define persistent volumes
model_volume = modal.Volume.from_name("infinitetalk-models", create_if_missing=True)
output_volume = modal.Volume.from_name("infinitetalk-outputs", create_if_missing=True)

MODEL_DIR = "/models"
OUTPUT_DIR = "/outputs"

# Define the custom image
image = (
    modal.Image.from_registry("pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel")
    .env({"HF_HUB_ETAG_TIMEOUT": "60"})
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
        "xformers==0.0.28", "supabase", "cloudinary", # Added new deps
        "xfuser==0.4.1" # Pin version to match requirements.txt
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
        final_output_path = output_dir / f"{output_filename}.mp4"
        
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
    volumes={OUTPUT_DIR: output_volume}, # Mount output volume to read results
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("cloudinary-secrets"),
        modal.Secret.from_name("api-key-secret")
    ]
)
@modal.asgi_app()
def fastapi_app():
    web_app = FastAPI(title="InfiniteTalk API", version="1.0.0")
    
    # Include routers
    web_app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    web_app.include_router(status.router, prefix="/api/v1/projects", tags=["status"])
    web_app.include_router(avatars.router, prefix="/api/v1/avatars", tags=["avatars"])
    
    return web_app