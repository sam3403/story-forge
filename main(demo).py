import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image
import io

from utils import (
    generate_openrouter,
    convert_to_pdf,
    convert_to_docx,
    generate_gtts_audio,
)
from gemini_helper import (
    generate_story_from_images,
    narrate_story_gemini,
    get_gemini_voices,
)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY missing in .env")
    st.stop()

# ── Page config & theme ─────────────────────────────────────
st.set_page_config(page_title="AI Story Generator", page_icon="📖", layout="wide")

mode = st.sidebar.radio("🌓 Theme", ["Dark", "Light"], index=0)
if mode == "Dark":
    st.markdown("""<style> /* your dark css here - copy from original */ </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style> /* your light css here - copy from original */ </style>""", unsafe_allow_html=True)

st.title("📖 AI Story Generator")
st.markdown("Text or image inspired stories — continue, listen, download.")

# Session state
for key in ["story", "title", "history", "continue_clicked", "reset_flag"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key in ["story", "title"] else [] if key == "history" else False

# ── Sidebar history ─────────────────────────────────────────
st.sidebar.title("📚 Story History")
if st.session_state.history:
    titles = [f"{len(st.session_state.history)-i}. {h['title']}" for i, h in enumerate(st.session_state.history[::-1])]
    selected = st.sidebar.selectbox("", ["Select one"] + titles)
    if selected != "Select one":
        idx = int(selected.split(". ")[0]) - 1
        h = st.session_state.history[idx]
        st.session_state.story = h["story"]
        st.session_state.title = h["title"]
        st.session_state.continue_clicked = False

# ── Inputs ──────────────────────────────────────────────────
use_image_mode = st.checkbox("🖼️ Image-to-Story mode (uses Gemini)", value=False)

genre = st.selectbox("🎭 Genre", ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Comedy", "Horror", "Other"], index=0)
character = st.text_input("🧑 Character name (optional)", "")
mood = st.selectbox("🎨 Tone/Mood", ["Light", "Whimsical", "Mysterious", "Dramatic", "Dark"], index=0)
emotion = st.selectbox("💓 Character Emotion", ["Neutral", "Happy", "Nervous", "Confident", "Sad", "Angry", "Excited", "Scared"], index=0)

length = st.selectbox("🧱 Length", ["Short", "Medium", "Long"], index=1)
length_map = {"Short": 350, "Medium": 650, "Long": 1000}

if use_image_mode:
    uploaded_files = st.file_uploader("Upload 1–10 images", type=["jpg","jpeg","png"], accept_multiple_files=True)
    if uploaded_files and len(uploaded_files) > 10:
        st.error("Maximum 10 images allowed.")
        uploaded_files = uploaded_files[:10]
    if uploaded_files:
        st.image([Image.open(f) for f in uploaded_files], width=150)
else:
    start_prompt = st.text_area("✍ First line of the story", height=90, placeholder="Must start exactly with this...")

# Narration choice (only shown in image mode for Gemini TTS)
use_gemini_tts = False
gemini_voice = None
if use_image_mode and GOOGLE_API_KEY:
    use_gemini_tts = st.checkbox("Use premium Gemini voice narration (instead of gTTS)", value=False)
    if use_gemini_tts:
        lang_options = {"English (US)": "en-US"}  # can expand later
        selected_lang_name = st.selectbox("Narration language", list(lang_options.keys()))
        lang_code = lang_options[selected_lang_name]
        voices = get_gemini_voices(lang_code)
        if voices:
            voice_names = [v["name"] for v in voices]
            idx = st.selectbox("Voice", range(len(voices)), format_func=lambda i: voice_names[i])
            gemini_voice = voices[idx]["id"]

# ── Generate button ─────────────────────────────────────────
if st.button("🚀 Generate Story"):

    if use_image_mode:
        if not uploaded_files:
            st.error("Upload at least 1 image in Image mode.")
            st.stop()
        if not GOOGLE_API_KEY:
            st.error("GOOGLE_API_KEY required for image mode.")
            st.stop()

        with st.spinner("Gemini is writing the story..."):
            pil_images = [Image.open(f) for f in uploaded_files]
            story = generate_story_from_images(
                pil_images,
                genre=genre,
                mood=mood,
                emotion=emotion,
                character=character,
                approx_words=length_map[length]
            )
            st.session_state.story = story

    else:
        if not start_prompt.strip():
            st.error("Please provide the first line in text mode.")
            st.stop()

        with st.spinner("Generating..."):
            setting_desc = generate_openrouter(
                f"2-3 line vivid description of a {genre.lower()} {mood.lower()} setting.",
                120
            )
            story_prompt = f"""
First line (use exactly once): {start_prompt}

Continue in {genre} genre, {mood.lower()} tone.
Character emotion: {emotion}.
Character name: {character or 'the protagonist'}.

{setting_desc}

Write ~{length_map[length]} words. End properly.
"""
            story_text = generate_openrouter(story_prompt, length_map[length] + 80)
            st.session_state.story = setting_desc + "\n\n" + story_text

    # Title (use OpenRouter for both modes - consistent & cheap)
    if st.session_state.story:
        title = generate_openrouter(
            f"Short creative title (just the title):\n\n{st.session_state.story[:800]}",
            50
        )
        st.session_state.title = title.strip('"').strip()

    st.rerun()

# ── Show story + actions (same as original) ─────────────────
if st.session_state.story:
    st.subheader(st.session_state.title or "Untitled Story")
    st.markdown(st.session_state.story)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Continue Story"):
            if use_image_mode:
                st.info("Continue not implemented in image mode yet.")
            else:
                cont_prompt = f"Continue the story with one more paragraph.\n\n{st.session_state.story}"
                next_p = generate_openrouter(cont_prompt, 250)
                st.session_state.story += "\n\n" + next_p
                st.rerun()

    with col2:
        if st.button("🔊 Listen"):
            if use_image_mode and use_gemini_tts and gemini_voice:
                with st.spinner("Gemini narrating..."):
                    audio = narrate_story_gemini(st.session_state.story, "en-US", gemini_voice, emotion.lower())
                    if isinstance(audio, io.BytesIO):
                        st.audio(audio, format="audio/wav")
                    else:
                        st.error(audio)
            else:
                with st.spinner("gTTS narrating..."):
                    audio_path = generate_gtts_audio(st.session_state.story)
                    with open(audio_path, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")

    # Download buttons (same as original)
    if st.session_state.title and st.session_state.story:
        pdf_bytes = io.BytesIO()
        convert_to_pdf(st.session_state.title, st.session_state.story, pdf_bytes)
        st.download_button("📄 PDF", pdf_bytes.getvalue(), f"{st.session_state.title}.pdf")

        docx_buffer = convert_to_docx(st.session_state.title, st.session_state.story)
        st.download_button("📥 DOCX", docx_buffer, f"{st.session_state.title}.docx")

    if st.button("🔄 New Story"):
        if st.session_state.title and st.session_state.story:
            st.session_state.history.append({
                "title": st.session_state.title,
                "story": st.session_state.story,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        for k in ["story", "title"]:
            st.session_state[k] = ""
        st.rerun()