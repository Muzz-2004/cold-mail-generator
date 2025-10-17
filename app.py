import streamlit as st
import os, json, uuid, pandas as pd

# try to load dotenv but don't crash if it's not installed in the runtime
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# optional: langchain / loaders / prompts
try:
    from langchain.document_loaders import WebBaseLoader
    from langchain.prompts import PromptTemplate
except Exception:
    WebBaseLoader = None
    PromptTemplate = None
    st.warning("langchain not installed: web scraping and prompt templates will be disabled. Install with: python -m pip install langchain")

# optional: Groq chat model
try:
    from langchain_groq.chat_models import ChatGroq
except Exception:
    ChatGroq = None
    st.warning("langchain-groq not installed: Groq LLM calls will be disabled. Install with: python -m pip install langchain-groq")

# optional: chromadb for vector store
try:
    import chromadb
except Exception:
    chromadb = None
    st.warning("chromadb not installed: portfolio matching will be disabled. Install with: python -m pip install chromadb")

# Load environment variables from .env locally if available
if load_dotenv:
    load_dotenv()

# Prefer Streamlit secrets, fallback to environment variables
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

# Initialize Streamlit page
st.set_page_config(page_title="AI Cold Email Dashboard", page_icon="🤖", layout="wide")
st.title("🤖 AI-Powered Job Scraper + Email Generator + Portfolio Matcher")

# Initialize ChromaDB (only if available)
if chromadb:
    try:
        client = chromadb.PersistentClient(path="vectorstore")
        collection = client.get_or_create_collection("portfolio")
    except Exception as e:
        st.warning(f"Could not initialize chromadb client: {e}")
        client = None
        collection = None
else:
    client = None
    collection = None

# Load portfolio CSV once
if "portfolio_loaded" not in st.session_state:
    if os.path.exists("portfolio.csv"):
        df = pd.read_csv("portfolio.csv")

        if collection is not None and collection.count() == 0:
            for _, row in df.iterrows():
                try:
                    collection.add(
                        documents=[row.get("Techstack", "")],
                        metadatas=[{"links": row.get("Links", "")}],
                        ids=[str(uuid.uuid4())]
                    )
                except Exception as e:
                    st.warning(f"Error adding document to collection: {e}")
        st.session_state["portfolio_loaded"] = True
        st.success("✅ Portfolio database loaded successfully!")
    else:
        st.warning("⚠️ 'portfolio.csv' not found. Please upload it to enable matching.")

# Input field for job URL
url = st.text_input("🔗 Enter a job posting URL:")

if st.button("Process Job Posting"):
    if not url:
        st.warning("⚠️ Please enter a valid job posting URL.")
        st.stop()

    # Check required runtime components before proceeding
    missing = []
    if WebBaseLoader is None:
        missing.append("langchain (web loader)")
    if PromptTemplate is None:
        missing.append("langchain (prompt templates)")
    if ChatGroq is None:
        missing.append("langchain-groq (Groq LLM)")
    if collection is None:
        # chromadb is optional — we can continue but portfolio matching will be skipped
        st.info("⚠️ chromadb/collection not available: portfolio matching will be skipped.")

    if missing:
        st.error("Required packages are not available in this runtime:\n- " + "\n- ".join(missing))
        st.info("Add them to requirements.txt and redeploy, or run locally with the same Python interpreter.")
        st.stop()

    try:
        # Step 1: Load job page
        os.environ["USER_AGENT"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
        )
        loader = WebBaseLoader(url)
        loaded = loader.load()
        if not loaded:
            st.error("Could not load page content from the given URL.")
            st.stop()
        page_data = loaded.pop().page_content

        # Step 2: Extract job details using Groq LLM
        llm = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant"
        )

        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            Extract the job postings and return JSON with keys:
            `role`, `experience`, `skills`, and `description`.
            Only return valid JSON (no explanation).
            ### VALID JSON (NO PREAMBLE):
            """
        )

        chain_extract = prompt_extract | llm
        res = chain_extract.invoke({'page_data': page_data})
        job = json.loads(res.content)

        st.subheader("📄 Extracted Job Details")
        st.json(job)

        # Step 3: Query ChromaDB for relevant portfolio links (if available)
        matched_links = []
        if collection is not None:
            try:
                skills_text = job.get('skills', '') or job.get('description', '')
                query_result = collection.query(query_texts=[skills_text], n_results=3)
                # query_result["metadatas"] -> list of lists of metadata dicts
                metas = query_result.get("metadatas", [[]])[0]
                for m in metas:
                    if isinstance(m, dict) and m.get("links"):
                        matched_links.append(m.get("links"))
            except Exception as e:
                st.warning(f"Portfolio matching failed: {e}")

        if matched_links:
            st.subheader("🔗 Matched Portfolio Links")
            for link in matched_links:
                st.markdown(f"- [{link}]({link})")
        else:
            st.info("No portfolio links matched or chromadb not available.")

        # Step 4: Generate Cold Email
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Muzzammil, a business development executive at A.
            Accenture builds AI & software consulting solutions that automate and optimize business processes.
            Write a professional cold email to the client about this job,
            showing how Accenture can fulfill their needs.
            Mention the most relevant portfolio links below:
            {link_list}
            Do not include any preamble.
            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | llm
        email_res = chain_email.invoke({
            "job_description": json.dumps(job, indent=2),
            "link_list": "\n".join(matched_links) if matched_links else "No matched links available"
        })

        st.subheader("📧 Generated Cold Email")
        st.write(email_res.content)

    except Exception as e:
        st.error(f"❌ Error: {e}")
