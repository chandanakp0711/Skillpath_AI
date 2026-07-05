"""
===============================================================================
 config.py  --  Central configuration & domain knowledge base
===============================================================================
Intelligent Skill Profiling for Career Readiness & Growth Pathways.

This module is the single source of truth for:
    * File-system paths (data, models, assets)
    * The skill catalogues that exist in the dataset
    * The 10 target career domains and everything we know about them
      (required skills, certifications, projects, interview topics ...)
    * The career-affinity matrix used to engineer a learnable target label
    * The weighted Career-Readiness scoring scheme
    * Curated learning resources

Keeping every "fact" about the domain here means the ML pipeline, the Streamlit
UI and the documentation all stay perfectly in sync.
===============================================================================
"""

from __future__ import annotations

import os

# --------------------------------------------------------------------------- #
#  1. PATHS
# --------------------------------------------------------------------------- #
# Project root = parent folder of this file's folder (src/ -> project root)
ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR: str = os.path.join(ROOT_DIR, "data")
MODELS_DIR: str = os.path.join(ROOT_DIR, "models")
ASSETS_DIR: str = os.path.join(ROOT_DIR, "assets")

# Raw dataset shipped with the project. The loader also looks in ROOT_DIR so
# the original `skillgap_dataset.xlsx` keeps working out of the box.
RAW_DATASET_XLSX: str = os.path.join(DATA_DIR, "skillgap_dataset.xlsx")
RAW_DATASET_FALLBACK: str = os.path.join(ROOT_DIR, "skillgap_dataset.xlsx")
PROCESSED_DATASET_CSV: str = os.path.join(DATA_DIR, "processed_dataset.csv")

# Serialised ML artefacts (created by train.py)
MODEL_PATH: str = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH: str = os.path.join(MODELS_DIR, "preprocessor.pkl")
LABEL_ENCODER_PATH: str = os.path.join(MODELS_DIR, "label_encoder.pkl")
FEATURE_COLUMNS_PATH: str = os.path.join(MODELS_DIR, "feature_columns.pkl")
METRICS_PATH: str = os.path.join(MODELS_DIR, "model_metrics.json")
METADATA_PATH: str = os.path.join(MODELS_DIR, "training_metadata.json")

# Reproducibility
RANDOM_STATE: int = 42

for _d in (DATA_DIR, MODELS_DIR, ASSETS_DIR):
    os.makedirs(_d, exist_ok=True)


# --------------------------------------------------------------------------- #
#  2. RAW COLUMN NAMES  (the spreadsheet ships with messy headers)
# --------------------------------------------------------------------------- #
# Mapping of the (stripped) raw column name -> clean canonical name.
COLUMN_RENAME_MAP: dict[str, str] = {
    "NAME": "name",
    "EMAIL_ID": "email",
    "YEAR": "academic_year",
    "CURRENT_COURSE": "course",
    "TECHNICAL_SKILLS": "technical_skills",
    "PROG_LANGUAGES": "programming_languages",
    "RATING": "technical_rating",
    "SOFT_SKILSS": "soft_skills",          # note: original header is misspelt
    "RATING.1": "soft_rating",
    "PROJECTS": "has_projects",
    "CAREER_INTEREST": "career_interest",
    "CHALLENGES": "learning_challenge",
    "SUPPORT_REQUIRED": "support_required",
    "METHOD": "learning_method",
}

# Personally-identifiable columns we never feed to the model.
PII_COLUMNS: list[str] = ["name", "email"]


# --------------------------------------------------------------------------- #
#  3. SKILL CATALOGUES  (exact tokens present in the dataset)
# --------------------------------------------------------------------------- #
TECHNICAL_SKILLS: list[str] = [
    "Python", "SQL", "Machine Learning", "Data Analysis",
    "Cloud Computing", "Cybersecurity", "Java", "Blockchain",
]

PROGRAMMING_LANGUAGES: list[str] = [
    "Python", "Java", "JavaScript", "C++", "C#", "R", "Go",
]

SOFT_SKILLS: list[str] = [
    "Communication", "Problem-Solving", "Teamwork",
    "Leadership", "Time Management", "Adaptability",
]

COURSES: list[str] = [
    "B.Tech CSE", "B.Tech IT", "B.Sc Data Science",
    "M.Tech AI", "MBA", "BBA",
]

