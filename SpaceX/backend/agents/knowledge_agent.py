"""
KNOWLEDGE AGENT - RAG Specialist

WHY THIS AGENT?
- Retrieves relevant information from both Vector DB and SQLite
- Combines unstructured knowledge (guides) with structured data (prices, availability)
- Provides context to other agents for informed decision-making

HOW IT WORKS:
1. User query → Generate embedding
2. Search Chroma for similar documents (semantic search)
3. Query SQLite for structured data (exact matches)
4. Combine and return enriched context
"""

import sqlite3
import chromadb
from chromadb.config import Settings
from typing import Dict, List
from backend.utils.llm_client import get_embedding
from backend.config import CHROMA_DB_PATH, SQLITE_DB_PATH, MAX_RETRIEVAL_RESULTS

class KnowledgeAgent:
    """
    Retrieves relevant information from knowledge bases
    
    ANALOGY: Like a research librarian who knows where to find information
    """
    
    def __init__(self):
        """Initialize connections to both databases"""
        
        # Connect to Vector Database (Chroma)
        # WHY? For semantic search - finds conceptually similar content
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.chroma_client.get_collection("space_travel_knowledge")
        
        # Connect to Structured Database (SQLite)
        # WHY? For exact queries - prices, dates, availability
        self.sqlite_conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        print("Knowledge Agent initialized!")
    
    def retrieve(self, query: str, filters: Dict = None) -> Dict:
        """
        Retrieve relevant information for a query
        
        Args:
            query: User's question or request
            filters: Optional filters (e.g., {"location": "Mars", "max_price": 1000000})
            
        Returns:
            Dictionary with retrieved documents and structured data
            
        EXAMPLE:
        query = "Luxury hotels on Mars"
        Returns:
        {
            "vector_results": [documents about Mars accommodations],
            "structured_data": {
                "destinations": [Mars hotels from SQLite],
                "starships": [ships that go to Mars]
            }
        }
        """
        
        print(f"\nKnowledge Agent: Searching for '{query}'")
        
        # =========================
        # VALIDATION: CHECK DESTINATION IN QUERY
        # =========================
        # Get all available destinations from database
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT DISTINCT celestial_body FROM destinations")
        available_locations = [row[0].lower() for row in cursor.fetchall()]
        
        # Define valid destination keywords (including variations)
        valid_destinations = {
            'moon': ['moon', 'lunar', 'selene'],
            'mars': ['mars', 'martian', 'red planet'],
            'earth orbit': ['earth orbit', 'iss', 'space station', 'orbital'],
            'asteroid belt': ['asteroid', 'psyche', 'asteroid belt'],
            'titan': ['titan', 'saturn']
        }
        
        # Common Earth destinations that should be rejected
        earth_destinations = [
            'kashmir', 'kailash', 'kailasha', 'himalaya', 'everest',
            'paris', 'london', 'new york', 'tokyo', 'dubai',
            'india', 'china', 'usa', 'europe', 'asia', 'africa',
            'beach', 'mountain', 'desert', 'forest', 'ocean',
            'maldives', 'bali', 'hawaii', 'caribbean', 'alps'
        ]
        
        # Check if query mentions Earth destinations
        query_lower = query.lower()
        mentioned_earth_destination = None
        for earth_dest in earth_destinations:
            if earth_dest in query_lower:
                mentioned_earth_destination = earth_dest.title()
                break
        
        if mentioned_earth_destination:
            return {
                "error": "destination_not_available",
                "message": f"We apologize, but '{mentioned_earth_destination}' is not available in our interplanetary travel system.",
                "available_destinations": ['Moon', 'Mars', 'Earth Orbit (ISS-2)', 'Asteroid Belt (16 Psyche)', 'Titan (Saturn Moon)'],
                "suggestion": "Stellar Voyage AI specializes in space travel. Please choose from: Moon, Mars, Earth Orbit, Asteroid Belt, or Titan.",
                "vector_results": [],
                "structured_data": {}
            }
        
        # Check if filter location is valid
        if filters and "location" in filters:
            requested_location = filters["location"]
            if requested_location:  # Only check if location is specified
                # Check if requested location is available
                location_found = any(
                    requested_location.lower() in loc or 
                    loc in requested_location.lower()
                    for loc in available_locations
                )
                
                if not location_found:
                    # Return error response with available destinations
                    return {
                        "error": "destination_not_available",
                        "message": f"We apologize, but '{requested_location}' is not currently in our destination list.",
                        "available_destinations": ['Moon', 'Mars', 'Earth Orbit (ISS-2)', 'Asteroid Belt (16 Psyche)', 'Titan (Saturn Moon)'],
                        "suggestion": "Please choose from our available interplanetary destinations: Moon, Mars, Earth Orbit, Asteroid Belt, or Titan.",
                        "vector_results": [],
                        "structured_data": {}
                    }
        
        # =========================
        # STEP 1: VECTOR SEARCH
        # =========================
        # Convert query to embedding and find similar documents
        query_embedding = get_embedding(query)
        
        # Search Chroma for semantically similar documents
        # n_results: How many similar documents to return
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=MAX_RETRIEVAL_RESULTS
        )
        
        # Extract documents and metadata
        retrieved_docs = []
        if vector_results['documents'] and len(vector_results['documents'][0]) > 0:
            for i, doc in enumerate(vector_results['documents'][0]):
                retrieved_docs.append({
                    "text": doc,
                    "metadata": vector_results['metadatas'][0][i] if vector_results['metadatas'] else {},
                    "relevance_score": 1 - vector_results['distances'][0][i] if vector_results['distances'] else 0
                })
        
        print(f"  Found {len(retrieved_docs)} relevant documents from vector DB")
        
        # =========================
        # STEP 2: STRUCTURED QUERIES
        # =========================
        # Query SQLite for exact data based on filters
        structured_data = {}
        
        # Query destinations
        destinations = self._query_destinations(filters)
        if destinations:
            structured_data["destinations"] = destinations
            print(f"  Found {len(destinations)} matching destinations")
        
        # Query starships
        starships = self._query_starships(filters)
        if starships:
            structured_data["starships"] = starships
            print(f"  Found {len(starships)} available starships")
        
        # Query launch windows
        launch_windows = self._query_launch_windows(filters)
        if launch_windows:
            structured_data["launch_windows"] = launch_windows
            print(f"  Found {len(launch_windows)} launch windows")
        
        # =========================
        # STEP 3: COMBINE RESULTS
        # =========================
        return {
            "vector_results": retrieved_docs,
            "structured_data": structured_data,
            "query": query
        }
    
    def _query_destinations(self, filters: Dict = None) -> List[Dict]:
        """Query destinations from SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        # Build dynamic SQL query based on filters
        query = "SELECT * FROM destinations WHERE 1=1"
        params = []
        
        if filters:
            if "location" in filters:
                query += " AND celestial_body LIKE ?"
                params.append(f"%{filters['location']}%")
            
            if "max_price" in filters:
                query += " AND cost_per_night <= ?"
                params.append(filters['max_price'])
            
            if "min_luxury_rating" in filters:
                query += " AND luxury_rating >= ?"
                params.append(filters['min_luxury_rating'])
        
        query += " LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        return [dict(row) for row in rows]
    
    def _query_starships(self, filters: Dict = None) -> List[Dict]:
        """Query starships from SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        query = "SELECT * FROM starships WHERE 1=1"
        params = []
        
        if filters:
            if "ship_type" in filters:
                query += " AND type = ?"
                params.append(filters['ship_type'])
            
            if "min_capacity" in filters:
                query += " AND capacity >= ?"
                params.append(filters['min_capacity'])
            
            if "max_cost_per_day" in filters:
                query += " AND cost_per_day <= ?"
                params.append(filters['max_cost_per_day'])
        
        query += " LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def _query_launch_windows(self, filters: Dict = None) -> List[Dict]:
        """Query launch windows from SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        query = "SELECT * FROM launch_windows WHERE 1=1"
        params = []
        
        if filters:
            if "origin" in filters:
                query += " AND origin = ?"
                params.append(filters['origin'])
            
            if "destination" in filters:
                query += " AND destination = ?"
                params.append(filters['destination'])
        
        query += " ORDER BY opens_date LIMIT 5"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def __del__(self):
        """Clean up database connections"""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()

# Test the agent
if __name__ == "__main__":
    agent = KnowledgeAgent()
    
    # Test query
    result = agent.retrieve(
        query="I want luxury accommodation on Mars",
        filters={"location": "Mars", "min_luxury_rating": 4}
    )
    
    print("\n=== RETRIEVAL RESULTS ===")
    print(f"Vector results: {len(result['vector_results'])}")
    print(f"Structured data keys: {list(result['structured_data'].keys())}")
