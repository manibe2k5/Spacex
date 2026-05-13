# CONTEXT.md - Stellar Voyage AI Project

## Project Overview
**Stellar Voyage AI** is a production-grade multi-agent AI system for SpaceX VVIP interplanetary travel planning, built for an AI Hackathon with a 4-hour development timeframe. The system uses LangGraph to orchestrate multiple specialized AI agents that collaborate to generate, validate, and verify luxury space travel itineraries.

## System Architecture

### Multi-Agent Workflow
```
User Query → ORCHESTRATOR AGENT
    ↓
    1. KNOWLEDGE AGENT (RAG - Hybrid Search)
       ├─ Chroma Vector DB (semantic search on 12 space travel documents)
       └─ SQLite (structured queries: starships, destinations, launch windows)
    ↓
    2. OPTIMIZER AGENT (GPT-4o generates itinerary)
    ↓
    3. VALIDATOR AGENT (checks feasibility: budget, timing, safety)
    ↓
    4. GUARDRAIL AGENT (prevents hallucinations, verifies against database)
    ↓
Final Itinerary → User (via FastAPI REST API)
```

### Technology Stack
- **Backend Framework:** FastAPI (Python) on port 8080
- **AI Orchestration:** LangGraph (state machine for agent coordination)
- **LLM:** Azure-hosted GPT-4o (genailab-maas-gpt-4o)
- **Embeddings:** Azure text-embedding-3-large
- **Vector Database:** Chroma (PersistentClient for data persistence)
- **Structured Database:** SQLite (stellar_voyage.db)
- **Frontend:** Vanilla HTML/CSS/JavaScript (React-style, space-themed UI)
- **Package Manager:** uv (Python dependency management)

## Project Structure
```
TravelIternaryOperator/
├── backend/
│   ├── agents/
│   │   ├── knowledge_agent.py      # RAG: Hybrid search + destination validation
│   │   ├── optimizer_agent.py      # GPT-4o itinerary generation with JSON parsing
│   │   ├── validator_guardrail.py  # ValidatorAgent + GuardrailAgent
│   │   └── orchestrator.py         # LangGraph state machine coordinator
│   ├── data/
│   │   ├── init_db.py              # SQLite initialization (5 starships, 6 destinations, 5 launch windows)
│   │   ├── init_vector_db.py       # Chroma initialization (12 space travel documents)
│   │   └── stellar_voyage.db       # SQLite database file
│   ├── utils/
│   │   └── llm_client.py           # LLM connection with SSL bypass for corporate networks
│   ├── config.py                   # Environment variable loader (.env)
│   └── main.py                     # FastAPI server (port 8080)
├── frontend/
│   └── index.html                  # Space-themed UI with animated starfield
├── chroma_db/                      # Chroma vector database storage
├── .env                            # API keys (GENAI_API_KEY, GENAI_BASE_URL, etc.)
├── pyproject.toml                  # Dependencies (langchain-openai, langgraph, chromadb, fastapi)
├── README.md                       # User documentation
└── CONTEXT.md                      # This file (developer context)
```

## Key Components Deep Dive

### 1. Knowledge Agent (backend/agents/knowledge_agent.py)
**Purpose:** Retrieval-Augmented Generation (RAG) with hybrid search

**Key Features:**
- **Vector Search (Chroma):** Semantic similarity search on 12 space travel knowledge documents
- **Structured Queries (SQLite):** Exact data retrieval (starships, destinations, launch windows, VVIP profiles)
- **Destination Validation:** Scans query text for 25+ Earth destination keywords (kashmir, kailash, paris, london, etc.)
- **Guardrail:** Only allows space destinations (Moon, Mars, Earth Orbit, Asteroid Belt, Titan)

**Critical Logic:**
```python
# Destination validation happens BEFORE LLM call
earth_destinations = ["kashmir", "kailash", "paris", "london", ...]
if any(dest in query_lower for dest in earth_destinations):
    return error response with available destinations
```

**Output:** Combined context from vector search + structured queries, or validation error

### 2. Optimizer Agent (backend/agents/optimizer_agent.py)
**Purpose:** Generate detailed travel itineraries using GPT-4o

**Key Features:**
- **LLM Prompt Engineering:** Structured prompt with context, constraints, and JSON schema
- **Robust JSON Parsing:** Multiple fallback strategies
  1. Direct JSON parsing
  2. Regex extraction from markdown code blocks
  3. Fallback template generation
- **Confidence Scoring:** Self-assessment of itinerary quality

**Critical Logic:**
```python
# JSON parsing with fallbacks
try:
    return json.loads(response)
except:
    # Try regex extraction
    match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Fallback template
    return basic_itinerary_template
```