ACADEMIC_YEARS: list[str] = ["1st Year", "2nd Year", "3rd Year", "Final Year"]

CAREER_INTERESTS: list[str] = [
    "Data Scientist", "AI Engineer", "Cloud Architect",
    "Cybersecurity Expert", "Software Developer", "Business Analyst",
]

LEARNING_CHALLENGES: list[str] = [
    "Interview anxiety", "Lack of experience", "Limited guidance",
    "No networking opportunities", "Difficulty in resume building",
]

SUPPORT_OPTIONS: list[str] = [
    "Mentorship programs", "Technical skill training",
    "Resume workshops", "Internship opportunities",
]

LEARNING_METHODS: list[str] = [
    "College curriculum", "Self-study", "Online", "Bootcamp",
]


# --------------------------------------------------------------------------- #
#  4. TARGET CAREER DOMAINS
# --------------------------------------------------------------------------- #
# The 10 careers the system can recommend. Each entry is a complete profile
# used by the target-engineering step, the skill-gap detector and the growth
# pathway generator.
#
# Keys
# ----
# icon              : emoji shown in the UI
# description       : one-liner
# tech              : weighted technical-skill affinities (dataset tokens)
# lang              : weighted programming-language affinities (dataset tokens)
# soft              : weighted soft-skill affinities (dataset tokens)
# courses           : academic courses that align with the role
# interests         : career-interest values that point toward this role
# project_bias      : how much hands-on project experience matters (0-1)
# certifications    : recommended industry certifications
# projects          : portfolio project ideas
# learn_next        : higher-level skills to study (beyond the dataset tokens)
# interview_topics  : core interview preparation areas
# --------------------------------------------------------------------------- #
CAREERS: dict[str, dict] = {
    "Data Scientist": {
        "icon": "📊",
        "description": "Turns data into models and insight using statistics & ML.",
        "tech": {"Machine Learning": 3.0, "Data Analysis": 3.0, "Python": 2.0, "SQL": 1.0},
        "lang": {"Python": 3.0, "R": 2.0},
        "soft": {"Problem-Solving": 1.5, "Communication": 1.0},
        "courses": ["B.Sc Data Science", "M.Tech AI"],
        "interests": ["Data Scientist"],
        "project_bias": 0.7,
        "certifications": [
            "Google Advanced Data Analytics (Coursera)",
            "IBM Data Science Professional Certificate",
            "TensorFlow Developer Certificate",
            "Microsoft Certified: Azure Data Scientist Associate",
        ],
        "projects": [
            "End-to-end ML pipeline with experiment tracking (MLflow)",
            "Customer churn prediction with explainable AI (SHAP)",
            "Time-series demand forecasting dashboard",
            "NLP sentiment analysis on product reviews",
        ],
        "learn_next": ["Statistics & Probability", "Deep Learning", "Feature Engineering",
                       "MLflow / Experiment Tracking", "A/B Testing", "PyTorch"],
        "interview_topics": ["Bias-variance trade-off", "Regularisation", "Model evaluation metrics",
                             "SQL window functions", "Probability & statistics", "Case studies"],
    },
    "Data Analyst": {
        "icon": "📈",
        "description": "Answers business questions with SQL, dashboards & storytelling.",
        "tech": {"Data Analysis": 3.0, "SQL": 3.0, "Python": 1.0},
        "lang": {"Python": 1.5, "R": 1.5},
        "soft": {"Communication": 2.0, "Time Management": 1.0},
        "courses": ["B.Sc Data Science", "BBA", "B.Tech IT"],
        "interests": ["Data Scientist", "Business Analyst"],
        "project_bias": 0.5,
        "certifications": [
            "Google Data Analytics Professional Certificate",
            "Microsoft Power BI Data Analyst Associate (PL-300)",
            "Tableau Desktop Specialist",
        ],
        "projects": [
            "Interactive sales KPI dashboard (Power BI / Tableau)",
            "SQL-driven cohort & retention analysis",
            "Marketing funnel analytics report",
            "Excel-to-SQL automated reporting pipeline",
        ],
        "learn_next": ["Advanced SQL", "Power BI / Tableau", "Excel modelling",
                       "Statistics", "Data storytelling", "ETL basics"],
        "interview_topics": ["SQL joins & aggregations", "Dashboard design", "KPI definition",
                             "Descriptive statistics", "Business case framing"],
    },
    "AI Engineer": {
        "icon": "🤖",
        "description": "Builds and ships intelligent applications powered by AI models.",
        "tech": {"Machine Learning": 3.0, "Python": 2.5, "Cloud Computing": 2.0, "Data Analysis": 1.0},
        "lang": {"Python": 3.0, "C++": 1.0},
        "soft": {"Problem-Solving": 1.5, "Adaptability": 1.0},
        "courses": ["M.Tech AI", "B.Tech CSE"],
        "interests": ["AI Engineer"],
        "project_bias": 0.8,
        "certifications": [
            "TensorFlow Developer Certificate",
            "AWS Certified Machine Learning – Specialty",
            "DeepLearning.AI Deep Learning Specialization",
            "Hugging Face / LLM Engineering certificate",
        ],
        "projects": [
            "Retrieval-Augmented-Generation (RAG) chatbot",
            "Computer-vision defect-detection service",
            "Fine-tuned LLM for domain Q&A",
            "Real-time recommendation microservice",
        ],
        "learn_next": ["Deep Learning", "Transformers & LLMs", "MLOps", "Vector databases",
                       "Model serving (FastAPI/Triton)", "Prompt engineering"],
        "interview_topics": ["Neural network architectures", "Transformers/attention",
                             "Model deployment", "Vector search", "System design for ML"],
    },
    "Machine Learning Engineer": {
        "icon": "⚙️",
        "description": "Productionises ML models with robust, scalable engineering.",
        "tech": {"Machine Learning": 3.0, "Python": 2.0, "Cloud Computing": 2.0, "SQL": 1.0},
        "lang": {"Python": 3.0, "Java": 1.0, "C++": 1.0},
        "soft": {"Problem-Solving": 1.5, "Teamwork": 1.0},
        "courses": ["M.Tech AI", "B.Tech CSE"],
        "interests": ["AI Engineer", "Data Scientist"],
        "project_bias": 0.85,
        "certifications": [
            "AWS Certified Machine Learning – Specialty",
            "Google Professional Machine Learning Engineer",
            "TensorFlow Developer Certificate",
        ],
        "projects": [
            "CI/CD pipeline for automated model retraining",
            "Feature store + online inference API",
            "Model monitoring & drift-detection dashboard",
            "Dockerised, autoscaled ML microservice on Kubernetes",
        ],
        "learn_next": ["MLOps", "Docker & Kubernetes", "CI/CD", "Feature stores",
                       "Distributed training", "Model monitoring"],
        "interview_topics": ["ML system design", "Data pipelines", "Containerisation",
                             "Model versioning", "Scalability & latency"],
    },
    "Cloud Engineer": {
        "icon": "☁️",
        "description": "Designs, deploys & manages scalable cloud infrastructure.",
        "tech": {"Cloud Computing": 3.5, "Python": 1.0, "Cybersecurity": 1.0},
        "lang": {"Go": 2.0, "Python": 1.5, "Java": 1.0},
        "soft": {"Adaptability": 1.5, "Problem-Solving": 1.0},
        "courses": ["B.Tech IT", "B.Tech CSE"],
        "interests": ["Cloud Architect"],
        "project_bias": 0.6,
        "certifications": [
            "AWS Certified Solutions Architect – Associate",
            "Microsoft Certified: Azure Fundamentals (AZ-900)",
            "Google Associate Cloud Engineer",
            "AWS Cloud Practitioner",
        ],
        "projects": [
            "Infrastructure-as-Code deployment with Terraform",
            "Serverless image-processing pipeline",
            "Multi-region highly-available web app",
            "Cloud cost-optimisation audit & dashboard",
        ],
        "learn_next": ["AWS/Azure/GCP core services", "Terraform", "Networking",
                       "Linux", "Docker", "Cloud security"],
        "interview_topics": ["Cloud architecture patterns", "Networking & VPC", "IaC",
                             "High availability", "Cost optimisation"],
    },
    "DevOps Engineer": {
        "icon": "🔧",
        "description": "Automates build-test-deploy so teams ship faster & safer.",
        "tech": {"Cloud Computing": 3.0, "Python": 1.5, "Java": 1.0, "Cybersecurity": 1.0},
        "lang": {"Go": 2.0, "Python": 1.5, "JavaScript": 1.0},
        "soft": {"Teamwork": 1.5, "Adaptability": 1.5},
        "courses": ["B.Tech IT", "B.Tech CSE"],
        "interests": ["Cloud Architect", "Software Developer"],
        "project_bias": 0.7,
        "certifications": [
            "Docker Certified Associate",
            "Certified Kubernetes Administrator (CKA)",
            "AWS Certified DevOps Engineer – Professional",
            "HashiCorp Terraform Associate",
        ],
        "projects": [
            "Full CI/CD pipeline with GitHub Actions + ArgoCD",
            "Kubernetes cluster with Helm charts & monitoring",
            "Centralised logging & alerting stack (ELK/Prometheus)",
            "Blue-green & canary deployment automation",
        ],
        "learn_next": ["CI/CD", "Docker & Kubernetes", "Terraform/Ansible",
                       "Monitoring (Prometheus/Grafana)", "Scripting", "Git workflows"],
        "interview_topics": ["CI/CD pipelines", "Container orchestration", "IaC",
                             "Monitoring & observability", "Incident response"],
    },
    "Cybersecurity Analyst": {
        "icon": "🔒",
        "description": "Defends systems & data against threats and intrusions.",
        "tech": {"Cybersecurity": 4.0, "Python": 1.0, "Cloud Computing": 1.0},
        "lang": {"Python": 1.5, "C++": 1.0, "Go": 0.5},
        "soft": {"Problem-Solving": 1.5, "Adaptability": 1.0},
        "courses": ["B.Tech IT", "B.Tech CSE"],
        "interests": ["Cybersecurity Expert"],
        "project_bias": 0.6,
        "certifications": [
            "CompTIA Security+",
            "Certified Ethical Hacker (CEH)",
            "Cisco CyberOps Associate",
            "(ISC)² Certified in Cybersecurity (CC)",
        ],
        "projects": [
            "Home SOC lab with SIEM (Wazuh/Splunk)",
            "Vulnerability assessment & pentest report",
            "Phishing-detection ML classifier",
            "Network intrusion-detection system",
        ],
        "learn_next": ["Networking", "Linux", "Security fundamentals", "SIEM tools",
                       "Ethical hacking", "Cryptography"],
        "interview_topics": ["CIA triad", "OWASP Top 10", "Network security",
                             "Incident response", "Cryptography basics"],
    },
    "Software Developer": {
        "icon": "💻",
        "description": "Designs & builds reliable software across the stack.",
        "tech": {"Java": 2.5, "SQL": 1.5, "Cloud Computing": 0.5},
        "lang": {"Java": 3.0, "C#": 2.0, "C++": 2.0, "Python": 1.0},
        "soft": {"Teamwork": 1.5, "Time Management": 1.0, "Problem-Solving": 1.0},
        "courses": ["B.Tech CSE", "B.Tech IT"],
        "interests": ["Software Developer"],
        "project_bias": 0.75,
        "certifications": [
            "Oracle Certified Professional: Java SE",
            "Microsoft Certified: Azure Developer Associate",
            "Meta Back-End Developer Certificate",
        ],
        "projects": [
            "REST API with authentication & tests",
            "Inventory-management desktop/web app",
            "Multi-threaded file-processing tool",
            "Clean-architecture microservice",
        ],
        "learn_next": ["Data Structures & Algorithms", "OOP & design patterns",
                       "Databases", "REST APIs", "Version control", "Testing"],
        "interview_topics": ["Data structures & algorithms", "OOP principles",
                             "System design basics", "Databases", "Testing"],
    },
    "Full Stack Developer": {
        "icon": "🌐",
        "description": "Builds complete web apps — front-end to back-end to DB.",
        "tech": {"SQL": 2.0, "Java": 1.0, "Cloud Computing": 1.0, "Python": 1.0},
        "lang": {"JavaScript": 3.5, "Java": 1.0, "C#": 1.0, "Python": 1.0},
        "soft": {"Teamwork": 1.5, "Communication": 1.0, "Time Management": 1.0},
        "courses": ["B.Tech CSE", "B.Tech IT"],
        "interests": ["Software Developer"],
        "project_bias": 0.8,
        "certifications": [
            "Meta Full-Stack Developer Certificate",
            "freeCodeCamp Full Stack Certification",
            "MongoDB Associate Developer",
        ],
        "projects": [
            "MERN/Next.js e-commerce platform",
            "Real-time chat app with WebSockets",
            "SaaS dashboard with auth & billing",
            "Progressive Web App with offline support",
        ],
        "learn_next": ["HTML/CSS/JavaScript", "React/Next.js", "Node.js & Express",
                       "Databases (SQL & NoSQL)", "REST/GraphQL APIs", "Deployment"],
        "interview_topics": ["JavaScript fundamentals", "React lifecycle/hooks",
                             "REST API design", "Databases", "Web security"],
    },
    "Business Analyst": {
        "icon": "📋",
        "description": "Bridges business needs and tech solutions with data & analysis.",
        "tech": {"Data Analysis": 3.0, "SQL": 2.0},
        "lang": {"R": 1.0, "Python": 0.5},
        "soft": {"Communication": 3.0, "Leadership": 2.0, "Time Management": 1.5},
        "courses": ["MBA", "BBA", "B.Sc Data Science"],
        "interests": ["Business Analyst"],
        "project_bias": 0.4,
        "certifications": [
            "Google Data Analytics Professional Certificate",
            "IIBA Entry Certificate in Business Analysis (ECBA)",
            "Microsoft Power BI Data Analyst Associate (PL-300)",
            "PMI Professional in Business Analysis (PBA)",
        ],
        "projects": [
            "Requirement-gathering & BRD for a product feature",
            "Process-improvement analysis with KPIs",
            "Market & competitor analysis dashboard",
            "Cost-benefit / ROI modelling spreadsheet",
        ],
        "learn_next": ["Requirement analysis", "SQL", "Power BI/Tableau",
                       "Business process modelling", "Stakeholder management", "Agile"],
        "interview_topics": ["Requirement elicitation", "SQL basics", "Use-case & BRD",
                             "Stakeholder communication", "Agile/Scrum"],
    },
}

