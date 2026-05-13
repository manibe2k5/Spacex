# 🚀 STELLAR VOYAGE AI - Interplanetary Travel Planner

**An AI-Powered Multi-Agent System for SpaceX VVIP Travel Planning**

Built for the AI Hackathon | Production-Grade Architecture | 2026 Industry Standards

---

## 🌟 **WHAT IS THIS?**

Stellar Voyage AI is a futuristic travel planning system that helps VVIPs plan luxury interplanetary journeys to:
- 🌙 **Moon** (Lunar resorts, spacewalks)
- 🔴 **Mars** (Colony tours, Olympus Mons expeditions)
- 🪐 **Asteroid Belt** (16 Psyche mining tours)
- 🛸 **Titan** (Saturn's moon floating cities)
- 🌍 **Earth Orbit** (ISS-2 space station)

---

## 🏗️ **ARCHITECTURE**

### **Multi-Agent System (LangGraph)**
```
User Query
    ↓
ORCHESTRATOR AGENT (Coordinator)
    ↓
    ├─→ KNOWLEDGE AGENT (RAG - Retrieves context)
    │   ├─ Chroma Vector DB (semantic search)
    │   └─ SQLite (structured data)
    ↓
    ├─→ OPTIMIZER AGENT (Generates itinerary with GPT-4o)
    ↓
    ├─→ VALIDATOR AGENT (Checks feasibility)
    ↓
    └─→ GUARDRAIL AGENT (Prevents hallucinations)
    ↓
Final Itinerary → User
```

### **Tech Stack**
- **Backend:** FastAPI (Python)
- **AI Orchestration:** LangGraph
- **LLM:** GPT-4o (Azure)
- **Embeddings:** Azure text-embedding-3-large
- **Vector DB:** Chroma
- **Structured DB:** SQLite
- **Frontend:** HTML/CSS/JavaScript (React-style)

---

## 🚀 **QUICK START (4 STEPS)**

### **Step 1: Verify Environment**
```bash
# Check if dependencies are installed
uv --version
python --version
```

### **Step 2: Start Backend Server**
```bash
# From project root
set PYTHONPATH=%CD%
uv run python backend/main.py
```

You should see:
```
Initializing Stellar Voyage AI...
Knowledge Agent initialized!
Optimizer Agent initialized!
Validator Agent initialized!
Guardrail Agent initialized!
Orchestrator Agent ready!
API Ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 3: Open Frontend**
```bash
# Open in browser
start frontend/index.html
```

Or manually open `frontend/index.html` in your browser.

### **Step 4: Test the System**
1. Enter a query like: "7-day luxury Moon vacation with spacewalk"
2. Set budget: $20,000,000
3. Click "Generate Itinerary"
4. Watch the AI agents work!

---

## 📊 **WHAT MAKES THIS IMPRESSIVE?**

### **1. Multi-Agent Architecture**
- Not a simple chatbot - multiple specialized AI agents collaborate
- Each agent has a specific role (like a real team)
- LangGraph orchestrates complex workflows

### **2. Hybrid RAG System**
- **Vector Search** (Chroma): Semantic similarity for unstructured knowledge
- **Structured Queries** (SQLite): Exact data (prices, dates, availability)
- **Combined Context**: Best of both worlds

### **3. Guardrails & Validation**
- **Validator Agent**: Checks timing conflicts, budget feasibility
- **Guardrail Agent**: Prevents AI hallucinations (verifies against database)
- **Production-ready**: Won't recommend fake hotels or ships

### **4. Explainable AI**
- Every itinerary comes with reasoning
- Shows why specific choices were made
- Transparent decision-making

### **5. Futuristic Use Case**
- Not boring hotel bookings - interplanetary travel!
- Creative: Mars colonies, asteroid mining, lunar resorts
- Demonstrates advanced AI capabilities

---

## 🎯 **DEMO SCENARIOS**

### **Scenario 1: Quick Lunar Getaway**
```
Query: "7-day luxury Moon vacation with spacewalk experience"
Budget: $20M
Result: Lunar Gateway Hotel + Shackleton Crater Resort + Private spacewalk
```

### **Scenario 2: Mars Adventure**
```
Query: "14-day Mars colony tour with rover racing and Olympus Mons expedition"
Budget: $80M
Result: Full Mars experience with Starbase Alpha stay
```

### **Scenario 3: Ultimate Journey**
```
Query: "30-day trip visiting Moon, Mars, and Asteroid Belt with VVIP experiences"
Budget: $250M
Result: Multi-destination itinerary with exclusive access
```

---

## 📁 **PROJECT STRUCTURE**

```
TravelIternaryOperator/
├── backend/
│   ├── agents/
│   │   ├── knowledge_agent.py      # RAG retrieval
│   │   ├── optimizer_agent.py      # Itinerary generation
│   │   ├── validator_guardrail.py  # Validation & safety
│   │   └── orchestrator.py         # LangGraph coordinator
│   ├── data/
│   │   ├── init_db.py              # SQLite setup
│   │   ├── init_vector_db.py       # Chroma setup
│   │   └── stellar_voyage.db       # Structured data
│   ├── utils/
│   │   └── llm_client.py           # LLM connection
│   ├── config.py                   # Configuration
│   └── main.py                     # FastAPI server
├── frontend/
│   └── index.html                  # Web UI
├── chroma_db/                      # Vector database
├── .env                            # API keys (secure)
├── pyproject.toml                  # Dependencies
└── README.md                       # This file
```

---

## 🔧 **API ENDPOINTS**

### **POST /plan-travel**
Generate travel itinerary

**Request:**
```json
{
  "query": "7-day Moon vacation",
  "constraints": {
    "max_budget": 20000000,
    "passengers": 2,
    "location": "Moon"
  }
}
```

**Response:**
```json
{
  "success": true,
  "itinerary": {...},
  "validation": {...},
  "verification": {...}
}
```

### **GET /destinations**
List all available destinations

### **GET /starships**
List all available spacecraft

### **GET /docs**
Interactive API documentation (Swagger UI)
Visit: http://localhost:8000/docs

---

## 🧪 **TESTING**

### **Test Backend Only**
```bash
# Test Knowledge Agent
set PYTHONPATH=%CD%
uv run python backend/agents/knowledge_agent.py

# Test Optimizer Agent
uv run python backend/agents/optimizer_agent.py

# Test Validator & Guardrail
uv run python backend/agents/validator_guardrail.py

# Test Full Orchestrator
uv run python backend/agents/orchestrator.py
```

### **Test API**
```bash
# Using curl
curl -X POST http://localhost:8000/plan-travel \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"7-day Moon trip\", \"constraints\": {\"max_budget\": 20000000}}"
```

---

## 🎨 **CUSTOMIZATION**

### **Add More Destinations**
Edit `backend/data/init_db.py` and add to `destinations` list:
```python
("DEST-007", "Europa Base", "Jupiter Moon", ...)
```

Then re-run:
```bash
uv run python backend/data/init_db.py
```

### **Add More Knowledge**
Edit `backend/data/init_vector_db.py` and add to `documents` list:
```python
{
    "id": "doc_013",
    "text": "Your new knowledge here...",
    "metadata": {"category": "...", "location": "..."}
}
```

Then re-run:
```bash
set PYTHONPATH=%CD%
uv run python backend/data/init_vector_db.py
```

---

## 🏆 **JURY PRESENTATION POINTS**

### **Technical Excellence**
✅ Multi-agent architecture (LangGraph)
✅ Hybrid RAG (Vector + Structured)
✅ Guardrails for production safety
✅ Explainable AI decisions
✅ FastAPI with async support
✅ Type-safe with Pydantic

### **Innovation**
✅ Futuristic use case (interplanetary travel)
✅ Creative agent collaboration
✅ Real-time validation and conflict detection
✅ Personalized VVIP experiences

### **Production-Ready**
✅ Error handling and retries
✅ API documentation (Swagger)
✅ Modular architecture
✅ Scalable design
✅ Security (API keys in .env)

---

## 🐛 **TROUBLESHOOTING**

### **Issue: "Module not found"**
```bash
# Solution: Set PYTHONPATH
set PYTHONPATH=%CD%
```

### **Issue: "Connection refused"**
- Make sure backend is running on port 8000
- Check firewall settings

### **Issue: "Embedding API Error"**
- Verify .env file has correct API key
- Check network connection

### **Issue: "No results generated"**
- Check if databases are initialized
- Run init_db.py and init_vector_db.py again

---

## 📚 **LEARNING RESOURCES**

- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Chroma:** https://docs.trychroma.com/
- **RAG:** https://www.pinecone.io/learn/retrieval-augmented-generation/

---

## 🎉 **DEMO SCRIPT FOR JURY**

1. **Introduction (30 sec)**
   - "Stellar Voyage AI - Interplanetary travel planner for SpaceX VVIPs"
   - "Multi-agent system with RAG, LangGraph, and GPT-4o"

2. **Architecture Overview (1 min)**
   - Show diagram of agent workflow
   - Explain each agent's role

3. **Live Demo (2 min)**
   - Enter: "14-day luxury trip to Moon and Mars"
   - Show real-time generation
   - Highlight validation and verification

4. **Technical Deep Dive (1 min)**
   - Show code structure
   - Explain RAG hybrid approach
   - Demonstrate guardrails

5. **Q&A**

---

## 👨‍💻 **AUTHOR**

Built for AI Hackathon 2026
Demonstrates: Multi-Agent AI, RAG, LangGraph, Production Architecture

---

## 📄 **LICENSE**

MIT License - Feel free to use and modify!

---

**🚀 Ready to explore the cosmos? Start the backend and open the frontend!**