**Output:** Structured itinerary with daily_plan, total_cost_usd, duration_days, highlights, reasoning

### 3. Validator Agent (backend/agents/validator_guardrail.py - ValidatorAgent)
**Purpose:** Check itinerary feasibility

**Validation Checks:**
1. **Budget Check:** total_cost_usd <= max_budget
2. **Timing Check:** No scheduling conflicts, realistic activity durations
3. **Safety Check:** Proper safety equipment, medical clearance, emergency protocols
4. **Duration Check:** Prevents division by zero errors

**Output:** `{is_valid: bool, issues: [list of problems], confidence_score: float}`

### 4. Guardrail Agent (backend/agents/validator_guardrail.py - GuardrailAgent)
**Purpose:** Prevent AI hallucinations and verify data accuracy

**Verification Checks:**
1. **CHECK 0 (Critical):** Scan itinerary text for Earth destinations → Mark as critical hallucination
2. **CHECK 1:** Verify all destinations exist in database
3. **CHECK 2:** Verify all starships exist in database
4. **CHECK 3:** Verify all hotels/accommodations exist in database

**Critical Logic:**
```python
# Earth destination detection
earth_destinations = ["kashmir", "kailash", "paris", ...]
if any(dest in itinerary_text_lower for dest in earth_destinations):
    hallucinations.append({
        "type": "invalid_destination",
        "description": "Earth destination detected",
        "severity": "critical"
    })
```

**Output:** `{is_safe: bool, hallucinations: [list of issues], verified_entities: {...}}`

### 5. Orchestrator Agent (backend/agents/orchestrator.py)
**Purpose:** LangGraph state machine that coordinates all agents

**State Flow:**
```python
START → retrieve_knowledge → optimize_itinerary → validate_itinerary → 
verify_itinerary → should_regenerate? → [regenerate OR finalize] → END
```

**Conditional Logic:**
- **Regeneration:** If validation/verification fails (max 2 attempts)
- **Critical Errors:** If destination validation fails or critical hallucinations detected → Skip to error response
- **Success:** All checks pass → Return final itinerary

**State Schema:**
```python
class AgentState(TypedDict):
    query: str
    constraints: dict
    context: str
    itinerary: dict
    validation: dict
    verification: dict
    regeneration_count: int
    final_response: dict
```

### 6. FastAPI Server (backend/main.py)
**Purpose:** REST API endpoint for frontend communication

**Endpoints:**
- **POST /plan-travel:** Main endpoint for itinerary generation
- **GET /destinations:** List all available destinations
- **GET /starships:** List all available starships
- **GET /docs:** Swagger UI documentation

**Error Handling:**
- Detects destination validation errors (`destination_not_available`)
- Formats friendly error messages for frontend
- Returns structured JSON responses

### 7. Frontend (frontend/index.html)
**Purpose:** User interface for travel planning

**Key Features:**
- **Animated Starfield:** 100 twinkling stars for space theme
- **Input Form:** Query textarea, budget, passengers, destination dropdown
- **Example Queries:** Pre-filled scenarios (Moon vacation, Mars tour, multi-destination)
- **Results Display:** Itinerary with day-by-day plan, stats, validation badges
- **Error Handling:** Special UI for destination validation errors (orange warning box)
- **Issue Display:** Shows validation issues (red box) and verification issues (orange box) with details

**API Integration:**
```javascript
fetch('http://localhost:8080/plan-travel', {
    method: 'POST',
    body: JSON.stringify({query, constraints})
})
```

## Database Schemas

### SQLite (stellar_voyage.db)

**starships table:**
```sql
id, name, capacity, cost_per_day_usd, speed_km_per_sec, luxury_rating, description
```
Sample: Starship Odyssey, Celestial Cruiser, Nebula Express, Quantum Voyager, Titan Transporter

**destinations table:**
```sql
id, name, location, distance_from_earth_km, travel_time_days, cost_per_day_usd, description, activities
```
Sample: Moon (Lunar Gateway Hotel), Mars (Starbase Alpha), Earth Orbit (ISS-2), Asteroid Belt (16 Psyche), Titan (Kraken Mare)

**launch_windows table:**
```sql
id, destination_id, start_date, end_date, optimal_travel_time_days, notes
```

**vvip_profiles table:**
```sql
id, name, preferences, budget_range, past_destinations
```

### Chroma Vector DB (chroma_db/)
**Collection:** stellar_voyage_knowledge

**Documents (12 total):**
- Space travel basics, safety protocols
- Destination guides (Moon, Mars, Asteroid Belt, Titan, Earth Orbit)
- Starship specifications
- VVIP experiences
- Launch windows and timing
- Medical requirements
- Emergency procedures

**Metadata:** category, location, importance

