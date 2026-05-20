
````markdown
# Enterprise Multi-Agent AI Workflow Studio

Production-grade Agentic AI Workflow Platform built using  
Streamlit + LangGraph + Ollama + MongoDB Atlas Vector Search + MCP-inspired Tool Orchestration.

This project demonstrates how enterprise AI agents can:
- reason
- plan
- retrieve knowledge
- collaborate
- call tools
- generate business insights

through modular multi-agent workflows.

---

# 🚀 Features

## ✅ Multi-Agent AI Workflow
- Planner Agent
- RAG Agent
- Tool Agent
- Supervisor Agent

## ✅ Enterprise RAG
- MongoDB Atlas Vector Search
- Semantic document retrieval
- PDF + Spreadsheet ingestion

## ✅ MCP-Style Tool Orchestration
- Tool registry
- Tool execution layer
- Modular business tools

## ✅ Streamlit Real-Time UI
- Interactive workflow execution
- Chat-like task interface
- Agent output visualization

## ✅ Hybrid AI Architecture
- Ollama local LLM support
- Cloud-agnostic architecture
- Easily extendable to Azure/OpenAI

## ✅ Production-Oriented Design
- Modular architecture
- LangGraph orchestration
- Docker support
- Enterprise-ready folder structure

---

# 🏗️ Architecture

```text
User
 │
 ▼
Streamlit UI
 │
 ▼
LangGraph Orchestrator
 ├── Planner Agent
 ├── RAG Agent
 ├── Tool Agent
 └── Supervisor Agent
        │
        ├── MongoDB Atlas Vector Search
        ├── MCP Tool Server
        └── Ollama LLM
```

---

# 📂 Project Structure

```bash
enterprise-agent-studio/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── agents/
├── rag/
├── llm/
├── mcp/
├── workflow/
├── utils/
└── data/
```

---

# 🧠 Example Use Cases

## Retail Analytics
- Analyze customer purchases
- Detect overdue payments
- Generate business insights

## Finance Workflow
- Invoice aging analysis
- Delayed collection reports
- Risk detection

## HR Intelligence
- Employee attrition analysis
- Workforce insights
- Retention recommendations

## Operations Monitoring
- Shipment delay analytics
- SLA breach detection
- Logistics bottleneck analysis

---

# 📊 Sample Datasets Included

- Retail Dataset (50+ records)
- Finance Dataset (50+ records)
- HR Dataset (50+ records)
- Operations Dataset (50+ records)

---

# 📄 Sample RAG Documents Included

- Retail reference PDF
- Finance reference PDF
- HR reference PDF
- Operations reference PDF

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/Siva-Dev-001/enterprise-agent-studio.git

cd enterprise-agent-studio
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Setup Environment Variables

Create `.env`

```env
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

MONGO_URI=your_mongodb_connection

OPENAI_API_KEY=your_openai_api_key
```
Note:

```text
Suppose your feel that ollama hitting the maximum CPU. Use OPENAI API.
---

# 🦙 Setup Ollama

Install Ollama:

https://ollama.com/

Pull model:

```bash
ollama pull llama3
```

Run model:

```bash
ollama run llama3
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

---

# 🐳 Docker Deployment

Build Docker image:

```bash
docker build -t enterprise-agent .
```

Run container:

```bash
docker run -p 8501:8501 enterprise-agent
```

---

# 📌 Example Prompt

```text
Analyze uploaded sales CSV, identify top products,
detect delayed payments, and generate summary report.
```

---

# 🧾 Sample Output

## Plan
```text
1. Load uploaded dataset
2. Analyze sales metrics
3. Detect overdue payments
4. Retrieve related policy documents
5. Generate executive summary
```

## Context (RAG)
```text
Payment terms are Net 30.
Invoices unpaid after 30 days are marked overdue.
```

## Final Output
```text
Total Revenue: ₹12,45,000
Overdue Invoices: 17
Top Product: Premium Denim Jeans
Recommendation: Escalate invoices beyond 15 days.
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Agent Orchestration | LangGraph |
| LLM | Ollama |
| Vector Database | MongoDB Atlas |
| RAG | Embeddings + Vector Search |
| Backend | Python |
| Tool Layer | MCP-style registry |
| Deployment | Docker |

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Built for enterprise-scale Agentic AI workflow experimentation, portfolio showcasing, and AI engineering interviews.
````
