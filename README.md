# 💼 TalentScout AI: Technical Screening & Recruitment Portal

TalentScout AI is a state-of-the-art recruitment automation tool that uses LLM-powered conversational intelligence (Groq/Llama 3.3) to conduct technical screenings. It bridges the gap between candidate assessment and HR efficiency through secure, encrypted data handling and automated performance analysis.

---

## 🚀 Requirement Satisfaction & Features

### 1. 🤖 Advanced Prompt Engineering
- **Structured Interview Logic:** Guided by a robust 3-phase system prompt (Info Gathering, Technical Assessment, and Closing).
- **Dynamic Difficulty:** AI generates technical questions tailored to the candidate's specific tech stack and years of experience.
- **Multilingual Support:** Detects and responds in the candidate's preferred language while maintaining screening standards.

### 2. 🔐 Data Privacy & Security (GDPR Ready)
- **Encryption at Rest:** Personally Identifiable Information (PII) is encrypted using **AES-128 (Fernet)** before being stored.
- **Privacy Consent Gate:** Mandatory agreement screen ensures informed consent before data collection.
- **Secure Configuration:** API keys and Encryption keys are managed via environment variables and excluded from Git.

### 3. 🛠️ Code Quality & Modular Architecture
- **Separation of Concerns:** - `app.py`: UI and Dashboard.
  - `src/chatbot.py`: AI logic & Sentiment analysis.
  - `src/utils.py`: Security & PDF generation.
  - `src/config.py`: Centralized prompts.
- **Maintainability:** Clean-code principles with descriptive naming and modular design.

### 🌟 Bonus Features
- **Sentiment Analysis:** Gauges candidate confidence and emotional tone.
- **AI Performance Summary:** Automated "Hire/No-Hire" recommendations.
- **Bulk PDF Export:** Export the entire candidate database as a professional report.

---

## 📂 Project Structure
```text
TalentScout/
├── app.py                # Main Application & Dashboard
├── requirements.txt      # Project Dependencies
├── .gitignore            # Security Exclusions
├── .env.example          # Template for credentials
├── data/                 # Local Storage (candidates.json)
├── tests/                # Automated Logic Tests
└── src/
    ├── __init__.py       # Package indicator
    ├── chatbot.py        # LLM Logic & Sentiment Analysis
    ├── config.py         # System Prompts & Constants
    └── utils.py          # Encryption & PDF Utilities


Installation & Setup
        Clone the repository:

        git clone [https://github.com/sreekeshvk/talentscout-ai-recruiter.git](https://github.com/sreekeshvk/talentscout-ai-recruiter.git)
        cd talentscout-ai-recruiter

Install dependencies:
        pip install -r requirements.txt


Configure Environment: Create a .env file in the root:
                        
        GROQ_API_KEY=your_api_key_here
        ENCRYPTION_KEY=your_generated_fernet_key

Run the App:

        streamlit run app.py