"""
Application Fit Analyzer - Streamlit UI.

Paste a job description, upload a CV, get an evidence-backed fit assessment.
CVs are processed in memory only and never written to disk.
"""

import os
import re

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

import cv_reader
import match_engine

load_dotenv()

# st.secrets on Streamlit Cloud, .env locally.
# st.secrets raises when no secrets file exists, so catch broadly.
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=api_key)

MAX_JD_CHARS = 20000

VERDICT_ORDER = [
    ("not_evidenced", "Not evidenced", "These gaps are what a screener will notice first."),
    ("partial", "Partially evidenced", "Real evidence, but thinner than what was asked for."),
    ("met", "Evidenced", "Backed by a direct quote from the CV."),
]


def escape_md(text):
    """Neutralise markdown characters so CV text renders as written."""
    return re.sub(r"([*_`#\[\]])", r"\\\1", str(text))


def render_requirements(requirements):
    for verdict, label, blurb in VERDICT_ORDER:
        rows = [r for r in requirements if r["verdict"] == verdict]
        if not rows:
            continue

        st.markdown(f"##### {label} ({len(rows)})")
        st.caption(blurb)

        for row in rows:
            tier = "Essential" if row["importance"] == "essential" else "Desirable"
            st.markdown(f"**{escape_md(row['requirement'])}**  \n`{tier}`")
            if row.get("evidence"):
                st.markdown(f"> {escape_md(row['evidence'])}")
            if row.get("note"):
                st.caption(escape_md(row["note"]))
            st.divider()


def render_results(result):
    essential = result["essential_score"]
    desirable = result["desirable_score"]

    left, right = st.columns(2)
    with left:
        st.metric("Essential requirements", f"{essential['percentage']}%")
        st.caption(
            f"{essential['met']} evidenced · {essential['partial']} partial · "
            f"{essential['not_evidenced']} not evidenced · {essential['total']} total"
        )
    with right:
        if desirable:
            st.metric("Desirable requirements", f"{desirable['percentage']}%")
            st.caption(
                f"{desirable['met']} evidenced · {desirable['partial']} partial · "
                f"{desirable['not_evidenced']} not evidenced · {desirable['total']} total"
            )
        else:
            st.metric("Desirable requirements", "—")
            st.caption("None identified in this job description")

    st.caption(
        "Partially evidenced requirements count as half. Every evidenced claim "
        "is backed by a quote from the CV — check them against your own reading."
    )

    st.subheader("Recommendation")
    st.write(result["recommendation"])

    if result.get("downgraded_count"):
        st.info(
            f"{result['downgraded_count']} claim(s) were moved to 'not evidenced' "
            "because the supporting quote could not be found in the CV."
        )

    st.subheader("Requirements")
    render_requirements(result["requirements"])

    if result.get("missing_keywords"):
        st.subheader("Keywords absent from the CV")
        st.caption("Terms from the job description a keyword screen may search for.")
        st.write(" · ".join(escape_md(k) for k in result["missing_keywords"]))

    if result.get("unrequested_strengths"):
        st.subheader("Strengths the job description didn't ask for")
        st.caption("Not gaps — these are angles worth raising in an interview.")
        for item in result["unrequested_strengths"]:
            st.markdown(f"- {escape_md(item)}")

    summary = result.get("role_summary") or {}
    with st.expander("About this role"):
        if summary.get("seniority"):
            st.markdown(f"**Seniority:** {escape_md(summary['seniority'])}")
            for signal in summary.get("seniority_signals", []):
                st.markdown(f"- {escape_md(signal)}")
        if summary.get("salary_band"):
            st.markdown(f"**Estimated salary band:** {escape_md(summary['salary_band'])}")
        flags = summary.get("bias_flags") or []
        if flags:
            st.markdown("**Language worth questioning**")
            for flag in flags:
                st.markdown(f"- {escape_md(flag.get('issue', ''))}")
                if flag.get("suggestion"):
                    st.caption(escape_md(flag["suggestion"]))
        else:
            st.caption("No biased or unnecessary language flagged.")


# --- UI ---

st.set_page_config(page_title="Application Fit Analyzer", page_icon="🔍", layout="centered")

st.title("🔍 Application Fit Analyzer")
st.write(
    "Paste a job description and add your CV. Every claim this tool makes is "
    "backed by a quote from your CV — if it can't quote it, it won't claim it."
)

jd_text = st.text_area(
    "Job description",
    height=220,
    max_chars=MAX_JD_CHARS,
    placeholder="Paste the full job description here",
)

st.markdown("**Your CV**")
st.caption("Processed in memory for this analysis only. Nothing is stored.")

upload_tab, paste_tab = st.tabs(["Upload a file", "Paste as text"])
with upload_tab:
    cv_file = st.file_uploader("PDF or Word document", type=["pdf", "docx"])
with paste_tab:
    cv_pasted = st.text_area(
        "CV text", height=220, placeholder="Paste the text of your CV here"
    )

has_cv = cv_file is not None or bool(cv_pasted and cv_pasted.strip())
ready = bool(jd_text and jd_text.strip()) and has_cv

if not ready:
    st.caption("Add both a job description and a CV to run the analysis.")

if st.button("Analyse fit", type="primary", disabled=not ready):
    try:
        if cv_file is not None:
            cv_text = cv_reader.extract_from_upload(cv_file.getvalue(), cv_file.name)
        else:
            cv_text = cv_reader.extract_from_text(cv_pasted)
    except cv_reader.CVReadError as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Comparing your CV against the job description…"):
        try:
            result = match_engine.analyse(client, jd_text, cv_text)
        except match_engine.MatchError as exc:
            st.error(str(exc))
            st.stop()

    render_results(result)