## Environment Configuration (.env)

```env
GENAI_API_KEY=<your-api-key>
GENAI_BASE_URL=https://genailab-maas.azure.com/v1
GENAI_LLM_MODEL=genailab-maas-gpt-4o
GENAI_EMBEDDING_MODEL=text-embedding-3-large
```

**Note:** Corporate network requires SSL verification bypass in llm_client.py

## Critical Business Rules

### 1. Space-Only Destinations (ENFORCED)
**Rule:** System ONLY allows interplanetary destinations. Earth destinations are strictly prohibited.

**Allowed Destinations:**
- Moon (Lunar Gateway Hotel, Shackleton Crater Resort)
- Mars (Starbase Alpha, Olympus Mons Base)
- Earth Orbit (ISS-2 Space Station)
- Asteroid Belt (16 Psyche Mining Station)
- Titan (Kraken Mare Floating City)

**Blocked Destinations:**
- Any Earth location (Kashmir, Kailash, Paris, London, Tokyo, New York, etc.)

**Enforcement Layers:**
1. **Knowledge Agent:** Pre-LLM query validation (scans for 25+ Earth keywords)
2. **Frontend Dropdown:** Only shows space destinations
3. **Guardrail Agent:** Post-generation verification (marks Earth destinations as critical hallucinations)

### 2. Budget Constraints
- Minimum: $1M (basic Moon trip)
- Maximum: $500M (ultimate multi-destination journey)
- Validator checks: total_cost_usd <= max_budget

### 3. Safety Requirements
- Medical clearance for all passengers
- Proper space suits and equipment
- Emergency protocols in place
- Radiation protection for Mars/Asteroid Belt

### 4. Timing Constraints
- Launch windows must align with orbital mechanics
- Minimum stay: 3 days per destination
- Maximum trip duration: 90 days (safety limit)

## Known Issues & Fixes Applied

### Issue 1: Port Conflict
**Problem:** Port 8000 already in use
**Solution:** Changed entire system to port 8080 (backend, frontend, documentation)

### Issue 2: Windows Emoji Encoding
**Problem:** Python print statements with emojis crashed on Windows
**Solution:** Removed all emoji characters from backend print statements

### Issue 3: Division by Zero in Guardrail
**Problem:** `cost_per_day = total_cost / duration` when duration = 0
**Solution:** Added check `if duration > 0` before calculation

### Issue 4: JSON Parsing Failures
**Problem:** GPT-4o sometimes returns malformed JSON or JSON in markdown blocks
**Solution:** Implemented 3-tier fallback strategy (direct parse → regex extraction → template)

### Issue 5: Earth Destination Requests
**Problem:** Users requesting Earth destinations (Kashmir, Kailash, etc.)
**Solution:** Multi-layer validation (Knowledge Agent pre-check + Guardrail Agent post-check + Frontend dropdown)

## How to Run the System

### Prerequisites
```bash
uv --version  # Package manager
python --version  # Python 3.10+
```

### Step 1: Initialize Databases
```bash
set PYTHONPATH=%CD%
uv run python backend/data/init_db.py
uv run python backend/data/init_vector_db.py
```

### Step 2: Start Backend
```bash
set PYTHONPATH=%CD%
uv run python backend/main.py
```
Expected output: "API Ready! INFO: Uvicorn running on http://0.0.0.0:8080"

### Step 3: Open Frontend
```bash
start frontend/index.html
```
Or manually open in browser

### Step 4: Test
1. Enter query: "7-day luxury Moon vacation with spacewalk"
2. Set budget: $20,000,000
3. Click "Generate Itinerary"
4. Watch agents work in real-time

## Testing Individual Components

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

## API Request/Response Examples

### Request
```json
POST http://localhost:8080/plan-travel
{
  "query": "7-day luxury Moon vacation with spacewalk experience",
  "constraints": {
    "max_budget": 20000000,
    "passengers": 2,
    "location": "Moon"
  }
}
```

### Success Response
```json
{
  "success": true,
  "itinerary": {
    "itinerary_name": "Lunar Luxury Escape",
    "duration_days": 7,
    "total_cost_usd": 18500000,
    "daily_plan": [...],
    "highlights": [...],
    "reasoning": "...",
    "confidence_score": 0.95
  },
  "validation": {
    "is_valid": true,
    "issues": [],
    "confidence_score": 0.98
  },
  "verification": {
    "is_safe": true,
    "hallucinations": [],
    "verified_entities": {...}
  }
}
```

### Error Response (Earth Destination)
```json
{
  "success": false,
  "message": "We apologize, but 'Kashmir' is not currently in our destination list. Available destinations: Moon, Mars, Earth Orbit (ISS-2), Asteroid Belt (16 Psyche), Titan (Saturn Moon)",
  "error_type": "destination_not_available"
}
```

