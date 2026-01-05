import streamlit as st
import os
import json
from src.chatbot import get_groq_response, get_recruiter_summary
from src.utils import save_candidate_info, create_pdf_bytes, create_bulk_pdf, decrypt_val

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TalentScout AI Portal", 
    page_icon="💼", 
    layout="wide"
)

# --- 2. SESSION STATE INITIALIZATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_ended = False
    # Initial Greeting
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm TalentScout AI. To begin, could you please provide your **Full Name, Email, Phone, Location, and Tech Stack**?"
    })

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("💼 TalentScout AI")
    st.markdown("---")
    
    if not st.session_state.admin_logged_in:
        st.subheader("🔐 HR Administration")
        pw = st.text_input("Enter Admin Password", type="password")
        if st.button("Login", use_container_width=True):
            if pw == "hr2026":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Access Denied")
    else:
        st.success("Admin Session Active")
        if st.button("Switch to Candidate View", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

# --- 4. VIEW: HR ADMIN DASHBOARD ---
if st.session_state.admin_logged_in:
    st.title("🕵️ Candidate Review Dashboard")
    
    data_path = "data/candidates.json"
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            try:
                candidates = json.load(f)
            except:
                candidates = []
        
        if candidates:
            # Dashboard Controls
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.metric("Total Applicants", len(candidates))
            
            c2.download_button(
                "📥 Export All (PDF)", 
                data=create_bulk_pdf(candidates), 
                file_name="Master_Recruitment_Report.pdf",
                use_container_width=True
            )

            if c3.button("🗑️ Reset Database", type="secondary", use_container_width=True):
                if os.path.exists(data_path):
                    os.remove(data_path)
                st.rerun()

            st.markdown("---")

            # Candidate List (Latest First)
            for idx, person in enumerate(reversed(candidates)):
                # Robust Header Logic: Decrypt name and handle fallback fields
                name = decrypt_val(person.get('name', 'New Candidate'))
                stack = person.get('tech_stack', 'Technical')
                date = person.get('date', 'Unknown Date')
                
                # Simplified Expander Header to prevent "N/A" clutter
                with st.expander(f"👤 {name} | 🛠️ {stack} | 📅 {date}"):
                    col_meta, col_actions = st.columns([2, 1])
                    
                    with col_meta:
                        st.markdown(f"**Target Role:** {person.get('position', 'Not Specified')}")
                        st.markdown(f"**Experience:** {person.get('experience', 'Not Specified')}")
                        
                        if st.button(f"👁️ View Chat Transcript", key=f"view_{idx}"):
                            for msg in person.get('transcript', []):
                                st.text(f"{msg['role'].upper()}: {msg['content']}")

                    with col_actions:
                        # Bonus Feature: Combined Summary & Sentiment Analysis
                        if st.button(f"🔍 AI Deep Analysis", key=f"an_{idx}", use_container_width=True):
                            with st.spinner("Analyzing Sentiment & Skills..."):
                                analysis = get_recruiter_summary(person['transcript'])
                                st.markdown(analysis)
                        
                        st.download_button(
                            "📄 Download PDF",
                            data=create_pdf_bytes(person.get('transcript', [])),
                            file_name=f"{name}_Report.pdf",
                            key=f"pdf_{idx}",
                            use_container_width=True
                        )
        else:
            st.info("No candidates have applied yet.")
    else:
        st.info("The database is currently empty.")

# --- 5. VIEW: CANDIDATE INTERVIEW ---
else:
    st.title("💼 AI Technical Screening")
    
    # GDPR Consent Check
    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False

    if not st.session_state.consent_given:
        st.warning("### 🔐 Privacy & Data Consent")
        st.write("""
        Before we begin, please acknowledge that:
        - Your responses will be recorded and encrypted for recruitment purposes.
        - Data is handled according to GDPR standards for pseudonymization.
        """)
        if st.button("I Consent & Start Interview"):
            st.session_state.consent_given = True
            st.rerun()
    else:
        # Render Chat History
        for message in st.session_state.messages:
            if message["role"] in ["user", "assistant"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # End of Session Logic
        if st.session_state.conversation_ended:
            st.success("✅ Interview Complete. Your data has been securely submitted.")
            st.balloons()
            if st.button("Start New Interview"):
                st.session_state.clear()
                st.rerun()
        
        # User Input Handling
        elif prompt := st.chat_input("Message TalentScout AI..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_groq_response(st.session_state.messages)
                    
                    # Check for system termination trigger
                    if "FINAL_HANDOVER" in response:
                        final_msg = response.replace("FINAL_HANDOVER", "").strip()
                        st.markdown(final_msg)
                        st.session_state.messages.append({"role": "assistant", "content": final_msg})
                        
                        # Persist data
                        save_candidate_info(st.session_state.messages)
                        st.session_state.conversation_ended = True
                        st.rerun()
                    else:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})