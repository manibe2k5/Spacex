"""
ORCHESTRATOR AGENT - Multi-Agent Coordinator (LangGraph)

WHY THIS AGENT?
- Coordinates all other agents in a workflow
- Manages state between agent calls
- Implements decision logic (when to call which agent)
- Uses LangGraph for production-grade agent orchestration

HOW IT WORKS:
1. User query → Knowledge Agent (retrieve context)
2. Context → Optimizer Agent (generate itinerary)
3. Itinerary → Validator Agent (check feasibility)
4. Itinerary → Guardrail Agent (prevent hallucinations)
5. If issues found → Loop back to Optimizer with feedback
6. If all good → Return to user

LANGGRAPH BENEFITS:
- State management (remembers conversation context)
- Conditional routing (smart decision-making)
- Error handling and retries
- Production-ready architecture
"""

from typing import TypedDict, Annotated, Dict, List
from langgraph.graph import StateGraph, END
from backend.agents.knowledge_agent import KnowledgeAgent
from backend.agents.optimizer_agent import OptimizerAgent
from backend.agents.validator_guardrail import ValidatorAgent, GuardrailAgent
from backend.agents.weather_agent import WeatherAgent
import json

# =========================
# STATE DEFINITION
# =========================
# WHY? LangGraph uses state to pass data between agents
# Like a shared whiteboard where agents write their results

class TravelPlannerState(TypedDict):
    """
    State object that flows through the agent workflow
    
    ANALOGY: Like a form that gets filled out as it passes through departments
    """
    # User input
    user_query: str
    user_constraints: Dict  # Budget, duration, preferences
    
    # Agent outputs
    retrieved_context: Dict
    weather_context: Dict
    generated_itinerary: Dict
    validation_report: Dict
    verification_report: Dict
    
    # Control flow
    iteration_count: int
    max_iterations: int
    final_response: Dict
    errors: List[str]


