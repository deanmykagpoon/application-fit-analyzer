import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()

# Set up Anthropic client
client = Anthropic()

def analyze_jd(jd_text):
    prompt = f"""
    Analyze this job description and return a structured breakdown:

    1. REQUIRED VS PREFERRED SKILLS
       - List required skills separately from preferred/nice-to-have
    
    2. SENIORITY LEVEL
       - State the level (Junior/Mid/Senior/Lead)
       - List the signals in the JD that indicate this
    
    3. ESTIMATED SALARY BAND
       - Estimate based on role, seniority, and Singapore market rates
    
    4. BIAS FLAGS
       - Identify any gendered language or unnecessary requirements
       - Suggest neutral alternatives where applicable
    
    5. KEY COMPETENCIES (do not skip this section)
       - Look beyond the listed skills
       - What soft skills, working style, or hidden expectations does this role require
       - What type of person would succeed in this role

    Job Description:
    {jd_text}
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text

def prepare_download(jd_text, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""=== JD ANALYZER RESULT ===
Generated: {timestamp}
{'=' * 40}

ORIGINAL JOB DESCRIPTION:
{'-' * 40}
{jd_text}

ANALYSIS:
{'-' * 40}
{result}
"""
    return content

# --- Streamlit UI ---
st.set_page_config(page_title="JD Analyzer", page_icon="🔍")

st.title("🔍 Job Description Analyzer")
st.write("Paste a job description below and get an instant structured analysis.")

jd_text = st.text_area(
    label="Job Description",
    placeholder="Paste the full job description here...",
    height=300
)

if st.button("Analyze", type="primary"):
    if jd_text.strip() == "":
        st.warning("Please paste a job description before analyzing.")
    else:
        with st.spinner("Analyzing... please wait"):
            result = analyze_jd(jd_text)
        
        st.success("Analysis complete!")
        st.markdown("---")
        st.markdown(result)
        st.markdown("---")

        # Download button
        download_content = prepare_download(jd_text, result)
        st.download_button(
            label="📥 Download Analysis",
            data=download_content,
            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )