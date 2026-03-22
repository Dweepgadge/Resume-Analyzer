# 🚀 AI Resume Analyzer — Step-by-Step Guide

## Project Structure
```
resume_analyzer/
├── app.py              ← Flask backend (main file)
├── requirements.txt    ← Python dependencies
├── templates/
│   └── index.html      ← Frontend HTML
└── static/
    ├── css/style.css   ← Styling
    └── js/main.js      ← Frontend JavaScript
```

---

## STEP 1 — Python Install Karo
Python 3.8+ chahiye. Check karo:
```bash
python --version
```
Download: https://www.python.org/downloads/

---

## STEP 2 — Project Folder Banao
```bash
mkdir resume_analyzer
cd resume_analyzer
```

---

## STEP 3 — Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

---

## STEP 4 — Dependencies Install Karo
```bash
pip install -r requirements.txt
```

Required packages:
- `flask` — web framework
- `PyPDF2` — PDF parsing
- `python-docx` — DOCX parsing
- `nltk` — NLP tokenization

---

## STEP 5 — App Chalao
```bash
python app.py
```

Browser mein kholo: http://127.0.0.1:5000

---

## STEP 6 — Use Karo!
1. Resume paste karo ya file upload karo (.txt / .pdf / .docx)
2. Target role select karo (Data Analyst, Software Engineer, etc.)
3. "Analyze Resume" click karo
4. Results dekho:
   - ATS Score (0-100)
   - Keyword Match Score
   - Format Score
   - Impact Score
   - Missing Skills
   - Improvement Tips

---

## How It Works (Technical)

### Scoring System
| Score | Weight | What it checks |
|-------|--------|----------------|
| ATS Score | 35% | Sections, contact info, action verbs, numbers |
| Keyword Score | 35% | Role-specific skills match |
| Format Score | 15% | Line structure, special chars, length |
| Impact Score | 15% | Quantifiable results, strong verbs |

### Files Explained
- **app.py** → Flask server, scoring logic, API endpoint `/analyze`
- **index.html** → Resume input form + results display
- **style.css** → Visual design
- **main.js** → File upload, AJAX call, result rendering

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: flask` | Run `pip install flask` |
| Port already in use | Change port: `app.run(port=5001)` |
| PDF not reading | Install `pip install PyPDF2` |
| DOCX not reading | Install `pip install python-docx` |
| NLTK download error | Run Python: `import nltk; nltk.download('all')` |

---

## Extend Karo — Ideas
- Add login system (Flask-Login)
- Save results to database (SQLite / PostgreSQL)
- Add job description matching
- Export results as PDF report
- Deploy on Render / Railway / Heroku (free!)
