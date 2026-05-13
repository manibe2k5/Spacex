"""
Quick Test Script - Verify System Works

This script tests the entire pipeline without starting the web server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.orchestrator import OrchestratorAgent
import json

def test_system():
    """Test the complete system"""
    
    print("="*60)
    print("STELLAR VOYAGE AI - SYSTEM TEST")
    print("="*60)
    
    # Initialize orchestrator
    print("\n[1/3] Initializing orchestrator...")
    orchestrator = OrchestratorAgent()
    
    # Test query
    print("\n[2/3] Testing with sample query...")
    result = orchestrator.plan_travel(
        user_query="Plan a 7-day luxury vacation to the Moon with a private spacewalk experience and stay at the best resort",
        user_constraints={
            "max_budget": 25000000,
            "passengers": 2,
            "location": "Moon"
        }
    )
    
    # Display results
    print("\n[3/3] Results:")
    print("="*60)
    
    itinerary = result.get("itinerary", {})
    validation = result.get("validation", {})
    verification = result.get("verification", {})
    
    print(f"\nItinerary Name: {itinerary.get('itinerary_name', 'N/A')}")
    print(f"Duration: {itinerary.get('duration_days', 0)} days")
    print(f"Total Cost: ${itinerary.get('total_cost_usd', 0):,.0f}")
    print(f"Confidence: {itinerary.get('confidence_score', 0):.2%}")
    
    print(f"\nValidation: {'PASSED' if validation.get('is_valid') else 'FAILED'}")
    print(f"Verification: {'SAFE' if verification.get('is_safe') else 'NEEDS REVIEW'}")
    
    if itinerary.get('daily_plan'):
        print(f"\nDaily Plan: {len(itinerary['daily_plan'])} days planned")
    
    if itinerary.get('highlights'):
        print(f"\nHighlights:")
        for highlight in itinerary['highlights'][:3]:
            print(f"  - {highlight}")
    
    print("\n" + "="*60)
    print("✓ SYSTEM TEST COMPLETE!")
    print("="*60)
    
    # Save full result to file
    with open("test_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nFull result saved to: test_result.json")
    
    return result

if __name__ == "__main__":
    try:
        test_system()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
