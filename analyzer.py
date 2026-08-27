import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load the API key from .env file
load_dotenv()

# Set up the Anthropic client
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

def save_result(jd_text, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write("=== JD ANALYZER RESULT ===\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 40 + "\n\n")
        f.write("ORIGINAL JOB DESCRIPTION:\n")
        f.write("-" * 40 + "\n")
        f.write(jd_text + "\n\n")
        f.write("ANALYSIS:\n")
        f.write("-" * 40 + "\n")
        f.write(result + "\n")
    
    return filename

def print_formatted(result):
    print("\n" + "=" * 40)
    print("       JD ANALYSIS RESULT")
    print("=" * 40 + "\n")
    print(result)
    print("\n" + "=" * 40)

# --- Main program ---
print("=== Application Fit Analyzer ===")
print("Paste your job description below.")
print("When done, type END on a new line and press Enter.")
print("")

lines = []
while True:
    line = input()
    if line.strip() == "END":
        break
    lines.append(line)

jd_text = "\n".join(lines)

print("\nAnalyzing... please wait\n")
result = analyze_jd(jd_text)

# Print formatted result
print_formatted(result)

# Ask if user wants to save
print("\nDo you want to save this analysis to a file? (yes/no)")
save_choice = input().strip().lower()

if save_choice == "yes":
    filename = save_result(jd_text, result)
    print(f"\nSaved to: {filename}")
else:
    print("\nAnalysis not saved.")

print("\nDone. Run the script again to analyze another JD.")