# 📖 Story Forge – AI Story Generator

**Turn your imagination into stories with AI.**

Story Forge is an AI-powered story generation application that creates creative stories from text prompts and uploaded images. Users can customize their stories based on genre, mood, character emotion and length, continue existing stories, listen to AI-generated narration, and download stories in PDF or DOCX formats.

## ✨ Features

- **Text-to-Story Generation:** Generate creative stories using your own opening line.
- **Image-to-Story Generation:** Upload images and transform visual inspiration into stories using Google Gemini.
- **Customizable Stories:** Choose from different genres, moods, character emotions and story lengths.
- **Story Continuation:** Continue previously generated stories with additional paragraphs.
- **AI Narration:** Listen to generated stories using Google Text-to-Speech or Gemini voice narration.
- **Download Stories:** Export stories as PDF and DOCX files.
- **Story History:** Access previously generated stories during your session.
- **Dark & Light Themes:** Switch between themes for a comfortable reading experience.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | User interface |
| OpenRouter API | AI text generation |
| Google Gemini API | Image-based story generation and voice narration |
| gTTS | Text-to-speech narration |
| FPDF2 | PDF generation |
| python-docx | DOCX generation |
| Pillow (PIL) | Image processing |

## 📂 Project Structure

```text
story-forge/
│
├── main.py              # Main Streamlit application
├── utils.py             # Story utilities, API calls and exports
├── gemini_helper.py     # Gemini integration
├── requirements.txt     # Project dependencies
├── DejaVuSans.ttf       # Unicode font for PDF generation
├── .gitignore           # Git ignored files
└── README.md            # Project documentation
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sam3403/story-forge.git
```

### 2. Navigate to the project directory

```bash
cd story-forge
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API keys

Create a `.env` file in the project root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
GOOGLE_API_KEY=your_google_api_key
```

Get your API keys:

- [OpenRouter API](https://openrouter.ai/)
- [Google AI Studio](https://aistudio.google.com/)

**Note:** Keep your API keys private. Never commit your `.env` file to GitHub.

### 6. Run the application

```bash
streamlit run main.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## ☁️ Deployment

Story Forge can be deployed using Streamlit Community Cloud.

1. Push the project to a GitHub repository.
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your GitHub repository.
4. Select `main.py` as the application entry point.
5. Configure the required API keys under App Settings → Secrets.
6. Deploy the application.

Add the following to Streamlit Secrets:

```toml
OPENROUTER_API_KEY = "your_openrouter_api_key"
GOOGLE_API_KEY = "your_google_api_key"
```

## 🔮 Future Improvements

- More narration voices and language options.
- Improved story editing and formatting.
- Enhanced story history with persistent storage.
- Additional AI models and generation options.
- More customization options for storytelling.

## 👨‍💻 Author

**Samuel**

GitHub: [@sam3403](https://github.com/sam3403)

---

⭐ If you find Story Forge interesting, consider giving the repository a star!

**Story Forge – Where imagination meets AI.**