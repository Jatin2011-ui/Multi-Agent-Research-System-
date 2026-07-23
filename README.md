# 🔬 ResearchMind — Multi-Agent Research Pipeline

A multi-agent AI system that researches any topic autonomously using **Groq (LLaMA 3.3)** + **Tavily**, then writes and critiques a structured report — all through a clean Streamlit UI.

---

## 🧠 How It Works

The pipeline runs 4 agents/chains in sequence:

```
User Topic
    │
    ▼
[1] Search Agent     →  Finds top 5 web sources via Tavily
    │
    ▼
[2] Reader Agent     →  Scrapes the most relevant URL for deep content
    │
    ▼
[3] Writer Chain     →  Drafts a structured research report
    │
    ▼
[4] Critic Chain     →  Reviews and scores the report (X/10)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq — `llama-3.3-70b-versatile` |
| Agent Framework | LangChain (`create_react_agent`, `AgentExecutor`) |
| Web Search | Tavily API |
| Web Scraping | BeautifulSoup4 + Requests |
| UI | Streamlit |
| Env Management | python-dotenv |

---

## 📁 Project Structure

```
multi-agent/
├── app.py            # Streamlit UI
├── agents.py         # LLM, agents, writer & critic chains
├── pipeline.py       # Orchestrates the 4-step pipeline
├── tools.py          # web_search and scrape_url tools
├── requirements.txt  # Dependencies
├── .env              # API keys (never commit this)
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/your-username/multi-agent-research.git
cd multi-agent-research
```

### 2. Create and activate virtual environment
```bash
# Using uv (recommended)
uv venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
uv pip install -r requirements.txt
```

### 4. Set up your `.env` file
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Get your keys:
- Groq → https://console.groq.com
- Tavily → https://app.tavily.com

---

## 🚀 Run the App

```bash
uv run streamlit run app.py
```

Or if your venv is already activated:
```bash
streamlit run app.py
```

---

## 💻 Run via Terminal (no UI)

```bash
python pipeline.py
```

You'll be prompted to enter a research topic directly.

---

## 📦 Requirements

```
langchain
langchain-groq
langchain-community
langchain-core
tavily-python
beautifulsoup4
requests
python-dotenv
rich
streamlit
```

---

## 🖥️ UI Features

- **Live step progress pills** — Search → Reader → Writer → Critic
- **Tabbed results** — Report, Critic Feedback, Search Results, Scraped Content, Run Log
- **Word count stats** for each pipeline stage
- **Download report** as `.txt` or full pipeline state as `.json`
- **API key inputs** in sidebar (or loaded from `.env`)

---

## 📸 Output Format

The writer produces a structured report:
- Introduction
- Key Findings (minimum 3 points)
- Conclusion
- Sources (all URLs found)

The critic scores it:
```
Score: X/10

Strengths:
- ...

Areas to Improve:
- ...

One line verdict: ...
```

---

## 🔒 Security

- Never commit your `.env` file — it's in `.gitignore`
- API keys can also be entered directly in the Streamlit sidebar

---

## 👨‍💻 Author

**Jatin Prabhakar**  
B.Tech CSE — Bharati Vidyapeeth's College of Engineering, New Delhi  