# =========================
# ORCHESTRATOR CLASS
# =========================
class OrchestratorAgent:
    """
    Coordinates multi-agent workflow using LangGraph
    
    ANALOGY: Like a project manager coordinating a team
    """
    
    def __init__(self):
        """Initialize all agents and build workflow graph"""
        
        print("Initializing Orchestrator Agent...")
        
        # Initialize all sub-agents
        self.knowledge_agent = KnowledgeAgent()
        self.weather_agent = WeatherAgent()
        self.optimizer_agent = OptimizerAgent()
        self.validator_agent = ValidatorAgent()
        self.guardrail_agent = GuardrailAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
        print("Orchestrator Agent ready!")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the agent workflow using LangGraph
        
        WHY LANGGRAPH?
        - Handles complex multi-agent coordination
        - Built-in state management
        - Conditional routing (if/else logic)
        - Industry standard for production AI systems
        """
        
        # Create workflow graph
        workflow = StateGraph(TravelPlannerState)
        
        # =========================
        # ADD NODES (Agent Functions)
        # =========================
        # Each node is a step in the workflow
        
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge_node)
        workflow.add_node("fetch_weather", self._fetch_weather_node)
        workflow.add_node("generate_itinerary", self._generate_itinerary_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("verify_guardrails", self._verify_guardrails_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # =========================
        # ADD EDGES (Workflow Flow)
        # =========================
        # Defines the order of execution
        
        # Start → Retrieve Knowledge
        workflow.set_entry_point("retrieve_knowledge")
        
        # Retrieve → Fetch Weather
        workflow.add_edge("retrieve_knowledge", "fetch_weather")
        
        # Fetch Weather → Generate
        workflow.add_edge("fetch_weather", "generate_itinerary")
        
        # Generate → Validate
        workflow.add_edge("generate_itinerary", "validate")
        
        # Validate → Verify Guardrails
        workflow.add_edge("validate", "verify_guardrails")
        
        # Verify → Conditional routing
        # WHY CONDITIONAL? If issues found, we might need to regenerate
        workflow.add_conditional_edges(
            "verify_guardrails",
            self._should_regenerate,  # Decision function
            {
                "regenerate": "generate_itinerary",  # Loop back if issues
                "finalize": "finalize"  # Proceed if all good
            }
        )
        
        # Finalize → End
        workflow.add_edge("finalize", END)
        
        # Compile the workflow
        return workflow.compile()
    
    # =========================
    # NODE FUNCTIONS
    # =========================
    # Each function represents one step in the workflow
    
    def _retrieve_knowledge_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 1: Retrieve relevant knowledge
        
        WHY FIRST? Need context before generating itinerary
        """
        print("\n[ORCHESTRATOR] Step 1: Retrieving knowledge...")
        
        try:
            # Extract filters from user constraints
            filters = {}
            if "location" in state.get("user_constraints", {}):
                filters["location"] = state["user_constraints"]["location"]
            if "max_budget" in state.get("user_constraints", {}):
                filters["max_price"] = state["user_constraints"]["max_budget"] / 10  # Per night estimate
            
            # Call Knowledge Agent
            context = self.knowledge_agent.retrieve(
                query=state["user_query"],
                filters=filters
            )
            
            # Check if destination validation failed
            if context.get("error") == "destination_not_available":
                # Store error in state and skip to finalize
                state["errors"].append(context.get("message"))
                state["final_response"] = {
                    "success": False,
                    "error": "destination_not_available",
                    "message": context.get("message"),
                    "available_destinations": context.get("available_destinations", []),
                    "suggestion": context.get("suggestion", "")
                }
                # Mark as complete to skip other agents
                state["skip_processing"] = True
            else:
                state["retrieved_context"] = context
            
        except Exception as e:
            state["errors"].append(f"Knowledge retrieval error: {str(e)}")
        
        return state
    
    def _fetch_weather_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 2: Fetch live space weather conditions
        
        WHY? Adds real-time NASA/NOAA data so the itinerary reflects
        actual planetary conditions at booking time.
        """
        print("\n[ORCHESTRATOR] Step 2: Fetching live space weather...")
        
        # Skip if destination validation failed
        if state.get("skip_processing"):
            print("  Skipping - destination validation failed")
            return state
        
        try:
            weather_context = self.weather_agent.get_weather_context(
                user_query=state["user_query"],
                user_constraints=state.get("user_constraints", {})
            )
            state["weather_context"] = weather_context
        except Exception as e:
            print(f"  Weather fetch failed (non-critical): {str(e)}")
            state["weather_context"] = {"error": str(e), "safety_alerts": [], "destinations": {}, "space_weather": {}}
        
        return state
    
    def _generate_itinerary_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 3: Generate itinerary using LLM
        
        WHY? This is where AI creativity happens
        """
        print("\n[ORCHESTRATOR] Step 3: Generating itinerary...")
        
        # Skip if destination validation failed
        if state.get("skip_processing"):
            print("  Skipping - destination validation failed")
            return state
        
        try:
            # Call Optimizer Agent
            itinerary = self.optimizer_agent.generate_itinerary(
                user_query=state["user_query"],
                context=state["retrieved_context"],
                weather_context=state.get("weather_context", {})
            )
            
            state["generated_itinerary"] = itinerary
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            
        except Exception as e:
            state["errors"].append(f"Itinerary generation error: {str(e)}")
        
        return state
    
    def _validate_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 4: Validate itinerary feasibility
        
        WHY? Catch timing conflicts, budget issues, weather safety concerns etc.
        """
        print("\n[ORCHESTRATOR] Step 4: Validating itinerary...")
        
        try:
            # Call Validator Agent
            validation_report = self.validator_agent.validate(
                itinerary=state["generated_itinerary"],
                user_constraints=state.get("user_constraints", {}),
                weather_context=state.get("weather_context", {})
            )
            
            state["validation_report"] = validation_report
            
        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
        
        return state
    
    def _verify_guardrails_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 5: Verify against hallucinations
        
        WHY? Ensure all recommendations are real and available
        """
        print("\n[ORCHESTRATOR] Step 4: Verifying guardrails...")
        
        try:
            # Call Guardrail Agent
            verification_report = self.guardrail_agent.verify(
                itinerary=state["generated_itinerary"]
            )
            
            state["verification_report"] = verification_report
            
        except Exception as e:
            state["errors"].append(f"Verification error: {str(e)}")
        
        return state
    
    def _finalize_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Node 6: Finalize and prepare response
        
        WHY? Package everything nicely for the user
        """
        print("\n[ORCHESTRATOR] Step 5: Finalizing response...")
        
        # Check if we already have a final response (from validation error)
        if state.get("final_response"):
            print("  Using pre-set final response (validation error)")
            return state
        
        # Compile final response
        final_response = {
            "itinerary": state["generated_itinerary"],
            "validation": state["validation_report"],
            "verification": state["verification_report"],
            "weather": state.get("weather_context", {}),
            "metadata": {
                "iterations": state.get("iteration_count", 1),
                "errors": state.get("errors", [])
            }
        }
        
        state["final_response"] = final_response
        
        print("\n[ORCHESTRATOR] Workflow complete!")
        
        return state
    
    # =========================
    # CONDITIONAL ROUTING
    # =========================
    
    def _should_regenerate(self, state: TravelPlannerState) -> str:
        """
        Decide whether to regenerate itinerary or finalize
        
        WHY? If critical issues found, we should try again
        
        Returns:
            "regenerate" or "finalize"
        """
        
        # Check if destination validation failed - skip to finalize with error
        if state.get("skip_processing"):
            print("  Destination validation failed. Finalizing with error...")
            return "finalize"
        
        # Check iteration limit
        if state.get("iteration_count", 0) >= state.get("max_iterations", 2):
            print("  Max iterations reached. Finalizing...")
            return "finalize"
        
        # Check for critical issues
        validation = state.get("validation_report", {})
        verification = state.get("verification_report", {})
        
        # Check for critical hallucinations (Earth destinations)
        critical_hallucinations = [
            h for h in verification.get("hallucinations", [])
            if h.get("severity") == "critical"
        ]
        
        if critical_hallucinations:
            print(f"  Critical hallucinations detected: {len(critical_hallucinations)}")
            # Don't regenerate for Earth destinations - it's a fundamental error
            if any(h.get("type") == "invalid_destination" for h in critical_hallucinations):
                print("  Invalid Earth destination detected. Cannot regenerate.")
                # Set error in state
                state["final_response"] = {
                    "success": False,
                    "error": "invalid_destination",
                    "message": "The requested destination is not available in our interplanetary travel system.",
                    "suggestion": "Stellar Voyage AI specializes in space travel. Please choose from: Moon, Mars, Earth Orbit (ISS-2), Asteroid Belt (16 Psyche), or Titan (Saturn Moon).",
                    "itinerary": {},
                    "validation": validation,
                    "verification": verification
                }
                return "finalize"
        
        has_critical_issues = (
            not validation.get("is_valid", True) or
            not verification.get("is_safe", True)
        )
        
        if has_critical_issues:
            print("  Critical issues detected. Regenerating...")
            return "regenerate"
        else:
            print("  All checks passed. Finalizing...")
            return "finalize"
    
    # =========================
    # PUBLIC INTERFACE
    # =========================
    
    def plan_travel(self, user_query: str, user_constraints: Dict = None) -> Dict:
        """
        Main entry point: Plan travel based on user query
        
        Args:
            user_query: User's travel request
            user_constraints: Budget, duration, preferences
            
        Returns:
            Complete travel plan with itinerary and validation
            
        EXAMPLE:
        result = orchestrator.plan_travel(
            user_query="14-day luxury trip to Moon and Mars",
            user_constraints={"max_budget": 150000000, "passengers": 2}
        )
        """
        
        print(f"\n{'='*60}")
        print(f"STELLAR VOYAGE AI - Planning Your Journey")
        print(f"{'='*60}")
        print(f"Query: {user_query}")
        print(f"Constraints: {user_constraints}")
        print(f"{'='*60}\n")
        
        # Initialize state
        initial_state = TravelPlannerState(
            user_query=user_query,
            user_constraints=user_constraints or {},
            retrieved_context={},
            weather_context={},
            generated_itinerary={},
            validation_report={},
            verification_report={},
            iteration_count=0,
            max_iterations=2,
            final_response={},
            errors=[]
        )
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state["final_response"]


# =========================
# TEST THE ORCHESTRATOR
# =========================
if __name__ == "__main__":
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Test query
    result = orchestrator.plan_travel(
        user_query="Plan a 10-day luxury trip to the Moon with spacewalk experience and stay at the best resort",
        user_constraints={
            "max_budget": 25000000,
            "passengers": 2,
            "location": "Moon"
        }
    )
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
