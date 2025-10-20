import streamlit as st
import os, json, uuid, pandas as pd

# Guard optional imports so app doesn't crash in runtimes where packages aren't installed
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

try:
    from langchain_core.prompts import PromptTemplate
except Exception:
    PromptTemplate = None

try:
    import chromadb
except Exception:
    chromadb = None

# Load environment variables (.env or Streamlit Secrets) if available
if load_dotenv:
    load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# Inform user about missing runtime packages instead of crashing
if ChatGroq is None:
    st.warning("Package 'langchain-groq' is not installed in this runtime. LLM features will be disabled. Add 'langchain-groq' to requirements.txt and redeploy.")
if PromptTemplate is None:
    st.warning("Package 'langchain-core' (prompts) is not installed. PromptTemplate features will be disabled.")
if chromadb is None:
    st.info("Package 'chromadb' not installed: portfolio matching will be disabled.")

# Safety check for API key only when LLM is required
if ChatGroq is not None and not GROQ_API_KEY:
    st.error("🚨 Missing GROQ_API_KEY. Add it in Streamlit Cloud → Settings → Secrets or .env.")
    st.stop()

# Initialize LLM only if available
llm = None
if ChatGroq is not None:
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=GROQ_API_KEY
    )

# Streamlit UI
st.set_page_config(page_title="Cold Mail Generator", page_icon="📧", layout="centered")

st.title("📧 Cold Email Generator (Powered by Groq Llama 3.1)")

st.markdown("""
This app helps you generate professional **cold emails** tailored to a job description and your company’s portfolio.
""")

# User Inputs
job_description = st.text_area("🧾 Paste Job Description:", height=200)
links = st.text_area("🔗 Enter Portfolio Links (comma separated):", height=100)

if st.button("✉️ Generate Cold Email"):
    if not job_description.strip():
        st.warning("Please enter a job description first.")
    else:
        with st.spinner("Generating cold email..."):
            # Build prompt
            prompt = PromptTemplate.from_template("""
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Muzzammil, a Business Development Executive at **Accenture**, an AI & Software Consulting company.
            Accenture facilitates seamless business process integration through automated tools, driving scalability,
            process optimization, cost reduction, and efficiency.

            Write a professional cold email describing Accenture’s capability to fulfill their needs.
            Also, reference the most relevant ones from the following portfolio links:
            {link_list}

            ### EMAIL (NO PREAMBLE):
            """)

            chain = prompt | llm
            res = chain.invoke({
                "job_description": job_description,
                "link_list": links
            })

        st.success("✅ Email Generated Successfully!")
        st.markdown("### ✉️ Output:")
        st.write(res.content)

        # Copy email
        st.download_button(
            label="📥 Download Email as Text",
            data=res.content,
            file_name="cold_email.txt",
            mime="text/plain"
        )

st.markdown("---")
st.caption("Built by Muzzammil — Powered by Accenture & Groq AI 🚀")
