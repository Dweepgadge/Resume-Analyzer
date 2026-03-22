from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.utils import secure_filename

# ---- Try importing optional NLP libraries ----
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx as python_docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# =============================================
# SKILL DATABASE — Role ke liye required skills
# =============================================
ROLE_SKILLS = {
    "Data Analyst": {
        "required": ["python", "sql", "excel", "tableau", "power bi", "statistics",
                     "data visualization", "pandas", "numpy", "matplotlib", "r",
                     "machine learning", "data cleaning", "etl", "reporting"],
        "nice_to_have": ["spark", "hadoop", "aws", "azure", "looker", "google analytics"]
    },
    "Software Engineer": {
        "required": ["python", "java", "javascript", "git", "sql", "rest api",
                     "algorithms", "data structures", "agile", "docker", "linux",
                     "testing", "debugging", "oop", "ci/cd"],
        "nice_to_have": ["kubernetes", "microservices", "aws", "react", "node.js", "typescript"]
    },
    "Data Scientist": {
        "required": ["python", "machine learning", "deep learning", "tensorflow", "pytorch",
                     "scikit-learn", "statistics", "sql", "pandas", "numpy",
                     "feature engineering", "model evaluation", "nlp", "data visualization"],
        "nice_to_have": ["spark", "hadoop", "aws", "azure", "mlflow", "airflow", "docker"]
    },
    "Product Manager": {
        "required": ["product strategy", "roadmap", "agile", "scrum", "user stories",
                     "stakeholder management", "data analysis", "a/b testing",
                     "market research", "prioritization", "jira", "presentation"],
        "nice_to_have": ["sql", "figma", "ux research", "okrs", "gtm strategy", "analytics"]
    },
    "ML Engineer": {
        "required": ["python", "tensorflow", "pytorch", "scikit-learn", "docker",
                     "kubernetes", "mlops", "ci/cd", "sql", "machine learning",
                     "deep learning", "git", "aws", "model deployment", "rest api"],
        "nice_to_have": ["spark", "kafka", "airflow", "mlflow", "triton", "onnx"]
    },
    "Frontend Developer": {
        "required": ["javascript", "html", "css", "react", "git", "responsive design",
                     "typescript", "rest api", "testing", "webpack", "node.js",
                     "accessibility", "performance optimization", "figma"],
        "nice_to_have": ["vue", "angular", "graphql", "nextjs", "storybook", "tailwind css"]
    },
    "General": {
        "required": ["communication", "problem solving", "teamwork", "leadership",
                     "project management", "analytical thinking", "adaptability",
                     "time management", "documentation", "presentation"],
        "nice_to_have": ["agile", "scrum", "python", "excel", "sql", "git"]
    }
}

# ATS-friendly section keywords
ATS_SECTIONS = ["experience", "education", "skills", "summary", "objective",
                "projects", "certifications", "achievements", "publications", "contact"]

# Impact action verbs
ACTION_VERBS = ["achieved", "built", "created", "delivered", "developed", "drove",
                "enhanced", "established", "executed", "generated", "grew", "improved",
                "increased", "launched", "led", "managed", "optimized", "reduced",
                "saved", "scaled", "streamlined", "transformed"]

# Red flag keywords (negative signals)
WEAK_PHRASES = ["responsible for", "helped with", "worked on", "assisted",
                "tried to", "attempted to", "duties included"]


# =============================================
# UTILITY FUNCTIONS
# =============================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path, extension):
    """Extract plain text from uploaded file"""
    text = ""
    if extension == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

    elif extension == 'pdf' and PDF_AVAILABLE:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"

    elif extension == 'docx' and DOCX_AVAILABLE:
        doc = python_docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text


def tokenize_simple(text):
    """Simple tokenizer — fallback if NLTK not available"""
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.\-]*\b', text.lower())
    stop = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "is", "was", "are", "were", "be", "been",
            "have", "has", "had", "do", "did", "will", "would", "can", "could",
            "i", "my", "me", "we", "our", "you", "your", "it", "its"}
    return [w for w in words if w not in stop and len(w) > 1]