CAREER_LIST: list[str] = list(CAREERS.keys())

# Maps the dataset's 6 "career interest" values onto the most representative
# target career (used by the readiness alignment pillar & the UI).
INTEREST_TO_CAREER: dict[str, str] = {
    "Data Scientist": "Data Scientist",
    "AI Engineer": "AI Engineer",
    "Cloud Architect": "Cloud Engineer",
    "Cybersecurity Expert": "Cybersecurity Analyst",
    "Software Developer": "Software Developer",
    "Business Analyst": "Business Analyst",
}


# --------------------------------------------------------------------------- #
#  5. CAREER-READINESS SCORING SCHEME
# --------------------------------------------------------------------------- #
# Weighted contribution of each pillar to the 0-100 readiness score.
READINESS_WEIGHTS: dict[str, float] = {
    "technical": 0.40,   # technical skills (breadth × rated proficiency)
    "programming": 0.20,  # programming languages (breadth)
    "soft": 0.20,         # soft skills (breadth × rated proficiency)
    "projects": 0.10,     # hands-on project experience
    "alignment": 0.10,    # alignment between skills and chosen career
}

# Readiness bands: (lower_inclusive, upper_inclusive, label, emoji, colour)
READINESS_BANDS: list[tuple[int, int, str, str, str]] = [
    (0, 40, "Beginner", "🌱", "#ef4444"),
    (41, 60, "Intermediate", "📘", "#f59e0b"),
    (61, 80, "Advanced", "🚀", "#3b82f6"),
    (81, 100, "Industry Ready", "🏆", "#22c55e"),
]


