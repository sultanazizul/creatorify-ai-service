# InfiniteTalk Quality Presets Configuration

"""
Quality presets for InfiniteTalk video generation.
Each preset optimizes different aspects: speed vs quality.
"""

from typing import Dict, Any

# Quality Presets
QUALITY_PRESETS: Dict[str, Dict[str, Any]] = {
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
        "num_persistent_param_in_dit": 0,
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
        "use_quantization": False,
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
        "num_persistent_param_in_dit": 0,
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
    preset_config = QUALITY_PRESETS.get(preset, QUALITY_PRESETS["fast"])
    
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
    
    return VRAM_REQUIREMENTS.get(key, "20GB")