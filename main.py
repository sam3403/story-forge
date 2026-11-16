import io
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

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

st.set_page_config(
    page_title="AI Story Studio",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- Theme ---------------------------
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "Dark"

with st.sidebar:
    st.markdown("<div class='brand-mark'>✦</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-name'>STORY<span>FORGE</span></div>", unsafe_allow_html=True)
    st.caption("YOUR CREATIVE AI STUDIO")
    st.divider()
    st.markdown("#### Appearance")
    st.session_state.ui_theme = st.radio(
        "Choose theme",
        ["Dark", "Light"],
        index=0 if st.session_state.ui_theme == "Dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )

is_dark = st.session_state.ui_theme == "Dark"
if is_dark:
    colors = {
        "bg": "#0b0b12", "panel": "#141420", "panel2": "#1b1a2a",
        "text": "#f4f1ff", "muted": "#aaa6bd", "border": "rgba(190,175,255,.14)",
        "accent": "#a78bfa", "accent2": "#7c3aed", "input": "#191827",
        "shadow": "0 18px 55px rgba(0,0,0,.24)",
    }
else:
    colors = {
        "bg": "#f7f6fb", "panel": "#ffffff", "panel2": "#f0edfa",
        "text": "#211d32", "muted": "#716b82", "border": "rgba(76,55,125,.14)",
        "accent": "#7c3aed", "accent2": "#6d28d9", "input": "#f5f3fa",
        "shadow": "0 18px 55px rgba(49,35,82,.08)",
    }

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root {{ --bg:{colors['bg']}; --panel:{colors['panel']}; --panel2:{colors['panel2']};
      --text:{colors['text']}; --muted:{colors['muted']}; --border:{colors['border']};
      --accent:{colors['accent']}; --accent2:{colors['accent2']}; --input:{colors['input']};
      --shadow:{colors['shadow']}; }}
    html, body, [data-testid="stAppViewContainer"] {{ background:var(--bg); color:var(--text); }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stToolbar"] {{ right:1rem; }}
    [data-testid="stSidebar"] {{ background:var(--panel); border-right:1px solid var(--border); }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top:1.4rem; }}
    .block-container {{ max-width:1240px; padding-top:2.2rem; padding-bottom:4rem; }}
    * {{ font-family:'DM Sans',sans-serif; }}
    h1,h2,h3,h4 {{ font-family:'Manrope',sans-serif !important; color:var(--text) !important; letter-spacing:-.035em; }}
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {{ color:var(--text); }}
    [data-testid="stCaptionContainer"] {{ color:var(--muted) !important; }}
    .brand-mark {{ width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;
      background:linear-gradient(135deg,#c4b5fd,#7c3aed);color:white;font-size:24px;margin-bottom:10px;box-shadow:0 8px 25px #7c3aed44; }}
    .brand-name {{ font:800 19px Manrope,sans-serif;letter-spacing:.08em;color:var(--text); }}
    .brand-name span {{ color:var(--accent); }}
    .hero {{ position:relative; overflow:hidden; padding:34px 38px; border:1px solid var(--border); border-radius:26px;
      background:radial-gradient(circle at 82% 5%, #8b5cf633, transparent 30%), linear-gradient(125deg,var(--panel),var(--panel2));
      box-shadow:var(--shadow); margin-bottom:26px; }}
    .eyebrow {{ color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;margin-bottom:12px; }}
    .hero h1 {{ font-size:clamp(34px,4vw,52px);line-height:1.08;margin:0 0 12px 0; }}
    .hero p {{ color:var(--muted);font-size:16px;margin:0;max-width:650px; }}
    .hero-orb {{ position:absolute;right:7%;top:15%;width:150px;height:150px;border-radius:50%;
      background:radial-gradient(circle at 35% 30%,#ddd6fe,#8b5cf6 48%,#4c1d95);filter:blur(.2px);opacity:.8;
      box-shadow:0 0 80px #8b5cf655; }}
    .section-kicker {{ color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;margin:4px 0 8px; }}
    .panel {{ background:var(--panel);border:1px solid var(--border);border-radius:22px;padding:24px;box-shadow:var(--shadow); }}
    .panel-subtitle {{ color:var(--muted);font-size:13px;margin-top:-6px;margin-bottom:18px; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {{
      background:var(--input);border:1px solid var(--border);border-radius:12px;color:var(--text); }}
    input, textarea {{ color:var(--text) !important; }}
    [data-testid="stFileUploader"] section {{ background:var(--input);border:1px dashed var(--accent) !important;border-radius:15px; }}
    .stButton > button, .stDownloadButton > button {{ border-radius:12px;border:1px solid var(--border);font-weight:700;
      min-height:44px;transition:all .18s ease;background:var(--panel2);color:var(--text); }}
    .stButton > button:hover, .stDownloadButton > button:hover {{ border-color:var(--accent);color:var(--accent);transform:translateY(-1px); }}
    div[data-testid="stButton"] button[kind="primary"] {{ background:linear-gradient(100deg,var(--accent2),var(--accent));color:white;border:0; }}
    div[data-testid="stButton"] button[kind="primary"]:hover {{ color:white;box-shadow:0 8px 24px #7c3aed44; }}
    [data-testid="stRadio"] label {{ color:var(--text) !important; }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {{ margin-top:8px; }}
    .story-card {{ background:var(--panel);border:1px solid var(--border);border-radius:22px;padding:30px;
      box-shadow:var(--shadow);line-height:1.85; }}
    .story-label {{ color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase; }}
    .story-title {{ font:800 30px Manrope,sans-serif;color:var(--text);margin:8px 0 20px; }}
    .small-note {{ color:var(--muted);font-size:12px; }}
    hr {{ border-color:var(--border) !important; }}
    [data-testid="stAlert"] {{ border-radius:14px; }}
    @media(max-width:700px) {{ .hero {{ padding:26px 22px; }} .hero-orb {{ opacity:.22;right:-30px; }} .panel {{ padding:18px; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- State ---------------------------
for key, default in {
    "story": "", "title": "", "history": [], "continue_clicked": False,
    "reset_flag": False, "last_mode": "text",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------- Sidebar history ---------------------------
with st.sidebar:
    st.divider()
    st.markdown("#### ◷ Story library")
    st.caption("Your previously created stories")
    if st.session_state.history:
        history_options = ["Choose a saved story"] + [
            f"{i + 1}. {item['title']}" for i, item in enumerate(st.session_state.history)
        ]
        selected_history = st.selectbox("Saved stories", history_options, label_visibility="collapsed")
        if selected_history != "Choose a saved story":
            history_idx = int(selected_history.split(".", 1)[0]) - 1
            saved = st.session_state.history[history_idx]
            st.session_state.story = saved["story"]
            st.session_state.title = saved["title"]
    else:
        st.markdown("<div class='small-note'>Your story collection is empty. Create your first story to see it here.</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='small-note'>STORYFORGE · Create something unforgettable.</div>", unsafe_allow_html=True)

# --------------------------- Main header ---------------------------
st.markdown(
    """
    <div class="hero">
      <div class="hero-orb"></div>
      <div class="eyebrow">A little imagination goes a long way</div>
      <h1>Your next story<br>starts here.</h1>
      <p>Turn a first line or an image into a world worth getting lost in. Create, continue, listen and download.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY is missing from your .env file. Add it to enable text-based story generation.")

# --------------------------- Story creation ---------------------------
left, right = st.columns([1.15, 0.85], gap="large")
with left:
    st.markdown("<div class='section-kicker'>01 / Create</div>", unsafe_allow_html=True)
    st.markdown("## Build your story")
    st.markdown("<div class='panel-subtitle'>Choose the ingredients. We'll take care of the storytelling.</div>", unsafe_allow_html=True)
    with st.container(border=True):
        use_image_mode = st.toggle("Create from images · Gemini", value=False)
        genre = st.selectbox("Genre", ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Comedy", "Horror", "Other"], index=0)
        character = st.text_input("Main character (optional)", placeholder="e.g. Mira, a curious astronaut")
        c1, c2 = st.columns(2)
        with c1:
            mood = st.selectbox("Tone / mood", ["Light", "Whimsical", "Mysterious", "Dramatic", "Dark"], index=0)
        with c2:
            emotion = st.selectbox("Character emotion", ["Neutral", "Happy", "Nervous", "Confident", "Sad", "Angry", "Excited", "Scared"], index=0)
        length = st.select_slider("Story length", options=["Short", "Medium", "Long"], value="Medium")
        length_map = {"Short": 350, "Medium": 650, "Long": 1000}
        if use_image_mode:
            uploaded_files = st.file_uploader("Drop in 1–10 inspiration images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
            if uploaded_files:
                if len(uploaded_files) > 10:
                    st.warning("Only the first 10 images will be used.")
                    uploaded_files = uploaded_files[:10]
                st.image([Image.open(file) for file in uploaded_files], caption=None, width=125)
            start_prompt = ""
        else:
            uploaded_files = []
            start_prompt = st.text_area("Opening line", height=115, placeholder="Type the very first line. Your story will begin with it...")

        use_gemini_tts = False
        gemini_voice = None
        lang_code = "en-US"
        if use_image_mode and GOOGLE_API_KEY:
            use_gemini_tts = st.checkbox("Use Gemini premium narration", value=False)
            if use_gemini_tts:
                lang_options = {"English (US)": "en-US"}
                selected_lang_name = st.selectbox("Narration language", list(lang_options.keys()))
                lang_code = lang_options[selected_lang_name]
                voices = get_gemini_voices(lang_code)
                if voices:
                    voice_names = [voice["name"] for voice in voices]
                    voice_idx = st.selectbox("Narrator voice", range(len(voices)), format_func=lambda i: voice_names[i])
                    gemini_voice = voices[voice_idx]["id"]

        generate_clicked = st.button("✦  Generate my story", type="primary", use_container_width=True)

with right:
    st.markdown("<div class='section-kicker'>02 / Your creative brief</div>", unsafe_allow_html=True)
    st.markdown("## Set the atmosphere")
    with st.container(border=True):
        st.markdown("### ✧ Your story ingredients")
        st.markdown(f"**Genre**  ·  {genre}")
        st.markdown(f"**Mood**  ·  {mood}")
        st.markdown(f"**Emotion**  ·  {emotion}")
        st.markdown(f"**Length**  ·  {length} · about {length_map[length]} words")
        st.divider()
        st.markdown("### A few creative tips")
        st.markdown("- Start with a line that raises a question.\n- Give your character something to want.\n- Mix an unexpected setting with a familiar emotion.")
        st.caption("Your selections are used as guidance for the story generator.")

# --------------------------- Generation ---------------------------
def is_api_error(value):
    return isinstance(value, str) and value.strip().startswith("[OpenRouter error")

if generate_clicked:
    if use_image_mode:
        if not uploaded_files:
            st.error("Upload at least one image to create an image-inspired story.")
            st.stop()
        if not GOOGLE_API_KEY:
            st.error("GOOGLE_API_KEY is missing from your .env file. Add it to enable image mode.")
            st.stop()
        with st.spinner("Gemini is finding a story in your images..."):
            try:
                pil_images = [Image.open(file).convert("RGB") for file in uploaded_files]
                story_result = generate_story_from_images(
                    pil_images, genre=genre, mood=mood, emotion=emotion,
                    character=character, approx_words=length_map[length]
                )
                if isinstance(story_result, str) and story_result.strip():
                    st.session_state.story = story_result
                    st.session_state.last_mode = "image"
                else:
                    st.error("Gemini did not return a story. Please try again.")
                    st.stop()
            except Exception as exc:
                st.error(f"Image story generation failed: {exc}")
                st.stop()
    else:
        if not OPENROUTER_API_KEY:
            st.error("Add OPENROUTER_API_KEY to your .env file before generating a text story.")
            st.stop()
        if not start_prompt.strip():
            st.error("Please enter an opening line first.")
            st.stop()
        with st.spinner("Writing your story... the first draft is taking shape."):
            setting_desc = generate_openrouter(
                f"2-3 line vivid description of a {genre.lower()} {mood.lower()} setting.", 120
            )
            if is_api_error(setting_desc):
                st.error(setting_desc)
                st.stop()
            story_prompt = f"""First line (use exactly once): {start_prompt}

Continue in {genre} genre, {mood.lower()} tone.
Character emotion: {emotion}.
Character name: {character or 'the protagonist'}.

{setting_desc}

Write approximately {length_map[length]} words. End properly."""
            story_text = generate_openrouter(story_prompt, length_map[length] + 80)
            if is_api_error(story_text):
                st.error(story_text)
                st.stop()
            st.session_state.story = setting_desc + "\n\n" + story_text
            st.session_state.last_mode = "text"

    if st.session_state.story:
        with st.spinner("Giving your story a title..."):
            title_result = generate_openrouter(
                f"Short creative title (just the title):\n\n{st.session_state.story[:800]}", 50
            )
        if is_api_error(title_result):
            st.session_state.title = "A Story of Possibility"
            st.warning("Your story was created, but automatic title generation failed. You can still read and download it.")
        else:
            st.session_state.title = title_result.strip().strip('"') or "Untitled Story"
        st.rerun()

# --------------------------- Story output ---------------------------
if st.session_state.story:
    st.markdown("<div class='section-kicker'>03 / The finished draft</div>", unsafe_allow_html=True)
    st.markdown("## Your story is ready")
    with st.container(border=True):
        st.markdown("<div class='story-label'>STORYFORGE ORIGINAL</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='story-title'>{st.session_state.title or 'Untitled Story'}</div>", unsafe_allow_html=True)
        st.markdown(st.session_state.story)

    action1, action2, action3 = st.columns(3)
    with action1:
        if st.button("↗  Continue story", use_container_width=True):
            if st.session_state.last_mode == "image":
                st.info("Continue is currently available for text-generated stories.")
            else:
                with st.spinner("Continuing the story..."):
                    next_paragraph = generate_openrouter(
                        f"Continue the story with one more engaging paragraph.\n\n{st.session_state.story}", 250
                    )
                if is_api_error(next_paragraph):
                    st.error(next_paragraph)
                else:
                    st.session_state.story += "\n\n" + next_paragraph
                    st.rerun()
    with action2:
        if st.button("♫  Listen", use_container_width=True):
            if st.session_state.last_mode == "image" and use_gemini_tts and gemini_voice:
                with st.spinner("Gemini is narrating your story..."):
                    audio = narrate_story_gemini(st.session_state.story, lang_code, gemini_voice, emotion.lower())
                    if isinstance(audio, io.BytesIO):
                        st.audio(audio, format="audio/wav")
                    else:
                        st.error(audio)
            else:
                with st.spinner("Preparing audio narration..."):
                    try:
                        audio_path = generate_gtts_audio(st.session_state.story)
                        with open(audio_path, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/mp3")
                    except Exception as exc:
                        st.error(f"Audio generation failed: {exc}")
    with action3:
        if st.button("＋  Start a new story", use_container_width=True):
            if st.session_state.title and st.session_state.story:
                st.session_state.history.insert(0, {
                    "title": st.session_state.title,
                    "story": st.session_state.story,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            st.session_state.story = ""
            st.session_state.title = ""
            st.rerun()

    st.markdown("#### Take your story with you")
    download1, download2 = st.columns(2)
    with download1:
        try:
            pdf_buffer = io.BytesIO()
            convert_to_pdf(st.session_state.title or "Untitled Story", st.session_state.story, pdf_buffer)
            st.download_button(
                "↓  Download PDF", data=pdf_buffer.getvalue(),
                file_name=f"{(st.session_state.title or 'story').replace('/', '-')}.pdf",
                mime="application/pdf", use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF export failed: {exc}")
    with download2:
        try:
            docx_buffer = convert_to_docx(st.session_state.title or "Untitled Story", st.session_state.story)
            st.download_button(
                "↓  Download DOCX", data=docx_buffer,
                file_name=f"{(st.session_state.title or 'story').replace('/', '-')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"DOCX export failed: {exc}")
else:
    st.markdown(
        """<div class='panel' style='text-align:center;padding:38px 24px;margin-top:12px;'>
        <div style='font-size:36px;margin-bottom:10px;'>✧</div>
        <div style='font:700 20px Manrope,sans-serif;margin-bottom:7px;'>Your blank page is full of possibility.</div>
        <div class='small-note'>Choose your story ingredients and generate your first draft to see it here.</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='text-align:center;margin-top:42px' class='small-note'>MADE FOR THE STORIES ONLY YOU CAN IMAGINE · STORYFORGE</div>", unsafe_allow_html=True)
