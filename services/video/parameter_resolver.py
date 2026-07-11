# Parameter Resolver Service for InfiniteTalk

"""
Resolves final generation parameters by merging presets with user overrides.
Priority: User Manual Override > Preset > Default
"""

from typing import Dict, Any, Optional
import sys
import os

# Add root directory to sys.path to ensure config can be imported
# This is necessary because in Modal, the execution context might vary
if "/root" not in sys.path:
    sys.path.insert(0, "/root")

try:
    from config.infinitetalk_presets import QUALITY_PRESETS, RESOLUTION_CONFIGS
except ImportError:
    # Fallback: try relative import if running locally or different structure
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    from config.infinitetalk_presets import QUALITY_PRESETS, RESOLUTION_CONFIGS

class ParameterResolver:
    """
    Resolves final parameters by merging presets with user overrides.
    """
    
    @staticmethod
    def resolve(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve final generation parameters.
        
        Args:
            params: User-provided parameters (can include preset or manual values)
        
        Returns:
            Dict with all parameters ready for InfiniteTalk generation
        """
        # Get preset (default to "fast")
        preset_name = params.get("quality_preset", "fast")
        if preset_name not in QUALITY_PRESETS:
            preset_name = "fast"
        
        preset = QUALITY_PRESETS[preset_name]
        
        # Get resolution config (default to "480p")
        resolution = params.get("resolution", "480p")
        if resolution not in RESOLUTION_CONFIGS:
            resolution = "480p"
        
        resolution_config = RESOLUTION_CONFIGS[resolution]
        
        # Start with preset values
        resolved = {
            "size": resolution_config["size"],
            "sample_steps": preset["sample_steps"],
            "sample_text_guide_scale": preset["sample_text_guide_scale"],
            "sample_audio_guide_scale": preset["sample_audio_guide_scale"],
            "lora_scale": preset["lora_scale"],
            "use_lora": preset["use_lora"],
        }
        
        # Resolve sample_shift
        if params.get("sample_shift") is not None:
            # User manual override
            resolved["sample_shift"] = params["sample_shift"]
        elif preset["sample_shift"] is not None:
            # Preset value (for LoRA modes: Fast/Balanced)
            resolved["sample_shift"] = preset["sample_shift"]
        else:
            # Auto-calculate for non-LoRA (Quality mode)
            resolved["sample_shift"] = resolution_config["sample_shift_no_lora"]
        
        # Apply user manual overrides
        if params.get("sample_steps") is not None:
            resolved["sample_steps"] = params["sample_steps"]
        
        if params.get("sample_text_guide_scale") is not None:
            resolved["sample_text_guide_scale"] = params["sample_text_guide_scale"]
        
        if params.get("sample_audio_guide_scale") is not None:
            resolved["sample_audio_guide_scale"] = params["sample_audio_guide_scale"]
        
        if params.get("lora_scale") is not None:
            resolved["lora_scale"] = params["lora_scale"]
        
        if params.get("use_lora") is not None:
            resolved["use_lora"] = params["use_lora"]
            # If user disables LoRA, set lora_scale to 0
            if not params["use_lora"]:
                resolved["lora_scale"] = 0.0
        
        # Other parameters with defaults
        resolved.update({
            "color_correction_strength": params.get("color_correction_strength") if params.get("color_correction_strength") is not None else 0.2,
            "num_persistent_param_in_dit": params.get("num_persistent_param_in_dit") if params.get("num_persistent_param_in_dit") is not None else 0,
            "seed": params.get("seed") if params.get("seed") is not None else -1,  # -1 means random
            "frame_num": params.get("frame_num"),  # None means auto-calculate
            # Logic: If param is None, use preset default (which is True for Fast, False for Quality)
            # If param is explicitly False, use False.
            "use_quantization": params.get("use_quantization") if params.get("use_quantization") is not None else preset.get("use_quantization", False),
            "use_teacache": params.get("use_teacache", True),
            "teacache_thresh": params.get("teacache_thresh", 0.2),
            "use_apg": params.get("use_apg", True),
            "motion_frame": 9,  # Fixed optimal value
            
            # Metadata for tracking
            "preset_used": preset_name,
            "resolution_used": resolution,
        })
        
        return resolved
    
    @staticmethod
    def get_lora_config(use_lora: bool, lora_scale: float) -> tuple:
        """
        Get LoRA directory and scale configuration.
        
        Args:
            use_lora: Whether to use LoRA
            lora_scale: LoRA scale value
        
        Returns:
            Tuple of (lora_dir, lora_scale) or (None, None)
        """
        if use_lora and lora_scale > 0:
            lora_dir = ["/models/FusionX_LoRa/FusionX_LoRa/Wan2.1_I2V_14B_FusionX_LoRA.safetensors"]
            return lora_dir, [lora_scale]
        return None, None
    
    @staticmethod
    def get_quantization_config(use_quantization: bool, is_multi_person: bool = False) -> tuple:
        """
        Get quantization configuration.
        
        Args:
            use_quantization: Whether to use FP8 quantization
            is_multi_person: Whether it is a multi-person model
        
        Returns:
            Tuple of (quant, quant_dir) or (None, None)
        """
        if use_quantization:
            if is_multi_person:
                return "fp8", "/models/InfiniteTalk/quant_models/infinitetalk_multi_fp8.safetensors"
            else:
                return "fp8", "/models/InfiniteTalk/quant_models/infinitetalk_single_fp8.safetensors"
        return None, None
    
    @staticmethod
    def validate_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate user parameters.
        
        Args:
            params: User-provided parameters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate quality_preset
        if "quality_preset" in params:
            if params["quality_preset"] not in QUALITY_PRESETS:
                return False, f"Invalid quality_preset. Must be one of: {list(QUALITY_PRESETS.keys())}"
        
        # Validate resolution
        if "resolution" in params:
            if params["resolution"] not in RESOLUTION_CONFIGS:
                return False, f"Invalid resolution. Must be one of: {list(RESOLUTION_CONFIGS.keys())}"
        
        # Validate sample_steps
        if params.get("sample_steps") is not None:
            steps = params["sample_steps"]
            if not isinstance(steps, int) or steps < 1 or steps > 50:
                return False, "sample_steps must be between 1 and 50"
        
        # Validate frame_num (must be 4n+1)
        if "frame_num" in params and params["frame_num"] is not None:
            frame_num = params["frame_num"]
            if (frame_num - 1) % 4 != 0:
                return False, f"frame_num must be 4n+1 (e.g., 1, 5, 9, 81, 85). Got {frame_num}"
        
        # Validate scales
        for scale_param in ["sample_text_guide_scale", "sample_audio_guide_scale", "lora_scale"]:
            if params.get(scale_param) is not None:
                value = params[scale_param]
                if not isinstance(value, (int, float)) or value < 0 or value > 20:
                    return False, f"{scale_param} must be between 0 and 20"
        
        # Validate color_correction_strength
        if params.get("color_correction_strength") is not None:
            value = params["color_correction_strength"]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                return False, "color_correction_strength must be between 0 and 1"
        
        return True, None