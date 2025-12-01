import streamlit as st
import PyPDF
from openai import OpenAI
import os

# 1. Page Configuration (मोबाईल फ्रेंडली सेटिंग)
st.set_page_config(page_title="Smart Resume Screener", layout="wide")

# 2. OpenAI API Key Setup (येथे तुमची की टाका किंवा .env वापरा)
# api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# --- फंक्शन्स ---

# PDF मधून टेक्स्ट काढणारे फंक्शन
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# AI कडून रेझ्युमे चेक करणारे फंक्शन (The Magic)
def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an expert HR Recruiter using advanced AI to screen resumes.
    
    Job Description:
    {job_description}
    
    Candidate Resume Text:
    {resume_text}
    
    Task:
    1. Compare the resume against the job description.
    2. Give a relevance score out of 100 based on skills, experience, and context.
    3. Provide a brief reason (2 lines) for the score.
    
    Output Format strictly like this:
    Score: [Number]
    Reason: [Text]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # सर्वात स्मार्ट मॉडेल
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

# --- मुख्य ॲप (UI Design) ---

st.title("🚀 AI Smart Resume Screener")
st.write("तुमची जॉब रिक्वायरमेंट टाका आणि मॅजिक पहा!")

# इनपुट विभाग
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. जॉब डिस्क्रिप्शन (JD)")
    job_desc = st.text_area("येथे स्किल्स आणि कामाचे स्वरूप लिहा...", height=300)

with col2:
    st.subheader("2. रेझ्युमे अपलोड (Bulk)")
    uploaded_files = st.file_uploader("येथे सर्व PDF रेझ्युमे टाका", type=["pdf"], accept_multiple_files=True)

# ॲक्शन बटन
if st.button("🔍 सर्वोत्तम उमेदवार शोधा (Analyze)"):
    if not job_desc:
        st.error("कृपया जॉब डिस्क्रिप्शन लिहा!")
    elif not uploaded_files:
        st.error("कृपया रेझ्युमे अपलोड करा!")
    else:
        results = []
        progress_bar = st.progress(0)
        
        st.info(f"एकूण {len(uploaded_files)} रेझ्युमे तपासले जात आहेत...")
        
        for i, file in enumerate(uploaded_files):
            # Text Extraction
            text = extract_text_from_pdf(file)
            
            # AI Analysis
            try:
                ai_response = analyze_resume(text, job_desc)
                
                # Parsing Score (AI च्या उत्तरातून स्कोर वेगळा करणे)
                lines = ai_response.split('\n')
                score = 0
                reason = ""
                for line in lines:
                    if "Score:" in line:
                        score = int(line.replace("Score:", "").strip())
                    if "Reason:" in line:
                        reason = line.replace("Reason:", "").strip()
                
                results.append({
                    "Name": file.name,
                    "Score": score,
                    "Reason": reason
                })
            except Exception as e:
                st.error(f"Error analyzing {file.name}: {e}")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        # --- निकाल (Results) ---
        st.success("विश्लेषण पूर्ण झाले! खालील यादी पहा:")
        
        # स्कोरनुसार क्रमवारी (Ranking)
        sorted_results = sorted(results, key=lambda x: x['Score'], reverse=True)
        
        # रिझल्ट दाखवणे
        for res in sorted_results:
            if res['Score'] >= 80:
                color = "green" # उत्तम
            elif res['Score'] >= 50:
                color = "orange" # मध्यम
            else:
                color = "red" # कमी
            
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:10px; margin-bottom:10px; border-left: 5px solid {color}">
                <h3>📄 {res['Name']} - <span style="color:{color}">Rating: {res['Score']}/100</span></h3>
                <p><strong>कारण:</strong> {res['Reason']}</p>
            </div>

            """, unsafe_allow_html=True)
