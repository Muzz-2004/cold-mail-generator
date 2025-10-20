from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st


class Chain:
    def __init__(self):
        # Load your API key from Streamlit Secrets
        groq_api_key = st.secrets["GROQ_API_KEY"]

        # Initialize Groq LLM
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-vers"
        )

    def extract_research_info_chain(self):
        """
        Creates a prompt and chain for extracting structured research paper information.
        """
        prompt = ChatPromptTemplate.from_template(
            """
            Extract the following information from the given text:
            - Research Title
            - Problem Statement
            - Solution
            - Result

            Return the response in JSON format with keys:
            ["research_title", "problem_statement", "solution", "result"]

            Text: {text}
            """
        )

        return prompt | self.llm

    def generate_cold_mail_chain(self):
        """
        Creates a prompt and chain for generating a cold email based on extracted research details.
        """
        prompt = ChatPromptTemplate.from_template(
            """
            You are a professional email copywriter.

            Write a cold email to a potential collaborator or professor based on the following research details.

            Ensure the tone is:
            - Polite and respectful
            - Clearly conveys interest in collaboration or discussion
            - Avoids generic statements
            - Well-formatted for readability

            Research Details:
            {research_details}

            Return only the email body (no JSON).
            """
        )

        return prompt | self.llm
