import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ParameterResolver:
    """
    Handles resolution of InfiniTalk video generation parameters.
    Maps high-level presets (turbo, fast, quality, low_vram) to low-level arguments.
    """
    
    # --- Presets Configuration ---
    PRESETS = {
        "turbo": {
            "name": "Turbo (Experimental)",
            "description": "Ultra-fast generation (4 steps) using LoRA. Lowest latency.",
            "sample_steps": 4,
            "sample_shift": 2.0,
            "sample_text_guide_scale": 1.0,
            "sample_audio_guide_scale": 2.0,
            "lora_scale": 1.0,
            "use_lora": True,
            "use_quantization": False,
            "size": "infinitetalk-480",
            "quant": "fp8", 
            "offload_model": False, # H100: Disable offloading 
            "num_persistent_param_in_dit": None, # Disable VRAM management
            "estimated_time_10s": "1-2 minutes",
            "estimated_time_30s": "3-4 minutes",
            "estimated_time_60s": "6-8 minutes",
            "quality_score": "7/10",
            "use_case": "Real-time interactions, rapid prototyping"
        },
        "fast": {
            "name": "Fast (Recommended)",
            "description": "8 steps with LoRA. Balanced speed/quality for production.",
            "sample_steps": 8,
            "sample_shift": 2.0,
            "sample_text_guide_scale": 1.0,
            "sample_audio_guide_scale": 2.0,
            "lora_scale": 1.0,
            "use_lora": True,
            "size": "infinitetalk-480",
            "quant": "fp8", # Forced fp8 for speed
            "use_quantization": False, # Logical flag, but we use fp8 internally
            "offload_model": False, 
            "num_persistent_param_in_dit": None,
            "estimated_time_10s": "2-3 minutes",
            "estimated_time_30s": "6-9 minutes",
            "estimated_time_60s": "15-20 minutes",
            "quality_score": "8/10",
            "use_case": "Social media, general production"
        },
        "balanced": {
            "name": "Balanced",
            "description": "20 steps with LoRA. Higher detail.",
            "sample_steps": 20,
            "sample_shift": 2.5,
            "sample_text_guide_scale": 2.0,
            "sample_audio_guide_scale": 3.0,
            "lora_scale": 1.0,
            "use_lora": True,
            "size": "infinitetalk-480",
            "quant": "fp8",
            "offload_model": False,
            "num_persistent_param_in_dit": None,
            "estimated_time_10s": "4-5 minutes",
            "estimated_time_30s": "10-14 minutes",
            "estimated_time_60s": "22-28 minutes",
            "quality_score": "8.5/10",
            "use_case": "Important presentations, high detail needs"
        },
        "quality": {
            "name": "Quality (Maximum)",
            "description": "40 steps, No LoRA. Standard high-quality generation.",
            "sample_steps": 40,
            "sample_shift": None,
            "sample_text_guide_scale": 5.0,
            "sample_audio_guide_scale": 4.0,
            "lora_scale": 0.0,
            "use_lora": False,
            "size": "infinitetalk-480",
            "quant": None,
            "offload_model": False,
            "num_persistent_param_in_dit": None,
            "estimated_time_10s": "8-10 minutes",
            "estimated_time_30s": "20-30 minutes",
            "estimated_time_60s": "50-60 minutes",
            "quality_score": "9/10",
            "use_case": "Final production, cinema quality"
        },
        "low_vram": {
            "name": "Low VRAM (Cost Effective)",
            "description": "FP8 Quantization + Memory Optimization. Fits on smaller GPUs.",
            "sample_steps": 40,
            "sample_shift": None,
            "sample_text_guide_scale": 5.0,
            "sample_audio_guide_scale": 4.0,
            "lora_scale": 0.0,
            "use_lora": False,
            "use_quantization": True,
            "size": "infinitetalk-480",
            "quant": "fp8",
            "offload_model": True, # Aggressive offloading
            "num_persistent_param_in_dit": 0, # Minimal VRAM
            "estimated_time_10s": "9-12 minutes",
            "estimated_time_30s": "25-35 minutes",
            "estimated_time_60s": "55-70 minutes",
            "quality_score": "8.5/10",
            "use_case": "Running on T4/A10G with high resolution"
        }
    }
    
    # Resolution Configurations
    RESOLUTION_CONFIGS: Dict[str, Dict[str, Any]] = {
        "480p": {
            "size": "infinitetalk-480",
            "base_resolution": (640, 640),
            "sample_shift_no_lora": 7.0,  # From official docs
            "vram_required": "18-20GB",
            "aspect_ratio_buckets": 15,
            "description": "Standard resolution, fast processing"
        },
        "720p": {
            "size": "infinitetalk-720",
            "base_resolution": (960, 960),
            "sample_shift_no_lora": 11.0,  # From official docs
            "vram_required": "24-28GB",
            "aspect_ratio_buckets": 21,
            "description": "High resolution, requires more VRAM"
        }
    }

    # VRAM Requirements Matrix
    VRAM_REQUIREMENTS: Dict[str, Dict[str, str]] = {
        "fast_480p": "18GB",
        "fast_720p": "24GB",
        "balanced_480p": "19GB",
        "balanced_720p": "25GB",
        "quality_480p": "20GB",
        "quality_720p": "28GB",
        "fast_480p_fp8": "12GB",
        "quality_480p_fp8": "14GB",
    }

    # Default fallback preset
    DEFAULT_PRESET = "fast" 

    @classmethod
    def resolve(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves final generation parameters by merging:
        1. Default Preset (base)
        2. Selected Preset (if any)
        3. User Overrides (e.g. specific step count)
        """
        params = params or {}
        
        # 1. Identify Preset
        preset_key = params.get("quality_preset", cls.DEFAULT_PRESET)
        if preset_key not in cls.PRESETS:
            logger.warning(f"Unknown preset '{preset_key}', falling back to '{cls.DEFAULT_PRESET}'")
            preset_key = cls.DEFAULT_PRESET
            
        # 2. Load Preset Config
        resolved = cls.PRESETS[preset_key].copy()
        
        # 3. Apply Explicit Overrides (only if key provided in params)
        # Allowable overrides: steps, seed, guidance scales, shift
        allowlist = [
            "sample_steps", "seed", "sample_shift", 
            "sample_text_guide_scale", "sample_audio_guide_scale",
            "color_correction_strength", "num_persistent_param_in_dit"
        ]
        
        for key in allowlist:
            if key in params and params[key] is not None:
                resolved[key] = params[key]
                
        # 4. Handle Logical Dependencies
        
        # 4.1 Resolution override
        if params.get("resolution") == "720p":
            resolved["size"] = "infinitetalk-720"
            if resolved.get("sample_shift") is None or resolved["sample_shift"] < 11.0:
                 resolved["sample_shift"] = 11.0
        elif params.get("resolution") == "480p":
            resolved["size"] = "infinitetalk-480"

        # 4.2 LoRA Configuration logic
        # If 'turbo' is manually requested but lora_scale is 0, disable LoRA
        if resolved.get("use_lora") and resolved.get("lora_scale", 1.0) == 0:
            resolved["use_lora"] = False
            
        # 4.3 Quantization override
        # If explicit quant mode is requested
        if params.get("quantization_mode"):
             resolved["quant"] = params["quantization_mode"] # e.g. 'fp8' or None

        # 4.4 Advanced VRAM settings
        # Consolidate standard params
        generated_seed = params.get("seed")
        resolved["seed"] = generated_seed if generated_seed is not None else 42
        resolved["motion_frame"] = params.get("motion_frame", 25)

        # Teacache & APG are always enabled in app.py currently, let's keep them unless disabled
        resolved["use_teacache"] = True
        resolved["teacache_thresh"] = 0.3
        resolved["use_apg"] = True
        resolved["apg_momentum"] = -0.75
        resolved["apg_norm_threshold"] = 55
        
        # Ensure offload defaults to False if not set
        if "offload_model" not in resolved:
            resolved["offload_model"] = False
        # Ensure param_in_dit defaults to None if not set
        if "num_persistent_param_in_dit" not in resolved:
            resolved["num_persistent_param_in_dit"] = None
        
        return resolved

    @staticmethod
    def validate_params(params: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates input parameters."""
        # Check step limits
        steps = params.get("sample_steps")
        if steps and (steps < 1 or steps > 100):
            return False, "sample_steps must be between 1 and 100"
            
        # Check resolution
        res = params.get("resolution")
        if res and res not in ["480p", "720p"]:
            return False, "resolution must be '480p' or '720p'"
            
        return True, ""

    @staticmethod
    def get_lora_config(use_lora: bool, scale: float = 1.0):
        """Helper to get LoRA paths for app.py"""
        if not use_lora:
            return None, None
            
        lora_dir = ["/models/FusionX_LoRa/FusionX_LoRa/Wan2.1_I2V_14B_FusionX_LoRA.safetensors"]
        lora_scale = [scale]
        return lora_dir, lora_scale

    @staticmethod
    def get_quantization_config(quant_mode: str):
        """Helper to get quantization paths"""
        if not quant_mode or quant_mode != "fp8":
            return None, None
            
        # Path to FP8 weights
        quant_dir = "/models/InfiniteTalk/quant_models/infinitetalk_single_fp8.safetensors" 
        return "fp8", quant_dir
    
    @staticmethod
    def get_estimated_time(preset: str, resolution: str, duration_seconds: int) -> str:
        """
        Get estimated processing time based on configuration.
        
        Args:
            preset: Quality preset name
            resolution: Resolution (480p/720p)
            duration_seconds: Video duration in seconds
        
        Returns:
            Estimated time as string
        """
        preset_config = ParameterResolver.PRESETS.get(preset, ParameterResolver.PRESETS["fast"])
        
        # Base times for 10s video
        base_times = {
            "fast": {"480p": 2.5, "720p": 4.0},  # LoRA-only (no FP8)
            "balanced": {"480p": 3.5, "720p": 6.0},
            "quality": {"480p": 7.0, "720p": 12.5}
        }
        
        base_time = base_times.get(preset, base_times["fast"]).get(resolution, 1.5)
        
        # Scale linearly with duration
        estimated_minutes = (duration_seconds / 10.0) * base_time
        
        if estimated_minutes < 1:
            return f"{int(estimated_minutes * 60)} seconds"
        elif estimated_minutes < 60:
            return f"{int(estimated_minutes)} minutes"
        else:
            hours = int(estimated_minutes / 60)
            mins = int(estimated_minutes % 60)
            return f"{hours}h {mins}m"

    @staticmethod
    def get_vram_requirement(preset: str, resolution: str, use_quantization: bool = False) -> str:
        """
        Get VRAM requirement for a configuration.
        
        Args:
            preset: Quality preset name
            resolution: Resolution (480p/720p)
            use_quantization: Whether FP8 quantization is enabled
        
        Returns:
            VRAM requirement as string
        """
        key = f"{preset}_{resolution}"
        if use_quantization:
            key += "_fp8"
        
        return ParameterResolver.VRAM_REQUIREMENTS.get(key, "20GB")
