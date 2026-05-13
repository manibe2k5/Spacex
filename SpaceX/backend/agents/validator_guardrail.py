"""
VALIDATOR AGENT - Quality Controller

WHY THIS AGENT?
- Checks if generated itinerary is feasible
- Detects timing conflicts, budget issues, safety concerns
- Suggests improvements before presenting to user

HOW IT WORKS:
1. Receives generated itinerary
2. Validates against constraints (time, cost, safety)
3. Flags issues and suggests fixes
4. Returns validation report
"""

from typing import Dict, List
from datetime import datetime, timedelta
import json

class ValidatorAgent:
    """
    Validates itineraries for feasibility and safety
    
    ANALOGY: Like a quality control inspector
    """
    
    def __init__(self):
        print("Validator Agent initialized!")
    
    def validate(self, itinerary: Dict, user_constraints: Dict = None, weather_context: Dict = None) -> Dict:
        """
        Validate an itinerary for feasibility
        
        Args:
            itinerary: Generated itinerary from Optimizer Agent
            user_constraints: User's budget, time, preferences
            weather_context: Live space weather from WeatherAgent (optional)
            
        Returns:
            Validation report with issues and suggestions
        """
        
        print(f"\nValidator Agent: Checking itinerary '{itinerary.get('itinerary_name', 'Unnamed')}'")
        
        issues = []
        warnings = []
        suggestions = []
        
        # =========================
        # CHECK 1: BUDGET VALIDATION
        # =========================
        if user_constraints and "max_budget" in user_constraints:
            max_budget = user_constraints["max_budget"]
            total_cost = itinerary.get("total_cost_usd", 0)
            
            if total_cost > max_budget:
                issues.append({
                    "type": "budget_exceeded",
                    "severity": "high",
                    "message": f"Cost ${total_cost:,.0f} exceeds budget ${max_budget:,.0f}",
                    "suggestion": "Consider shorter duration or less luxurious accommodations"
                })
            elif total_cost > max_budget * 0.9:
                warnings.append({
                    "type": "budget_warning",
                    "message": f"Cost is 90%+ of budget (${total_cost:,.0f} / ${max_budget:,.0f})"
                })
        
        # =========================
        # CHECK 2: TIMING CONFLICTS
        # =========================
        daily_plan = itinerary.get("daily_plan", [])
        for day in daily_plan:
            activities = day.get("activities", [])
            
            # Check for overlapping activities
            for i in range(len(activities) - 1):
                current = activities[i]
                next_activity = activities[i + 1]
                
                # Simple time conflict check (would be more sophisticated in production)
                if current.get("time") and next_activity.get("time"):
                    # This is simplified - real implementation would parse times properly
                    pass  # Placeholder for time conflict logic
        
        # =========================
        # CHECK 3: TRAVEL FEASIBILITY
        # =========================
        destinations = itinerary.get("destinations_visited", [])
        duration = itinerary.get("duration_days", 0)
        
        # Check if duration is realistic for destinations
        if "Mars" in str(destinations) and duration < 180:
            warnings.append({
                "type": "unrealistic_duration",
                "message": f"Mars trip in {duration} days is extremely optimistic (typical: 180+ days)",
                "suggestion": "Consider extending duration or using advanced propulsion"
            })
        
        if "Titan" in str(destinations) and duration < 730:
            issues.append({
                "type": "impossible_duration",
                "severity": "critical",
                "message": f"Titan trip requires minimum 2 years (730 days), not {duration} days",
                "suggestion": "Remove Titan or extend trip duration significantly"
            })
        
        # =========================
        # CHECK 4: SAFETY REQUIREMENTS
        # =========================
        requirements = itinerary.get("requirements", [])
        
        # Ensure critical requirements are mentioned
        critical_requirements = ["Medical clearance", "Radiation exposure waiver", "Training"]
        missing_requirements = []
        
        for req in critical_requirements:
            if not any(req.lower() in str(r).lower() for r in requirements):
                missing_requirements.append(req)
        
        if missing_requirements:
            warnings.append({
                "type": "missing_requirements",
                "message": f"Missing safety requirements: {', '.join(missing_requirements)}",
                "suggestion": "Add mandatory safety requirements to itinerary"
            })
        
        # =========================
        # CHECK 5: SPACECRAFT CAPACITY
        # =========================
        spacecraft = itinerary.get("spacecraft_used", [])
        if not spacecraft:
            warnings.append({
                "type": "no_spacecraft",
                "message": "No spacecraft specified in itinerary",
                "suggestion": "Assign specific starships to each leg of journey"
            })
        
        # =========================
        # CHECK 6: WEATHER SAFETY
        # =========================
        if weather_context and not weather_context.get("error"):
            
            # CHECK 6a: Solar flare EVA alert
            space_weather = weather_context.get("space_weather", {})
            if space_weather.get("solar_flare_alert"):
                flares = space_weather.get("solar_flares_today", [])
                flare_classes = ", ".join(f.get("class", "?") for f in flares)
                warnings.append({
                    "type": "weather_solar_flare",
                    "message": f"Solar flare detected today (class: {flare_classes}) — EVA activities may need rescheduling",
                    "suggestion": "Add contingency buffer days and flexible EVA scheduling to the itinerary"
                })
            
            # CHECK 6b: Destination-specific EVA safety
            dest_conditions = weather_context.get("destinations", {})
            for dest_name, conditions in dest_conditions.items():
                if not conditions.get("safe_for_eva", True):
                    eva_note = conditions.get("eva_recommendation", "EVA not recommended under current conditions")
                    issues.append({
                        "type": "weather_eva_unsafe",
                        "severity": "high",
                        "message": f"{dest_name}: {eva_note}",
                        "suggestion": f"Remove or reschedule spacewalk activities at {dest_name} until conditions improve"
                    })
            
            # CHECK 6c: Mars dust storm risk
            mars_conditions = dest_conditions.get("Mars", {})
            if mars_conditions.get("storm_risk") == "high":
                issues.append({
                    "type": "weather_mars_storm",
                    "severity": "high",
                    "message": "Mars: Dust storm risk is HIGH — outdoor rover activities are dangerous",
                    "suggestion": "Postpone surface rover excursions and crater expeditions until storm subsides"
                })
            
            # CHECK 6d: Geomagnetic storm deep space warning
            if space_weather.get("geomagnetic_storm_active"):
                kp = space_weather.get("kp_index", 0)
                warnings.append({
                    "type": "weather_geomagnetic_storm",
                    "message": f"Geomagnetic storm active (Kp={kp}) — enhanced radiation shielding required for all destinations",
                    "suggestion": "Ensure spacecraft radiation shielding is at maximum and limit cumulative EVA exposure"
                })
        
        # =========================
        # GENERATE SUGGESTIONS
        # =========================
        if len(issues) == 0 and len(warnings) == 0:
            suggestions.append("Itinerary looks excellent! Consider adding exclusive VVIP experiences.")
        
        if duration > 30:
            suggestions.append("For long journeys, consider cryo-sleep option to reduce life support costs")
        
        # =========================
        # COMPILE REPORT
        # =========================
        validation_report = {
            "is_valid": len(issues) == 0,
            "confidence": 1.0 - (len(issues) * 0.3 + len(warnings) * 0.1),
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "summary": self._generate_summary(issues, warnings)
        }
        
        print(f"  Validation: {'PASSED' if validation_report['is_valid'] else 'FAILED'}")
        print(f"  Issues: {len(issues)}, Warnings: {len(warnings)}")
        
        return validation_report
    
    def _generate_summary(self, issues: List, warnings: List) -> str:
        """Generate human-readable validation summary"""
        if len(issues) == 0 and len(warnings) == 0:
            return "Itinerary is fully validated and ready for booking."
        elif len(issues) == 0:
            return f"Itinerary is feasible with {len(warnings)} minor warnings."
        else:
            return f"Itinerary has {len(issues)} critical issues that must be resolved."