def get_tokens(text):
    if NLTK_AVAILABLE:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        return [t for t in tokens if t.isalnum() and t not in stop_words]
    return tokenize_simple(text)


# =============================================
# SCORING ENGINE
# =============================================

def calculate_ats_score(text):
    """Score ATS compatibility based on structure & keywords"""
    text_lower = text.lower()
    score = 0
    details = []

    # 1. Section headers (30 pts)
    found_sections = [s for s in ATS_SECTIONS if s in text_lower]
    section_score = min(30, len(found_sections) * 4)
    score += section_score
    details.append(f"Sections found: {len(found_sections)}/{len(ATS_SECTIONS)}")

    # 2. Contact info (20 pts)
    contact_score = 0
    if re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]+', text):
        contact_score += 7
    if re.search(r'(\+?\d[\d\s\-().]{8,})', text):
        contact_score += 6
    if re.search(r'linkedin\.com', text_lower):
        contact_score += 4
    if re.search(r'github\.com', text_lower):
        contact_score += 3
    score += contact_score
    details.append(f"Contact info score: {contact_score}/20")

    # 3. Length check (15 pts)
    word_count = len(text.split())
    if 300 <= word_count <= 800:
        length_score = 15
    elif word_count < 300:
        length_score = max(0, word_count // 30)
    else:
        length_score = max(5, 15 - (word_count - 800) // 100)
    score += length_score
    details.append(f"Word count: {word_count} words")

    # 4. Action verbs (20 pts)
    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    verb_score = min(20, len(found_verbs) * 3)
    score += verb_score
    details.append(f"Action verbs used: {len(found_verbs)}")

    # 5. Quantifiable achievements (15 pts)
    numbers = re.findall(r'\b\d+%|\$\d+|\d+\+|\d+x\b|\d{4}\b', text)
    quant_score = min(15, len(numbers) * 3)
    score += quant_score
    details.append(f"Quantifiable results: {len(numbers)}")

    # Penalize weak phrases
    weak_found = [w for w in WEAK_PHRASES if w in text_lower]
    penalty = len(weak_found) * 3
    score = max(0, score - penalty)
    if weak_found:
        details.append(f"Weak phrases found (penalty): {weak_found[:3]}")

    return min(100, score), details


def calculate_keyword_score(text, role):
    """Match resume keywords against role requirements"""
    text_lower = text.lower()
    skills_data = ROLE_SKILLS.get(role, ROLE_SKILLS["General"])
    required = skills_data["required"]
    nice_to_have = skills_data["nice_to_have"]

    found_required = [s for s in required if s in text_lower]
    found_nice = [s for s in nice_to_have if s in text_lower]
    missing_required = [s for s in required if s not in text_lower]

    if required:
        req_score = (len(found_required) / len(required)) * 80
    else:
        req_score = 40

    if nice_to_have:
        nice_score = (len(found_nice) / len(nice_to_have)) * 20
    else:
        nice_score = 10

    keyword_score = min(100, int(req_score + nice_score))

    return {
        "score": keyword_score,
        "found_skills": found_required + found_nice,
        "missing_skills": missing_required[:8],
        "found_count": len(found_required),
        "total_required": len(required)
    }


def calculate_format_score(text):
    """Evaluate formatting quality"""
    score = 0

    # Check for proper line breaks / structure
    lines = [l for l in text.split('\n') if l.strip()]
    if len(lines) > 10:
        score += 25

    # No tables (ATS unfriendly)
    if '|' not in text and '\t\t' not in text:
        score += 20

    # Consistent capitalization (not ALL CAPS)
    all_caps_lines = sum(1 for l in lines if l.isupper() and len(l) > 5)
    if all_caps_lines < 3:
        score += 15

    # Not too many special characters
    special = len(re.findall(r'[★◆▶▪•■]', text))
    if special < 10:
        score += 15

    # Reasonable line lengths
    avg_len = sum(len(l) for l in lines) / max(len(lines), 1)
    if 30 < avg_len < 120:
        score += 25

    return min(100, score)


def generate_suggestions(text, role, ats_score, keyword_data):
    """Generate personalized improvement suggestions"""
    suggestions = []
    text_lower = text.lower()

    if ats_score < 50:
        suggestions.append("Add clear section headers: EXPERIENCE, EDUCATION, SKILLS, SUMMARY.")

    if not re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]+', text):
        suggestions.append("Add your email address at the top of the resume.")

    if not re.search(r'linkedin\.com', text_lower):
        suggestions.append("Include your LinkedIn profile URL to boost credibility.")

    weak_found = [w for w in WEAK_PHRASES if w in text_lower]
    if weak_found:
        suggestions.append(
            f"Replace weak phrases like '{weak_found[0]}' with strong action verbs "
            f"(built, achieved, delivered, improved)."
        )

    numbers = re.findall(r'\b\d+%|\$\d+|\d+\+', text)
    if len(numbers) < 3:
        suggestions.append(
            "Add quantifiable results — e.g. 'Improved performance by 40%' or "
            "'Managed a team of 8 engineers'."
        )

    if keyword_data["missing_skills"]:
        top_missing = keyword_data["missing_skills"][:4]
        suggestions.append(
            f"Add missing {role} skills to your Skills section: "
            f"{', '.join(top_missing)}."
        )

    word_count = len(text.split())
    if word_count < 300:
        suggestions.append(
            f"Your resume is too short ({word_count} words). "
            "Aim for 400-700 words with detailed bullet points."
        )
    elif word_count > 900:
        suggestions.append(
            f"Your resume is too long ({word_count} words). "
            "Trim to 1-2 pages (400-700 words)."
        )

    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    if len(found_verbs) < 5:
        suggestions.append(
            "Start each bullet point with a strong action verb: "
            "Built, Led, Optimized, Delivered, Scaled."
        )

    if not re.search(r'github\.com', text_lower) and role in ["Software Engineer", "Data Scientist", "ML Engineer"]:
        suggestions.append("Add your GitHub profile link — recruiters actively check it for technical roles.")

    if len(suggestions) == 0:
        suggestions.append("Great resume! Consider tailoring keywords for each specific job description.")

    return suggestions[:6]


# =============================================
# FLASK ROUTES
# =============================================

@app.route('/')
def index():
    return render_template('index.html', roles=list(ROLE_SKILLS.keys()))


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = ""

    # File upload
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({"error": "Only .txt, .pdf, .docx files allowed"}), 400

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        resume_text = extract_text_from_file(filepath, ext)
        os.remove(filepath)  # cleanup

    # Pasted text
    elif 'resume_text' in request.form:
        resume_text = request.form['resume_text'].strip()

    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Please provide a resume with at least 50 characters"}), 400

    role = request.form.get('role', 'General')
    if role not in ROLE_SKILLS:
        role = 'General'

    # Run all scoring
    ats_score, ats_details = calculate_ats_score(resume_text)
    keyword_data = calculate_keyword_score(resume_text, role)
    format_score = calculate_format_score(resume_text)
    suggestions = generate_suggestions(resume_text, role, ats_score, keyword_data)

    # Impact score based on action verbs and numbers
    found_verbs = [v for v in ACTION_VERBS if v in resume_text.lower()]
    numbers = re.findall(r'\b\d+%|\$\d+|\d+\+|\d+x\b', resume_text)
    impact_score = min(100, len(found_verbs) * 7 + len(numbers) * 5)

    # Overall score (weighted average)
    overall = int(
        ats_score * 0.35 +
        keyword_data["score"] * 0.35 +
        format_score * 0.15 +
        impact_score * 0.15
    )

    result = {
        "overall_score": overall,
        "ats_score": ats_score,
        "keyword_score": keyword_data["score"],
        "format_score": format_score,
        "impact_score": impact_score,
        "skills_found": keyword_data["found_skills"][:10],
        "skills_missing": keyword_data["missing_skills"][:8],
        "suggestions": suggestions,
        "role": role,
        "word_count": len(resume_text.split()),
        "ats_details": ats_details
    }

    return jsonify(result)


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print("Starting Resume Analyzer — http://127.0.0.1:5000")
    app.run(debug=True)
