"""
FASTAPI BACKEND - REST API Server

WHY FASTAPI?
- Modern, fast Python web framework
- Automatic API documentation (Swagger UI)
- Async support for better performance
- Type validation with Pydantic
- Industry standard for AI/ML APIs

WHAT IT DOES:
- Exposes /plan-travel endpoint for frontend
- Handles CORS (allows React frontend to connect)
- Validates request/response data
- Calls Orchestrator Agent
- Returns JSON responses
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import uvicorn
from backend.agents.orchestrator import OrchestratorAgent

# =========================
# FASTAPI APP INITIALIZATION
# =========================
app = FastAPI(
    title="Stellar Voyage AI API",
    description="Interplanetary Travel Planning System for SpaceX VVIPs",
    version="1.0.0"
)

# =========================
# CORS MIDDLEWARE
# =========================
# WHY? Allows React frontend (running on different port) to call this API
# Without CORS, browser blocks cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# INITIALIZE ORCHESTRATOR
# =========================
# Create once at startup (expensive initialization)
print("Initializing Stellar Voyage AI...")
orchestrator = OrchestratorAgent()
print("API Ready!")

# =========================
# REQUEST/RESPONSE MODELS
# =========================
# WHY PYDANTIC? Type validation, automatic documentation, data validation

class TravelRequest(BaseModel):
    """
    Request model for travel planning
    
    EXAMPLE:
    {
        "query": "14-day luxury trip to Moon and Mars",
        "constraints": {
            "max_budget": 150000000,
            "passengers": 2,
            "location": "Moon"
        }
    }
    """
    query: str = Field(..., description="User's travel request in natural language")
    constraints: Optional[Dict] = Field(
        default={},
        description="Optional constraints (max_budget, passengers, location, etc.)"
    )

class TravelResponse(BaseModel):
    """
    Response model for travel planning
    
    Contains:
    - Generated itinerary
    - Validation report
    - Verification report
    - Metadata
    """
    success: bool
    itinerary: Dict
    validation: Dict
    verification: Dict
    weather: Optional[Dict] = None
    metadata: Dict
    message: Optional[str] = None

# =========================
# API ENDPOINTS
# =========================

@app.get("/")
async def root():
    """
    Health check endpoint
    
    WHY? Verify API is running
    """
    return {
        "service": "Stellar Voyage AI",
        "status": "operational",
        "version": "1.0.0",
        "message": "Welcome to the future of interplanetary travel!"
    }

@app.post("/plan-travel", response_model=TravelResponse)
async def plan_travel(request: TravelRequest):
    """
    Main endpoint: Plan interplanetary travel
    
    WHY POST? Sending data (user query + constraints)
    
    Args:
        request: TravelRequest with query and constraints
        
    Returns:
        TravelResponse with complete travel plan
        
    EXAMPLE REQUEST:
    POST /plan-travel
    {
        "query": "7-day Moon vacation with spacewalk",
        "constraints": {"max_budget": 20000000}
    }
    
    EXAMPLE RESPONSE:
    {
        "success": true,
        "itinerary": {...},
        "validation": {...},
        "verification": {...}
    }
    """
    
    try:
        print(f"\n[API] Received request: {request.query}")
        
        # Call orchestrator to plan travel
        result = orchestrator.plan_travel(
            user_query=request.query,
            user_constraints=request.constraints
        )
        
        # Check for errors
        if result.get("metadata", {}).get("errors"):
            errors = result["metadata"]["errors"]
            # Check if it's a destination validation error
            if result.get("error") == "destination_not_available":
                return TravelResponse(
                    success=False,
                    itinerary={},
                    validation={},
                    verification={},
                    weather=result.get("weather", {}),
                    metadata=result.get("metadata", {}),
                    message=result.get("message", "") + "\n\n" + result.get("suggestion", "")
                )
            else:
                return TravelResponse(
                    success=False,
                    itinerary={},
                    validation={},
                    verification={},
                    weather=result.get("weather", {}),
                    metadata=result.get("metadata", {}),
                    message=f"Errors occurred: {errors}"
                )
        
        # Return successful response
        return TravelResponse(
            success=True,
            itinerary=result.get("itinerary", {}),
            validation=result.get("validation", {}),
            verification=result.get("verification", {}),
            weather=result.get("weather", {}),
            metadata=result.get("metadata", {}),
            message="Travel plan generated successfully!"
        )
        
    except Exception as e:
        print(f"[API] Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/destinations")
async def get_destinations():
    """
    Get list of available destinations
    
    WHY? Frontend can show dropdown of destinations
    """
    import sqlite3
    from backend.config import SQLITE_DB_PATH
    
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM destinations ORDER BY celestial_body, name")
        rows = cursor.fetchall()
        
        destinations = [dict(row) for row in rows]
        conn.close()
        
        return {
            "success": True,
            "count": len(destinations),
            "destinations": destinations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/starships")
async def get_starships():
    """
    Get list of available starships
    
    WHY? Frontend can show spacecraft options
    """
    import sqlite3
    from backend.config import SQLITE_DB_PATH
    
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM starships ORDER BY luxury_rating DESC, name")
        rows = cursor.fetchall()
        
        starships = [dict(row) for row in rows]
        conn.close()
        
        return {
            "success": True,
            "count": len(starships),
            "starships": starships
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    """
    Start the API server
    
    WHY UVICORN? ASGI server for FastAPI (async support)
    
    Access:
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs (automatic Swagger UI!)
    """
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all network interfaces
        port=8080,
        log_level="info"
    )