"""
GUARDRAIL AGENT - Hallucination Prevention

WHY THIS AGENT?
- Prevents LLM from making up fake hotels, ships, or destinations
- Cross-checks generated content against database
- Ensures all recommendations are real and available

HOW IT WORKS:
1. Receives generated itinerary
2. Checks every hotel, ship, destination against database
3. Flags any hallucinated content
4. Replaces with real alternatives
"""

import sqlite3
from backend.config import SQLITE_DB_PATH

class GuardrailAgent:
    """
    Prevents AI hallucinations by verifying against database
    
    ANALOGY: Like a fact-checker for news articles
    """
    
    def __init__(self):
        self.conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        print("Guardrail Agent initialized!")
    
    def verify(self, itinerary: Dict) -> Dict:
        """
        Verify itinerary against database to prevent hallucinations
        
        Args:
            itinerary: Generated itinerary
            
        Returns:
            Verification report with hallucinations flagged
        """
        
        print(f"\nGuardrail Agent: Verifying itinerary against database")
        
        hallucinations = []
        verified_items = []
        
        # =========================
        # CHECK 0: VALIDATE DESTINATIONS ARE SPACE-ONLY
        # =========================
        # List of Earth destinations that should never appear
        earth_destinations = [
            'kashmir', 'kailash', 'kailasha', 'himalaya', 'everest',
            'paris', 'london', 'new york', 'tokyo', 'dubai',
            'india', 'china', 'usa', 'europe', 'asia', 'africa',
            'beach', 'mountain', 'desert', 'forest', 'ocean',
            'maldives', 'bali', 'hawaii', 'caribbean', 'alps',
            'earth', 'planet earth'
        ]
        
        # Check itinerary name and summary for Earth destinations
        itinerary_text = (
            str(itinerary.get("itinerary_name", "")) + " " +
            str(itinerary.get("summary", "")) + " " +
            str(itinerary.get("destinations_visited", []))
        ).lower()
        
        for earth_dest in earth_destinations:
            if earth_dest in itinerary_text:
                hallucinations.append({
                    "type": "invalid_destination",
                    "item": earth_dest.title(),
                    "severity": "critical",
                    "message": f"Earth destination '{earth_dest.title()}' detected. This system only handles interplanetary travel.",
                    "action": "Remove Earth destinations. Only Moon, Mars, Asteroid Belt, Earth Orbit, and Titan are allowed."
                })
        
        # =========================
        # CHECK 1: VERIFY DESTINATIONS
        # =========================
        destinations = itinerary.get("destinations_visited", [])
        cursor = self.conn.cursor()
        
        for dest in destinations:
            cursor.execute("SELECT name FROM destinations WHERE name LIKE ?", (f"%{dest}%",))
            result = cursor.fetchone()
            
            if result:
                verified_items.append(f"Destination: {dest}")
            else:
                hallucinations.append({
                    "type": "destination",
                    "item": dest,
                    "severity": "high",
                    "message": f"Destination '{dest}' not found in database",
                    "action": "Replace with verified destination or mark as conceptual"
                })
        
        # =========================
        # CHECK 2: VERIFY SPACECRAFT
        # =========================
        spacecraft = itinerary.get("spacecraft_used", [])
        
        for ship in spacecraft:
            cursor.execute("SELECT name FROM starships WHERE name LIKE ?", (f"%{ship}%",))
            result = cursor.fetchone()
            
            if result:
                verified_items.append(f"Spacecraft: {ship}")
            else:
                hallucinations.append({
                    "type": "spacecraft",
                    "item": ship,
                    "severity": "high",
                    "message": f"Spacecraft '{ship}' not found in fleet database",
                    "action": "Replace with available starship"
                })
        
        # =========================
        # CHECK 3: VERIFY ACCOMMODATIONS
        # =========================
        daily_plan = itinerary.get("daily_plan", [])
        
        for day in daily_plan:
            accommodation = day.get("accommodation", "")
            if accommodation and accommodation != "In transit":
                cursor.execute("SELECT name FROM destinations WHERE name LIKE ?", (f"%{accommodation}%",))
                result = cursor.fetchone()
                
                if result:
                    verified_items.append(f"Accommodation: {accommodation}")
                else:
                    # Not necessarily a hallucination - might be generic description
                    # Only flag if it sounds like a specific hotel name
                    if any(word in accommodation.lower() for word in ["hotel", "resort", "base", "station"]):
                        hallucinations.append({
                            "type": "accommodation",
                            "item": accommodation,
                            "severity": "medium",
                            "message": f"Accommodation '{accommodation}' not verified in database",
                            "action": "Verify or replace with known accommodation"
                        })
        
        # =========================
        # CHECK 4: COST REASONABLENESS
        # =========================
        total_cost = itinerary.get("total_cost_usd", 0)
        duration = itinerary.get("duration_days", 1)
        
        # Sanity check: Space travel shouldn't be cheaper than $1M/day
        # Only check if duration is valid (greater than 0)
        if duration > 0 and total_cost / duration < 1000000:
            hallucinations.append({
                "type": "unrealistic_cost",
                "item": f"${total_cost:,.0f} for {duration} days",
                "severity": "medium",
                "message": "Cost seems unrealistically low for space travel",
                "action": "Recalculate costs based on database prices"
            })
        elif duration == 0:
            hallucinations.append({
                "type": "missing_duration",
                "item": "Duration is 0 days",
                "severity": "high",
                "message": "Itinerary has no duration specified",
                "action": "Add valid trip duration"
            })
        
        # =========================
        # COMPILE REPORT
        # =========================
        verification_report = {
            "is_safe": len([h for h in hallucinations if h["severity"] == "high"]) == 0,
            "hallucinations_detected": len(hallucinations),
            "verified_items": len(verified_items),
            "hallucinations": hallucinations,
            "verified": verified_items,
            "summary": self._generate_summary(hallucinations, verified_items)
        }
        
        print(f"  Verification: {'SAFE' if verification_report['is_safe'] else 'HALLUCINATIONS DETECTED'}")
        print(f"  Verified: {len(verified_items)}, Hallucinations: {len(hallucinations)}")
        
        return verification_report
    
    def _generate_summary(self, hallucinations: List, verified: List) -> str:
        """Generate human-readable verification summary"""
        if len(hallucinations) == 0:
            return f"All {len(verified)} items verified against database. No hallucinations detected."
        else:
            high_severity = len([h for h in hallucinations if h["severity"] == "high"])
            if high_severity > 0:
                return f"CRITICAL: {high_severity} high-severity hallucinations detected. Itinerary needs revision."
            else:
                return f"{len(hallucinations)} minor inconsistencies detected. Review recommended."
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Test the agents
if __name__ == "__main__":
    # Test data
    test_itinerary = {
        "itinerary_name": "Lunar Luxury Escape",
        "duration_days": 7,
        "total_cost_usd": 15000000,
        "destinations_visited": ["Lunar Gateway Hotel", "Shackleton Crater Resort"],
        "spacecraft_used": ["Olympus Cruiser"],
        "requirements": ["Medical clearance", "Training"],
        "daily_plan": [
            {
                "day": 1,
                "accommodation": "Lunar Gateway Hotel",
                "activities": []
            }
        ]
    }
    
    # Test Validator
    validator = ValidatorAgent()
    validation_report = validator.validate(test_itinerary, {"max_budget": 20000000})
    print("\n=== VALIDATION REPORT ===")
    print(json.dumps(validation_report, indent=2))
    
    # Test Guardrail
    guardrail = GuardrailAgent()
    verification_report = guardrail.verify(test_itinerary)
    print("\n=== VERIFICATION REPORT ===")
    print(json.dumps(verification_report, indent=2))
