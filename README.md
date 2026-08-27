# Application Fit Analyzer

**Should I apply for this job, and where am I weak?**

Job seekers can read a job description perfectly well. What's genuinely hard is judging, honestly, whether they're a credible candidate for it — and if not, exactly where the shortfall is. That comparison is tedious to do properly, so almost nobody does.

This tool automates the analysis side of that decision using Claude (Anthropic API).

## What it does today

Paste a job description and get a structured breakdown:

- Required vs. preferred skills
- Seniority level, and the signals in the text that indicate it
- Estimated salary band (Singapore market rates)
- Bias flags — gendered language, unnecessary requirements — with neutral alternatives
- Key competencies: soft skills, working style, and unstated expectations

Two interfaces:

- **`app.py`** — Streamlit web app: paste a JD, get a formatted analysis, download it as `.txt`
- **`analyzer.py`** — command-line version: paste a JD, type `END`, analysis prints to the terminal

## In development

The next version adds CV compatibility analysis: upload a CV alongside the JD and get a requirement-by-requirement fit assessment — what's met, what's partially met, and what the CV doesn't evidence at all.

The design constraint that matters: **every "met" claim must quote the line in the CV that supports it.** No supporting quote, no claim. A fit report that infers matches from plausible-sounding job titles is worse than no report, because it sends someone into an interview unprepared for the question they can't answer.

## Setup

**1. Clone the repo and create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip3 install -r requirements.txt
```

**3. Set your Anthropic API key**

Create a `.env` file in the project root (not committed to version control):

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Web app

```bash
streamlit run app.py
```

Opens in your browser. Paste a job description, click **Analyze**, download the result if needed.

### Command line

```bash
python3 analyzer.py
```

Paste the job description, then type `END` on a new line to submit. You'll be asked whether to save the result to a timestamped `.txt` file.

## Deployment

Deployed on [Railway](https://railway.app) via `railway.toml`, running:

```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

`ANTHROPIC_API_KEY` must be set as an environment variable on the deployment platform.

## Project structure

```
.
├── app.py              # Streamlit web app
├── analyzer.py         # CLI version
├── requirements.txt    # Python dependencies
├── railway.toml        # Railway deployment config
└── .gitignore          # excludes .env, venv/, generated output
```

## Built with

Python · Streamlit · Anthropic Claude API
