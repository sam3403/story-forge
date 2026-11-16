import os
import requests
from fpdf import FPDF
from docx import Document
from io import BytesIO
from gtts import gTTS

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# MODEL = "arcee-ai/trinity-large-preview:free"  # or your preferred model
MODEL= "mistralai/mistral-small-2603"

def generate_openrouter(prompt, max_tokens=400):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Story Generator",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.75,
    }

    try:
        r = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if r.status_code != 200:
            return f"[OpenRouter error {r.status_code}] {r.text}"

        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"[OpenRouter connection error] {str(e)}"

    except (KeyError, IndexError, ValueError) as e:
        return f"[OpenRouter response error] {str(e)}"

def convert_to_pdf(title, text, buffer: BytesIO = None):
    pdf = FPDF()
    pdf.add_page()
    
    print("Trying to access font file...")
    print("File exists?", os.path.exists("DejaVuSans.ttf"))
    print("Can read it?", os.access("DejaVuSans.ttf", os.R_OK))
    print("Current folder:", os.getcwd())

    # Load Unicode font (must be in same folder as main.py)
    pdf.add_font(family="DejaVu", style="", fname="DejaVuSans.ttf", uni=True)

    # Title
    pdf.set_font("DejaVu", size=16)
    pdf.cell(0, 10, title, ln=1, align="C")
    pdf.ln(10)

    # Body text
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 8, text)

    if buffer:
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    else:
        pdf.output("temp_story.pdf")
        return "temp_story.pdf"

def convert_to_docx(title, story):
    doc = Document()
    doc.add_heading(title, 0)
    for p in story.split("\n\n"):
        doc.add_paragraph(p)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generate_gtts_audio(text, lang='en'):
    tts = gTTS(text, lang=lang)
    fname = "temp_audio.mp3"
    tts.save(fname)
    return fname