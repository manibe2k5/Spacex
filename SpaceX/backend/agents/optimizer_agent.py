"""
OPTIMIZER AGENT - Itinerary Generator

WHY THIS AGENT?
- Takes user requirements + retrieved context
- Uses LLM (GPT-4o) to generate optimal travel itineraries
- Considers costs, timing, preferences, and constraints

HOW IT WORKS:
1. Receives user query + context from Knowledge Agent
2. Constructs detailed prompt for LLM
3. LLM generates creative, optimized itinerary
4. Returns structured itinerary with reasoning
"""

from typing import Dict, List
from backend.utils.llm_client import llm
import json

class OptimizerAgent:
    """
    Generates optimal travel itineraries using AI
    
    ANALOGY: Like a travel agent who designs custom trips
    """
    
    def __init__(self):
        self.llm = llm
        print("Optimizer Agent initialized!")
    
    def generate_itinerary(self, user_query: str, context: Dict, weather_context: Dict = None) -> Dict:
        """
        Generate an optimized travel itinerary
        
        Args:
            user_query: User's travel request
            context: Retrieved information from Knowledge Agent
            weather_context: Live space weather from WeatherAgent (optional)
            
        Returns:
            Structured itinerary with day-by-day plan
            
        EXAMPLE:
        Input: "14-day trip to Moon and Mars"
        Output: {
            "itinerary": {
                "day_1": {...},
                "day_2": {...}
            },
            "total_cost": "$125M",
            "reasoning": "..."
        }
        """
        
        print(f"\nOptimizer Agent: Generating itinerary for '{user_query}'")
        
        # =========================
        # STEP 1: BUILD CONTEXT STRING
        # =========================
        # Combine all retrieved information into readable format
        context_str = self._format_context(context)
        
        # =========================
        # STEP 2: CONSTRUCT PROMPT
        # =========================
        # This is the "instruction manual" for the LLM
        # WHY DETAILED? Better prompts = better results
        weather_str = self._format_weather_context(weather_context or {})
        prompt = f"""
You are an elite interplanetary travel concierge for SpaceX VVIPs.
Your clients are ultra-wealthy individuals seeking extraordinary space travel experiences.

USER REQUEST:
{user_query}

AVAILABLE INFORMATION:
{context_str}
{weather_str}

YOUR TASK:
Generate an optimized, luxurious travel itinerary that:
1. Meets the user's requirements
2. Maximizes unique experiences
3. Ensures safety and comfort — USE THE LIVE WEATHER DATA above to flag unsafe EVA days or storm risks
4. Considers planetary alignments and launch windows
5. Provides day-by-day breakdown
6. Includes cost estimates
7. Explains your reasoning
8. Incorporates current space weather into activity notes (e.g. "Spacewalk safe — nominal solar wind")

IMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no explanations, just pure JSON.

RESPONSE FORMAT (VALID JSON ONLY):
{{
    "itinerary_name": "Creative name for the journey",
    "duration_days": 7,
    "total_cost_usd": 15000000,
    "confidence_score": 0.92,
    "summary": "Brief overview of the journey",
    "daily_plan": [
        {{
            "day": 1,
            "date": "2026-06-15",
            "title": "Departure to Moon",
            "activities": [
                {{
                    "time": "08:00",
                    "activity": "Board Olympus Cruiser at SpaceX Starbase",
                    "location": "Earth - SpaceX Starbase Texas",
                    "duration": "2 hours",
                    "cost_usd": 5000000,
                    "type": "flight"
                }}
            ],
            "accommodation": "In transit aboard Olympus Cruiser",
            "notes": "Launch window optimal for 3-day transit"
        }}
    ],
    "spacecraft_used": ["Olympus Cruiser"],
    "destinations_visited": ["Moon", "Lunar Gateway Hotel"],
    "highlights": [
        "Private spacewalk with professional astronaut guide",
        "Earth-rise viewing from lunar orbit",
        "Exclusive crater exploration"
    ],
    "requirements": [
        "Medical clearance required",
        "2-week pre-flight training",
        "Radiation exposure waiver"
    ],
    "reasoning": "This itinerary optimizes for luxury and safety while staying within budget. The Olympus Cruiser provides maximum comfort for the 3-day transit.",
    "alternatives": "Could extend to 10 days for surface exploration or reduce to 5 days for orbit-only experience."
}}

Remember: Respond with ONLY the JSON object. No markdown code blocks, no explanations before or after.
"""
        
        # =========================
        # STEP 3: CALL LLM
        # =========================
        print("  Calling LLM to generate itinerary...")
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content
            
            # Try to parse JSON response
            # LLMs sometimes add markdown formatting, so we clean it
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse as JSON
            try:
                itinerary = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                # Try to find JSON object in the response
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        itinerary = json.loads(json_match.group())
                    except:
                        # Last resort: try to find the outermost braces
                        start = response_text.find('{')
                        end = response_text.rfind('}')
                        if start != -1 and end != -1:
                            itinerary = json.loads(response_text[start:end+1])
                        else:
                            raise ValueError("Could not extract valid JSON from response")
                else:
                    raise ValueError("Could not find JSON object in response")
            
            print(f"  Generated itinerary: {itinerary.get('itinerary_name', 'Unnamed')}")
            print(f"  Duration: {itinerary.get('duration_days', 0)} days")
            print(f"  Estimated cost: ${itinerary.get('total_cost_usd', 0):,.0f}")
            
            return itinerary
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Warning: Could not parse JSON response: {str(e)}")
            print(f"  Raw response preview: {response_text[:300]}...")
            
            # Create a basic fallback itinerary from the text response
            return {
                "itinerary_name": "AI-Generated Journey",
                "duration_days": 7,
                "total_cost_usd": 20000000,
                "confidence_score": 0.7,
                "summary": "The AI generated a detailed response but it could not be parsed into structured format. The system has created a basic itinerary template. Please try your query again for a fully structured response.",
                "daily_plan": [
                    {
                        "day": 1,
                        "title": "Journey Begins",
                        "activities": [
                            {
                                "time": "09:00",
                                "activity": "Departure and transit",
                                "location": "As per your requirements",
                                "duration": "Variable",
                                "cost_usd": 5000000,
                                "type": "flight"
                            }
                        ],
                        "accommodation": "Luxury spacecraft or destination resort",
                        "notes": "AI response could not be fully parsed - please regenerate"
                    }
                ],
                "spacecraft_used": ["Luxury Starship"],
                "destinations_visited": ["As requested"],
                "highlights": [
                    "Exclusive VVIP experiences",
                    "Luxury accommodations",
                    "Professional guidance throughout"
                ],
                "requirements": [
                    "Medical clearance",
                    "Pre-flight training",
                    "Safety briefing"
                ],
                "reasoning": "This is a fallback response. The AI generated content but it was not in the expected JSON format. Please try regenerating for a complete itinerary.",
                "alternatives": "Try rephrasing your query or adjusting the budget/duration.",
                "error_info": {
                    "error": "JSON parsing failed",
                    "preview": response_text[:500]
                }
            }
        except Exception as e:
            print(f"  Error generating itinerary: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "itinerary_name": "Generation Failed",
                "duration_days": 0,
                "total_cost_usd": 0,
                "confidence_score": 0,
                "summary": f"An error occurred: {str(e)}",
                "daily_plan": [],
                "error": str(e)
            }
    
    def _format_weather_context(self, weather_context: Dict) -> str:
        """
        Format live weather data into a readable section for the LLM prompt.
        """
        if not weather_context or weather_context.get("error"):
            return ""
        
        lines = ["\n\n=== LIVE SPACE WEATHER CONDITIONS ==="]
        
        # Global space weather
        sw = weather_context.get("space_weather", {})
        if sw:
            lines.append(f"\nGlobal Space Weather (source: {sw.get('source', 'NOAA/NASA')})")
            lines.append(f"  Kp-index         : {sw.get('kp_index', 'N/A')} ({sw.get('radiation_belt_status', 'normal')})")
            lines.append(f"  Geomagnetic storm: {'YES - caution' if sw.get('geomagnetic_storm_active') else 'No'}")
            flares = sw.get("solar_flares_today", [])
            if flares:
                lines.append(f"  Solar flares today: {', '.join(f['class'] for f in flares)}")
            else:
                lines.append("  Solar flares today: None")
        
        # Per-destination conditions
        destinations = weather_context.get("destinations", {})
        for dest_name, conditions in destinations.items():
            lines.append(f"\n{dest_name} Conditions (source: {conditions.get('source', 'N/A')})")
            if "temperature_min_celsius" in conditions:
                lines.append(f"  Temperature : {conditions['temperature_min_celsius']}°C to {conditions['temperature_max_celsius']}°C")
            if "temperature_celsius" in conditions:
                lines.append(f"  Temperature : {conditions['temperature_celsius']}°C")
            if "pressure_pa" in conditions:
                lines.append(f"  Pressure    : {conditions['pressure_pa']} Pa")
            if "solar_wind_speed_km_s" in conditions:
                lines.append(f"  Solar wind  : {conditions['solar_wind_speed_km_s']} km/s")
            if "radiation_level" in conditions:
                lines.append(f"  Radiation   : {conditions['radiation_level']}")
            if "storm_risk" in conditions:
                lines.append(f"  Storm risk  : {conditions['storm_risk']}")
            eva_safe = conditions.get("safe_for_eva", True)
            lines.append(f"  EVA safe    : {'YES' if eva_safe else 'NO - do not schedule EVA'}")
            if conditions.get("eva_recommendation"):
                lines.append(f"  EVA note    : {conditions['eva_recommendation']}")
        
        # Safety alerts
        alerts = weather_context.get("safety_alerts", [])
        if alerts:
            lines.append("\nACTIVE SAFETY ALERTS:")
            for alert in alerts:
                lines.append(f"  ! {alert}")
        
        return "\n".join(lines)
    
    def _format_context(self, context: Dict) -> str:
        """
        Format retrieved context into readable string for LLM
        
        WHY? LLMs work better with well-structured text input
        """
        
        formatted = []
        
        # Add vector search results (unstructured knowledge)
        if context.get("vector_results"):
            formatted.append("=== RELEVANT KNOWLEDGE ===")
            for i, doc in enumerate(context["vector_results"][:3], 1):  # Top 3 most relevant
                formatted.append(f"\n[Document {i}] (Relevance: {doc.get('relevance_score', 0):.2f})")
                formatted.append(doc["text"])
        
        # Add structured data
        structured = context.get("structured_data", {})
        
        if structured.get("destinations"):
            formatted.append("\n\n=== AVAILABLE DESTINATIONS ===")
            for dest in structured["destinations"][:5]:  # Top 5
                formatted.append(f"\n- {dest['name']} ({dest['celestial_body']})")
                formatted.append(f"  Cost: ${dest['cost_per_night']:,.0f}/night")
                formatted.append(f"  Luxury Rating: {dest['luxury_rating']}/5")
                formatted.append(f"  Activities: {dest['activities']}")
        
        if structured.get("starships"):
            formatted.append("\n\n=== AVAILABLE STARSHIPS ===")
            for ship in structured["starships"][:5]:
                formatted.append(f"\n- {ship['name']} ({ship['type']})")
                formatted.append(f"  Capacity: {ship['capacity']} passengers")
                formatted.append(f"  Cost: ${ship['cost_per_day']:,.0f}/day")
                formatted.append(f"  Amenities: {ship['amenities']}")
                formatted.append(f"  Available: {ship['next_available']}")
        
        if structured.get("launch_windows"):
            formatted.append("\n\n=== LAUNCH WINDOWS ===")
            for window in structured["launch_windows"]:
                formatted.append(f"\n- {window['origin']} → {window['destination']}")
                formatted.append(f"  Opens: {window['opens_date']}")
                formatted.append(f"  Duration: {window['travel_duration_days']} days")
                formatted.append(f"  Efficiency: {window['fuel_efficiency_score']:.0%}")
        
        return "\n".join(formatted)

# Test the agent
if __name__ == "__main__":
    from backend.agents.knowledge_agent import KnowledgeAgent
    
    # Initialize agents
    knowledge_agent = KnowledgeAgent()
    optimizer_agent = OptimizerAgent()
    
    # Test query
    user_query = "Plan a 7-day luxury trip to the Moon with spacewalk experience"
    
    # Step 1: Retrieve context
    context = knowledge_agent.retrieve(
        query=user_query,
        filters={"location": "Moon", "min_luxury_rating": 5}
    )
    
    # Step 2: Generate itinerary
    itinerary = optimizer_agent.generate_itinerary(user_query, context)
    
    print("\n=== GENERATED ITINERARY ===")
    print(json.dumps(itinerary, indent=2))
