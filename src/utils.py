import json
import os
import re
from fpdf import FPDF
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# =================================================================
# 1. GDPR ENCRYPTION CONFIGURATION (ENV DRIVEN)
# =================================================================
# Fetch the key from .env. If not found, it falls back to a dummy key 
# to prevent the app from crashing (though decryption will fail).
ENV_KEY = os.getenv("ENCRYPTION_KEY")
if not ENV_KEY:
    # Fallback for local dev if .env is missing the key
    ENV_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(ENV_KEY.encode())

def encrypt_val(text):
    """Encrypts Personally Identifiable Information using AES-128."""
    if not text: return ""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_val(text):
    """Decrypts strings for authorized HR viewing via the Admin Dashboard."""
    if not text: return ""
    try:
        return cipher_suite.decrypt(text.encode()).decode()
    except Exception:
        # If the key changed or data is unencrypted, return as is
        return text

# =================================================================
# 2. DATA EXTRACTION & STORAGE
# =================================================================

def save_candidate_info(messages):
    """Parses transcript, extracts data, and saves encrypted JSON."""
    file_path = "data/candidates.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 1. Find the summary table in the assistant's responses
    summary_text = ""
    for m in reversed(messages):
        if m["role"] == "assistant" and "Full Name:" in m["content"]:
            summary_text = m["content"]
            break
            
    if not summary_text:
        summary_text = messages[1]["content"] if len(messages) > 1 else ""

    # 2. Regex Helper
    def extract_field(label, text):
        match = re.search(rf"{label}:\s*(.*)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    # 3. Data Construction
    raw_name = extract_field("Full Name", summary_text) or "Candidate"
    exp = extract_field("Years of Experience", summary_text) or "N/A"
    pos = extract_field("Desired Position", summary_text) or "Developer"
    stack = extract_field("Tech Stack", summary_text) or "Technical"

    new_entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "name": encrypt_val(raw_name.title()), # ENCRYPTED IN JSON
        "experience": f"{exp} Years" if exp.isdigit() else exp,
        "position": pos.title(),
        "tech_stack": stack.title(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "transcript": [m for m in messages if m["role"] != "system"] 
    }
    
    # 4. JSON Update Logic
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: data = []
    
    data.append(new_entry)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =================================================================
# 3. PDF GENERATION
# =================================================================

def create_pdf_bytes(transcript):
    """Generates a PDF for a single candidate."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Technical Interview Report", ln=True, align='C')
    pdf.ln(10)
    
    for m in transcript:
        role = "CANDIDATE" if m["role"] == "user" else "RECRUITER"
        content = m["content"].encode('latin-1', 'replace').decode('latin-1')
        pdf.set_font("Arial", 'B', 10)
        pdf.multi_cell(0, 8, f"{role}:")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, content)
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

def create_bulk_pdf(all_candidates):
    """Generates a Master PDF containing all candidates."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for person in all_candidates:
        pdf.add_page()
        # DECRYPT NAME FOR THE PDF REPORT
        name = decrypt_val(person.get('name', 'Unknown'))
        
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 12, txt=f"Candidate: {name}", ln=True, fill=True)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 8, f"Role: {person.get('position')} | Exp: {person.get('experience')}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=9)
        for msg in person.get('transcript', []):
            role = "USER" if msg['role'] == 'user' else "AI"
            content = msg['content'].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, f"{role}: {content}")
            pdf.ln(1)
            
    return pdf.output(dest='S').encode('latin-1')