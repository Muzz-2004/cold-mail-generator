📧 Cold Mail Generator

A simple AI-powered **cold email generator** built with Python and Streamlit. This tool helps you create personalized outreach emails quickly — ideal for business development, job applications, networking, and sales outreach.


🚀 Features

- 🧠 Generate cold emails automatically using AI  
- ✍️ Easy to customize templates and user inputs  
- 📄 Uses `portfolio.csv` for personal portfolio references  
- 💻 Web UI via Streamlit — interactively create emails  
- 📦 Pure Python stack with minimal dependencies  

 🛠 Tech Stack

- **Python** — Core programming language  
- **Streamlit** — Web interface  
- **AI/LLM API** — Email generation  
- **CSV** — Portfolio/reference data  

 📁 Project Structure

cold-mail-generator/
│
├── app.py
├── portfolio.csv
├── requirements.txt
├── .gitignore
└── README.md

⚡ Getting Started

 ✅ Prerequisites

- Python 3.8+
- API Key (if required for AI service)


 📥 Installation

1. Clone the repository

```bash
git clone https://github.com/Muzz-2004/cold-mail-generator.git
cd cold-mail-generator
Create virtual environment

python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
Install dependencies

pip install -r requirements.txt
Set environment variable (if needed)

export API_KEY="your_api_key_here"   # Linux/Mac
setx API_KEY "your_api_key_here"     # Windows
▶️ Run the Application
Start the Streamlit app:

streamlit run app.py
Open in browser:

http://localhost:8501

📄 How It Works

Edit portfolio.csv with your details and links.

Open the web interface.

Enter recipient and company details.

Click Generate.

"Get a ready-to-use cold email."
