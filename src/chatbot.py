import os
from groq import Groq
from dotenv import load_dotenv
from src.config import MODEL_NAME, SYSTEM_PROMPT

# Load environment variables (to get GROQ_API_KEY)
load_dotenv()

# Initialize the Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_groq_response(messages):
    """
    Handles the main interview conversation.
    Uses the SYSTEM_PROMPT from config.py to guide the AI.
    """
    try:
        # Combine System Prompt with Conversation History
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages,
            temperature=0.7,  
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting. (Error: {str(e)})"

def get_recruiter_summary(transcript):
    """
    Performs the Bonus Analysis:
    - Technical Assessment
    - Sentiment Analysis (Bonus Requirement)
    - Hiring Recommendation
    """
    try:
        analysis_prompt = (
            "You are an expert HR Analyst. Analyze the provided interview transcript "
            "and produce a structured report with these exact sections:\n\n"
            "### 🛠️ Technical Assessment\n"
            "Summarize their proficiency based on their answers.\n\n"
            "### 🎭 Sentiment & Soft Skills\n"
            "Analyze communication style (Confidence, Anxiety, Clarity).\n\n"
            "### ⚖️ Final Recommendation\n"
            "Provide a 'Hire', 'Hold', or 'No-Hire' status with a justification."
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": f"Transcript to analyze: {str(transcript)}"}
            ],
            temperature=0.2 # Low temperature for consistent, objective analysis
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis unavailable. (Error: {str(e)})"