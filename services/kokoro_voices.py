"""
Kokoro TTS voice and language data.
Contains all available voices and languages for the Kokoro-82M model.
"""

# Language definitions
LANGUAGES = {
    "a": {
        "code": "a",
        "name": "American English",
        "full_code": "en-us",
        "g2p": "misaki[en]",
        "fallback": "espeak-ng en-us"
    },
    "b": {
        "code": "b",
        "name": "British English",
        "full_code": "en-gb",
        "g2p": "misaki[en]",
        "fallback": "espeak-ng en-gb"
    },
    "e": {
        "code": "e",
        "name": "Spanish",
        "full_code": "es",
        "g2p": "espeak-ng",
        "fallback": "espeak-ng es"
    },
    "f": {
        "code": "f",
        "name": "French",
        "full_code": "fr-fr",
        "g2p": "espeak-ng",
        "fallback": "espeak-ng fr-fr"
    },
    "h": {
        "code": "h",
        "name": "Hindi",
        "full_code": "hi",
        "g2p": "espeak-ng",
        "fallback": "espeak-ng hi"
    },
    "i": {
        "code": "i",
        "name": "Italian",
        "full_code": "it",
        "g2p": "espeak-ng",
        "fallback": "espeak-ng it"
    },
    "p": {
        "code": "p",
        "name": "Brazilian Portuguese",
        "full_code": "pt-br",
        "g2p": "espeak-ng",
        "fallback": "espeak-ng pt-br"
    },
    "j": {
        "code": "j",
        "name": "Japanese",
        "full_code": "ja",
        "g2p": "misaki[ja]",
        "fallback": None
    },
    "z": {
        "code": "z",
        "name": "Mandarin Chinese",
        "full_code": "zh",
        "g2p": "misaki[zh]",
        "fallback": None
    }
}

# Voice definitions organized by language
VOICES = {
    "a": [  # American English
        {"id": "af_heart", "name": "Heart (Female)", "gender": "female", "lang": "a"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "female", "lang": "a"},
        {"id": "af_sarah", "name": "Sarah (Female)", "gender": "female", "lang": "a"},
        {"id": "af_nicole", "name": "Nicole (Female)", "gender": "female", "lang": "a"},
        {"id": "af_sky", "name": "Sky (Female)", "gender": "female", "lang": "a"},
        {"id": "af", "name": "AF (Female)", "gender": "female", "lang": "a"},
        {"id": "am_adam", "name": "Adam (Male)", "gender": "male", "lang": "a"},
        {"id": "am_michael", "name": "Michael (Male)", "gender": "male", "lang": "a"},
        {"id": "am", "name": "AM (Male)", "gender": "male", "lang": "a"},
    ],
    "b": [  # British English
        {"id": "bf_emma", "name": "Emma (Female)", "gender": "female", "lang": "b"},
        {"id": "bf_isabella", "name": "Isabella (Female)", "gender": "female", "lang": "b"},
        {"id": "bf", "name": "BF (Female)", "gender": "female", "lang": "b"},
        {"id": "bm_george", "name": "George (Male)", "gender": "male", "lang": "b"},
        {"id": "bm_lewis", "name": "Lewis (Male)", "gender": "male", "lang": "b"},
        {"id": "bm", "name": "BM (Male)", "gender": "male", "lang": "b"},
    ],
    "j": [  # Japanese
        {"id": "jf", "name": "JF (Female)", "gender": "female", "lang": "j"},
        {"id": "jm", "name": "JM (Male)", "gender": "male", "lang": "j"},
    ],
    "z": [  # Mandarin Chinese
        {"id": "zf", "name": "ZF (Female)", "gender": "female", "lang": "z"},
        {"id": "zm", "name": "ZM (Male)", "gender": "male", "lang": "z"},
    ],
    "e": [  # Spanish
        {"id": "ef", "name": "EF (Female)", "gender": "female", "lang": "e"},
        {"id": "em", "name": "EM (Male)", "gender": "male", "lang": "e"},
    ],
    "f": [  # French
        {"id": "ff", "name": "FF (Female)", "gender": "female", "lang": "f"},
    ],
    "h": [  # Hindi
        {"id": "hf", "name": "HF (Female)", "gender": "female", "lang": "h"},
        {"id": "hm", "name": "HM (Male)", "gender": "male", "lang": "h"},
    ],
    "i": [  # Italian
        {"id": "if", "name": "IF (Female)", "gender": "female", "lang": "i"},
        {"id": "im", "name": "IM (Male)", "gender": "male", "lang": "i"},
    ],
    "p": [  # Brazilian Portuguese
        {"id": "pf", "name": "PF (Female)", "gender": "female", "lang": "p"},
        {"id": "pm", "name": "PM (Male)", "gender": "male", "lang": "p"},
    ]
}

def get_all_languages():
    """Get list of all supported languages."""
    return list(LANGUAGES.values())

def get_all_voices():
    """Get list of all available voices across all languages."""
    all_voices = []
    for lang_code, voices in VOICES.items():
        all_voices.extend(voices)
    return all_voices

def get_voices_by_language(lang_code: str):
    """Get voices for a specific language."""
    return VOICES.get(lang_code, [])

def get_language_info(lang_code: str):
    """Get information about a specific language."""
    return LANGUAGES.get(lang_code)