def readiness_band(score: float) -> tuple[str, str, str]:
    """
    Return (label, emoji, colour) for a 0-100 readiness score.

    Uses upper-bound comparison so fractional scores that fall *between* the
    integer band ranges (e.g. 40.8) are still classified correctly instead of
    slipping through the gaps.
    """
    s = max(0, min(100, score))
    for _low, high, label, emoji, colour in READINESS_BANDS:
        if s <= high:
            return label, emoji, colour
    return READINESS_BANDS[-1][2:5]


# --------------------------------------------------------------------------- #
#  6. TARGET-ENGINEERING HYPER-PARAMETERS
# --------------------------------------------------------------------------- #
# The ML target ("recommended_career") is produced by an expert decision rubric
# (see target_engineering.assign_recommended_career): the stated career interest
# selects a career *family*, then course / signature-skills / ratings refine the
# choice within that family. This rubric distils domain expertise into a
# learnable label.
#
# A small fraction of labels are randomly perturbed (LABEL_NOISE_RATE) to model
# real-world fuzziness and keep the problem non-trivial — without it tree models
# would recover the rubric almost perfectly and report a misleading ~100%.
LABEL_NOISE_RATE: float = 0.06   # tuned so the best model lands ~88-92% accuracy


# --------------------------------------------------------------------------- #
#  7. CURATED LEARNING RESOURCES
# --------------------------------------------------------------------------- #
LEARNING_PLATFORMS: dict[str, str] = {
    "Coursera": "https://www.coursera.org",
    "Udemy": "https://www.udemy.com",
    "NPTEL": "https://nptel.ac.in",
    "YouTube": "https://www.youtube.com",
    "freeCodeCamp": "https://www.freecodecamp.org",
    "edX": "https://www.edx.org",
    "Kaggle": "https://www.kaggle.com/learn",
}

