import os
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai
from PIL import Image
import base64
import io
import wave

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

GEMINI_VOICE_MAP = {
    "en-US": [
        {"id": "zephyr", "name": "Zephyr (Bright)"},
        {"id": "puck", "name": "Puck (Upbeat)"},
        {"id": "charon", "name": "Charon (Informative)"},
        {"id": "kore", "name": "Kore (Firm)"},
    ],
    # add others if needed
}

def get_gemini_voices(lang_code):
    return GEMINI_VOICE_MAP.get(lang_code, GEMINI_VOICE_MAP["en-US"])

def generate_story_from_images(images, genre, mood, emotion, character, approx_words):
    model = genai.GenerativeModel("gemini-2.5-flash") # or 1.5-pro

    prompt = f"""
You are a creative storyteller.
Genre: {genre}
Tone/mood: {mood}
Main character name: {character or "the protagonist"}
Character emotion: {emotion}

Write a complete, engaging story inspired by the uploaded images.
- Aim for approximately {approx_words} words
- Use Indian cultural context / names if it fits naturally
- Clear beginning, middle, end
- Do NOT describe images technically — weave them into the narrative naturally
- Start directly with the story (no separate description section unless it flows)
"""

    try:
        response = model.generate_content([*images, prompt])
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {str(e)}"

def narrate_story_gemini(story_text, lang_code, voice_name, emotion):
    model = genai.GenerativeModel("gemini-1.5-flash-preview-tts")  # adjust model name if needed

    narration_prompt = f"Narrate this story in a {emotion} tone:\n\n{story_text}"

    try:
        response = model.generate_content(
            narration_prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="audio/wav",
                voice=voice_name
            )
        )
        # Note: actual TTS API structure may vary — this is approximate
        # You might need to adjust based on current Gemini TTS response format
        audio_data = response.parts[0].audio.data  # placeholder — check docs

        if isinstance(audio_data, str):
            audio_bytes = base64.b64decode(audio_data)
        else:
            audio_bytes = audio_data

        buffer = io.BytesIO(audio_bytes)
        return buffer

    except Exception as e:
        return f"Gemini TTS error: {str(e)}"