## Future Enhancement Ideas

### 1. Additional Destinations
- Europa (Jupiter moon)
- Enceladus (Saturn moon)
- Venus Cloud Cities
- Mercury Polar Bases

### 2. Advanced Features
- Multi-passenger pricing tiers
- Group booking discounts
- Loyalty program integration
- Real-time starship availability
- Dynamic pricing based on demand

### 3. Technical Improvements
- Caching layer (Redis) for repeated queries
- Async database queries
- WebSocket for real-time agent progress updates
- User authentication and saved itineraries
- Payment gateway integration

### 4. AI Enhancements
- Fine-tuned model for space travel domain
- Multi-modal support (image generation of destinations)
- Voice interface for queries
- Sentiment analysis for personalization

## Troubleshooting Guide

### "Module not found" Error
```bash
# Solution: Set PYTHONPATH
set PYTHONPATH=%CD%
```

### "Connection refused" Error
- Verify backend is running on port 8080
- Check firewall settings
- Ensure no other service is using port 8080

### "Embedding API Error"
- Verify .env file has correct GENAI_API_KEY
- Check network connection
- Verify SSL bypass is working (corporate networks)

### "No results generated"
- Check if databases are initialized (init_db.py, init_vector_db.py)
- Verify Chroma database exists in chroma_db/ folder
- Check stellar_voyage.db file exists

### "Validation Issues" in UI
- Check budget is sufficient (minimum $1M for Moon trips)
- Verify trip duration is realistic (3-90 days)
- Ensure query is clear and specific

### "Needs Review" in UI
- Guardrail detected potential hallucinations
- Check if Earth destinations were mentioned
- Verify all entities exist in database

## Code Style & Conventions

### Python
- Type hints for all function parameters and returns
- Docstrings for all classes and functions
- Error handling with try/except blocks
- Logging for debugging (print statements without emojis on Windows)

### JavaScript
- Async/await for API calls
- Template literals for HTML generation
- Error handling with try/catch
- Responsive design principles

### Database
- Normalized schema (foreign keys for relationships)
- Indexed columns for fast queries
- Consistent naming (snake_case for columns)

## Security Considerations

### Current Implementation
- API keys stored in .env (not committed to git)
- No authentication on API endpoints (demo purposes)
- CORS enabled for localhost
- SSL verification bypassed (corporate network requirement)

### Production Recommendations
- Implement OAuth2/JWT authentication
- Rate limiting on API endpoints
- Input sanitization and validation
- HTTPS only (remove SSL bypass)
- API key rotation policy
- Database encryption at rest

## Performance Metrics

### Typical Response Times
- Knowledge retrieval: 0.5-1s
- Itinerary generation: 3-5s (GPT-4o call)
- Validation: 0.2-0.5s
- Verification: 0.3-0.7s
- **Total:** 4-7 seconds for complete itinerary

### Database Sizes
- SQLite: ~50KB (5 starships, 6 destinations, 5 launch windows)
- Chroma: ~2MB (12 documents with embeddings)

### Scalability
- Current: Single-threaded, handles 1 request at a time
- Recommended: Add async workers, connection pooling, caching

## Demo Script for Presentations

### 1. Introduction (30 seconds)
"Stellar Voyage AI is a multi-agent system for SpaceX VVIP interplanetary travel planning. It uses LangGraph to orchestrate 5 specialized AI agents that collaborate to generate validated, verified luxury space travel itineraries."

### 2. Architecture (1 minute)
"The system uses hybrid RAG - combining Chroma vector search for semantic knowledge with SQLite for structured data. The Orchestrator coordinates Knowledge, Optimizer, Validator, and Guardrail agents in a state machine workflow."

### 3. Live Demo (2 minutes)
"Let me show you: I'll request a 14-day luxury trip to Moon and Mars. Watch as the agents retrieve context, generate the itinerary, validate feasibility, and verify against hallucinations. Notice the validation badges and detailed day-by-day plan."

### 4. Guardrails (1 minute)
"A key feature is our multi-layer guardrails. The system ONLY allows space destinations. If someone requests Kashmir or Paris, it's rejected immediately. The Guardrail Agent also prevents AI hallucinations by verifying all entities against the database."

### 5. Q&A
Be ready to discuss: LangGraph state machines, RAG architecture, prompt engineering, production readiness

## Contact & Contribution

**Built for:** AI Hackathon 2026
**Demonstrates:** Multi-Agent AI, RAG, LangGraph, Production Architecture
**License:** MIT

---

**Last Updated:** 2024
**Status:** Production-ready demo system
**Next Steps:** Add authentication, caching, more destinations, real-time updates
