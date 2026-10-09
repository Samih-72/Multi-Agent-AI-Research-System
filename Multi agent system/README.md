# 🧠 NEXUS — Multi-Agent AI Research System

A multi-agent AI system that researches any topic for you. Four specialized AI components work together as a pipeline: they **search** the web, **read** the most relevant source, **write** a structured research report, and **critique** the report with a score and feedback.

Built with **LangChain**, **LangGraph**, **Groq**, **Tavily** and **Streamlit**.

---

## ✨ How it works

```
   Topic
     │
     ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ 🔍 Search    │──▶│ 📖 Reader    │──▶│ ✍️ Writer     │──▶│ 🧐 Critic     │
│    Agent     │   │    Agent     │   │    Chain     │   │    Chain     │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
 Finds recent,      Picks the best     Writes a report    Scores the report
 reliable sources   URL and scrapes    with findings      /10 with strengths
 (Tavily)           it for depth       and sources        and improvements
```

| Component | Type | What it does |
|---|---|---|
| **Search Agent** | Agent + `web_search` tool | Uses the Tavily API to find recent, reliable sources (titles, URLs, snippets) |
| **Reader Agent** | Agent + `scrape_url` tool | Chooses the most relevant URL and extracts clean text with Requests + BeautifulSoup |
| **Writer Chain** | LCEL chain | Turns the research into a report: Introduction, Key Findings, Conclusion, Sources |
| **Critic Chain** | LCEL chain | Reviews the report and returns a score out of 10, its strengths, areas to improve and a one-line verdict |

The steps share one **state** object, so each agent builds on the previous agent's output.

## 🖥️ Streamlit UI

- Live progress card for each agent, with timings
- Suggested topics to try with one click
- Tabs for the report, the critique, the sources and the raw output
- Score tiles parsed from the critic's feedback
- Download the report, or a full bundle, as Markdown
- Automatic retry when the API hits a rate limit

## 🛠️ Tech stack

- **Python**
- **LangChain / LangGraph**: agents (`create_agent`), tools (`@tool`) and LCEL chains
- **Groq**: fast LLM inference (default model `openai/gpt-oss-120b`)
- **Tavily**: web search API
- **Requests + BeautifulSoup**: web scraping
- **Streamlit**: user interface
- **python-dotenv**: environment variables

## 📁 Project structure

```
├── app.py              # Streamlit UI
├── pipeline.py         # Search → Read → Write → Critique pipeline (also runs from the terminal)
├── agents.py           # LLM setup, Search/Reader agents, Writer/Critic chains
├── tools.py            # web_search (Tavily) and scrape_url (BeautifulSoup) tools
├── requirements.txt
├── .env.example        # Template for your API keys
└── .streamlit/
    └── config.toml     # Dark theme
```

## 🚀 Getting started

**1. Clone the repo**
```bash
git clone https://github.com/Samih-72/Multi-Agent-AI-Research-System.git
cd Multi-Agent-AI-Research-System
```

**2. Create a virtual environment and install the dependencies**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**3. Add your API keys**

Copy `.env.example` to `.env` and fill in your keys:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_MODEL=openai/gpt-oss-120b
```
- Get a Groq key at https://console.groq.com
- Get a Tavily key at https://tavily.com

**4. Run it**
```bash
# Streamlit UI
streamlit run app.py

# Or from the terminal
python pipeline.py
```

## 📚 What I learned

- How AI agents differ from simple LLM chains
- Tool calling: giving an LLM tools it can decide to use
- Designing multi-agent pipelines with shared state
- Building chains with LCEL and getting structured output through prompt engineering
- Using an LLM as a critic to evaluate output automatically
- Handling API rate limits and managing secrets safely
- Building a polished Streamlit UI for an AI application

## 🙏 Acknowledgements

Built while following the hands-on tutorial by **Akarsh Vyas**: [Multi-Agent Research System](https://github.com/AkarshVyas/Multi-agent-research-system).

---

⭐ If you found this useful, consider giving the repo a star!
