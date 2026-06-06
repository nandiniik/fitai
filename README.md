# 💪 FitAI — AI-Powered Health Platform

> Personalized diet & workout plans generated in under 10 seconds using LLMs

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![Groq](https://img.shields.io/badge/Groq-Llama3.3--70B-orange)

## 🔗 Live Demo
**[👉 Click here to try FitAI](YOUR_STREAMLIT_URL_HERE)**

---

## ✨ Features
- 🥗 **Personalized Diet Plans** — 6-meal daily plans based on your BMI, goals, allergies & region
- 💪 **Weekly Workout Plans** — Sets, reps, rest times tailored to your fitness level
- 📊 **Health Dashboard** — BMI gauge, macro pie chart, TDEE, calorie targets
- 📄 **PDF Export** — Download your complete plan as a branded PDF
- 🗄️ **User Persistence** — SQLite database stores all profiles & plans
- 🧠 **RAG-Ready Architecture** — Modular chain structure for nutrition data retrieval

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| LLM | Llama 3.3-70B via Groq API |
| AI Orchestration | LangChain (LCEL) |
| Data Validation | Pydantic v2 |
| Database | SQLite + SQLAlchemy ORM |
| Charts | Plotly |
| PDF Generation | ReportLab |
| Testing | pytest (7 tests) |
| Deployment | Streamlit Community Cloud |

## 🏗️ Project Structure
fitai/
├── app.py                  # Streamlit entry point
├── chains/                 # LangChain LCEL chains
│   ├── diet_chain.py       # Diet plan generation
│   └── workout_chain.py    # Workout plan generation
├── models/
│   └── user_profile.py     # Pydantic validation + BMI/TDEE calculations
├── prompts/                # Prompt templates (separated from logic)
├── database/
│   └── db.py               # SQLAlchemy ORM + CRUD operations
├── utils/
│   ├── health_calc.py      # Macro split, water intake, health summary
│   └── pdf_export.py       # ReportLab PDF generation
└── tests/
└── test_health_calc.py # pytest unit tests

## 🚀 Run Locally

```bash
git clone https://github.com/nandiniik/fitai.git
cd fitai
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY to .env

streamlit run app.py
```

## 🔑 Environment Variables
GROQ_API_KEY=your_groq_api_key_here   # Free at console.groq.com

## 📸 Screenshots

<!-- Add your screenshots here after deployment -->

## 🧪 Tests
```bash
pytest tests/ -v
# 7 passed in 0.29s
```

## 👩‍💻 Author
**Nandini Kumari** — [GitHub](https://github.com/nandiniik)
