# 🚀 QUICK REFERENCE CARD

## 🎯 **START THE SYSTEM**

```bash
# Terminal 1: Start Backend
start_backend.bat

# Browser: Open Frontend
frontend/index.html
```

---

## 💡 **DEMO QUERIES**

### **Query 1: Moon Vacation (Simple)**
```
Query: "7-day luxury Moon vacation with spacewalk experience"
Budget: $20,000,000
Passengers: 2
Location: Moon
```

### **Query 2: Mars Adventure (Medium)**
```
Query: "14-day Mars colony tour with rover racing and Olympus Mons expedition"
Budget: $80,000,000
Passengers: 1
Location: Mars
```

### **Query 3: Ultimate Journey (Complex)**
```
Query: "30-day trip visiting Moon, Mars, and Asteroid Belt with VVIP experiences"
Budget: $250,000,000
Passengers: 4
Location: (leave empty)
```

---

## 🏗️ **ARCHITECTURE (1-Sentence Each)**

1. **Orchestrator Agent** - Coordinates all other agents using LangGraph
2. **Knowledge Agent** - Retrieves context from Chroma (vector) + SQLite (structured)
3. **Optimizer Agent** - Generates itineraries using GPT-4o
4. **Validator Agent** - Checks feasibility (timing, budget, safety)
5. **Guardrail Agent** - Prevents hallucinations by verifying against database

---

## 🔑 **KEY TALKING POINTS**

✅ **Multi-Agent System** - Not a chatbot, collaborative AI team
✅ **Hybrid RAG** - Vector (semantic) + Structured (exact) search
✅ **Guardrails** - Prevents AI from making up fake hotels/ships
✅ **Explainable** - Shows reasoning for every decision
✅ **Production-Ready** - FastAPI, error handling, API docs

---

## 📊 **TECH STACK (Quick List)**

- **Backend:** FastAPI (Python)
- **AI:** GPT-4o + Azure Embeddings
- **Orchestration:** LangGraph
- **Vector DB:** Chroma
- **Structured DB:** SQLite
- **Frontend:** HTML/CSS/JavaScript

---

## 🔗 **IMPORTANT URLS**

- **Frontend:** file:///C:/AI/Mani/TravelIternaryOperator/frontend/index.html
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/

---

## 🐛 **QUICK FIXES**

**Backend not starting?**
```bash
set PYTHONPATH=%CD%
uv run python backend/main.py
```

**Frontend can't connect?**
- Check backend is running on port 8000
- Check browser console (F12) for errors

**Slow response?**
- Normal! AI agents are doing complex reasoning
- Show backend console to explain what's happening

---

## 💬 **ELEVATOR PITCH (30 seconds)**

"Stellar Voyage AI is a multi-agent system that plans interplanetary travel for SpaceX VVIPs. It uses LangGraph to coordinate 5 specialized AI agents: one retrieves context using hybrid RAG, another generates itineraries with GPT-4o, and two more validate and verify to prevent errors. The result? Optimized 14-day Mars trips in 5 seconds instead of 5 hours of manual planning."

---

## 🎯 **DEMO FLOW (2 minutes)**

1. **Show UI** (10 sec) - "Futuristic interface for space travel"
2. **Enter Query** (10 sec) - Use Query 1 from above
3. **Explain While Loading** (30 sec) - "Agents are working: retrieve → optimize → validate → verify"
4. **Show Results** (60 sec) - "7-day itinerary, $15M cost, validated, verified, explainable"
5. **Highlight Features** (10 sec) - "Multi-agent, RAG, guardrails, production-ready"

---

## 📁 **FILE LOCATIONS**

```
backend/
├── agents/orchestrator.py      ← Multi-agent workflow
├── agents/knowledge_agent.py   ← RAG implementation
├── main.py                     ← FastAPI server
└── data/stellar_voyage.db      ← Structured data

frontend/
└── index.html                  ← Web UI

chroma_db/                      ← Vector database
.env                            ← API keys (secure!)
```

---

## 🏆 **WHY THIS WINS**

1. **Not a chatbot** - Multi-agent collaboration
2. **Production-grade** - FastAPI, error handling, validation
3. **Creative** - Interplanetary travel (not boring hotels)
4. **Explainable** - Shows AI reasoning
5. **Safe** - Guardrails prevent hallucinations
6. **Scalable** - Modular architecture, API-first

---

**Print this and keep it handy during the demo! 📄**