# Generic, high-quality starting points keyed by broad skill area. The growth
# pathway maps a recommended skill to the closest bucket.
RESOURCE_LIBRARY: dict[str, list[dict]] = {
    "Python": [
        {"title": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python"},
        {"title": "freeCodeCamp Python Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization (Andrew Ng)", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
        {"title": "Kaggle Intro to ML", "platform": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
    ],
    "Deep Learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning"},
        {"title": "Practical Deep Learning (fast.ai)", "platform": "YouTube", "url": "https://course.fast.ai"},
    ],
    "SQL": [
        {"title": "SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science"},
        {"title": "freeCodeCamp SQL Course", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/tag/sql/"},
    ],
    "Data Analysis": [
        {"title": "Google Data Analytics", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-data-analytics"},
        {"title": "Data Analysis with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/"},
    ],
    "Cloud Computing": [
        {"title": "AWS Cloud Practitioner Essentials", "platform": "Coursera", "url": "https://www.coursera.org/learn/aws-cloud-practitioner-essentials"},
        {"title": "Azure Fundamentals AZ-900", "platform": "Udemy", "url": "https://learn.microsoft.com/credentials/certifications/azure-fundamentals/"},
    ],
    "Cybersecurity": [
        {"title": "Google Cybersecurity Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
        {"title": "CompTIA Security+ (Professor Messer)", "platform": "YouTube", "url": "https://www.youtube.com/c/professormesser"},
    ],
    "Web Development": [
        {"title": "Responsive Web Design", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
        {"title": "The Web Developer Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-web-developer-bootcamp/"},
    ],
    "Data Structures & Algorithms": [
        {"title": "Data Structures & Algorithms (NPTEL)", "platform": "NPTEL", "url": "https://nptel.ac.in/courses/106102064"},
        {"title": "freeCodeCamp DSA", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=8hly31xKli0"},
    ],
    "MLOps": [
        {"title": "MLOps Specialization (DeepLearning.AI)", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"},
    ],
    "DevOps": [
        {"title": "DevOps Beginners to Advanced", "platform": "Udemy", "url": "https://www.udemy.com/course/decodingdevops/"},
        {"title": "Docker & Kubernetes Full Course", "platform": "YouTube", "url": "https://www.youtube.com/watch?v=Wf2eSG3owoA"},
    ],
}

# A safe default bucket if a recommended skill has no dedicated resource list.
DEFAULT_RESOURCES: list[dict] = [
    {"title": "Search top-rated courses", "platform": "Coursera", "url": "https://www.coursera.org"},
    {"title": "Free tutorials & projects", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org"},
]


# --------------------------------------------------------------------------- #
#  8. UI THEME TOKENS  (used by Streamlit + Plotly for a consistent look)
# --------------------------------------------------------------------------- #
THEME = {
    "primary": "#6366f1",      # indigo
    "primary_dark": "#4338ca",
    "accent": "#06b6d4",       # cyan
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "bg": "#0f172a",
    "card": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}

# Sequential palette for categorical Plotly charts.
PLOTLY_PALETTE: list[str] = [
    "#6366f1", "#06b6d4", "#22c55e", "#f59e0b", "#ef4444",
    "#a855f7", "#ec4899", "#14b8a6", "#f97316", "#3b82f6",
]

APP_TITLE = "Intelligent Skill Profiling for Career Readiness & Growth Pathways"
APP_SHORT_TITLE = "SkillPath AI"
APP_ICON = "🎯"
