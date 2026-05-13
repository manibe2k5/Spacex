"""
Database Initialization Script

WHY THIS FILE?
- Creates SQLite database with structured space travel data
- Populates with realistic sample data (starships, destinations, etc.)
- Provides the "facts" that RAG will retrieve

WHAT IT CONTAINS:
- Starship fleet (luxury spacecraft)
- Destinations (Moon, Mars, asteroids, space stations)
- Launch windows (optimal travel times)
- VVIP profiles (personalization data)
"""

import sqlite3
import json
from datetime import datetime, timedelta

# Database file path
DB_PATH = "./backend/data/stellar_voyage.db"

def init_database():
    """
    Initialize the database with schema and sample data
    
    WHY SQLITE?
    - Lightweight, no server needed
    - Perfect for structured data (prices, dates, availability)
    - Fast queries for filtering (e.g., "ships available next week")
    """
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating database schema...")
    
    # =========================
    # TABLE 1: STARSHIPS
    # =========================
    # WHY? Stores available spacecraft with their capabilities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS starships (
            ship_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            capacity INTEGER,
            max_range_km BIGINT,
            luxury_rating INTEGER,
            amenities TEXT,
            current_location TEXT,
            next_available DATE,
            cost_per_day DECIMAL
        )
    """)
    
    # =========================
    # TABLE 2: DESTINATIONS
    # =========================
    # WHY? Stores places VVIPs can visit (Moon, Mars, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            dest_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            celestial_body TEXT NOT NULL,
            coordinates TEXT,
            accommodation_type TEXT,
            max_guests INTEGER,
            activities TEXT,
            season_best TEXT,
            distance_from_earth_km BIGINT,
            luxury_rating INTEGER,
            cost_per_night DECIMAL
        )
    """)
    
    # =========================
    # TABLE 3: LAUNCH WINDOWS
    # =========================
    # WHY? Space travel depends on planetary alignment
    # Can't go to Mars anytime - need optimal trajectories!
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS launch_windows (
            window_id TEXT PRIMARY KEY,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            opens_date DATE,
            closes_date DATE,
            travel_duration_days INTEGER,
            fuel_efficiency_score DECIMAL,
            trajectory_type TEXT
        )
    """)
    
    # =========================
    # TABLE 4: VVIP PROFILES
    # =========================
    # WHY? Personalization - remember preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vvip_profiles (
            vvip_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            past_destinations TEXT,
            preferred_ship_type TEXT,
            dietary_restrictions TEXT,
            medical_conditions TEXT,
            adventure_level INTEGER,
            privacy_level TEXT
        )
    """)
    
    print("Schema created!")
    print("Inserting sample data...")
    
    # =========================
    # SAMPLE DATA: STARSHIPS
    # =========================
    starships = [
        ("SS-001", "Olympus Cruiser", "luxury", 12, 400000000, 5, 
         json.dumps(["Zero-G Pool", "Holographic Cinema", "Michelin Restaurant", "Observation Deck", "AI Personal Trainer"]),
         "earth_orbit", (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), 5000000),
        
        ("SS-002", "Starship SN-47", "luxury", 8, 800000000, 5,
         json.dumps(["Presidential Suite", "Private Spacewalk Bay", "Cryo-Sleep Pods", "Medical Bay", "Zero-G Spa"]),
         "lunar_gateway", (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), 8000000),
        
        ("SS-003", "Velocity Express", "speed", 6, 600000000, 4,
         json.dumps(["Nuclear Propulsion", "Fast Transit", "Compact Luxury", "Emergency Medical"]),
         "mars_orbit", (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"), 6000000),
        
        ("SS-004", "Cosmic Explorer", "research", 15, 1000000000, 4,
         json.dumps(["Science Lab", "Telescope Array", "Sample Collection", "Educational Programs"]),
         "earth_orbit", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), 4000000),
        
        ("SS-005", "Aurora Starship", "luxury", 10, 500000000, 5,
         json.dumps(["Sky Lounge", "Private Cabins", "Gourmet Kitchen", "VR Entertainment", "Fitness Center"]),
         "earth_orbit", (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), 7000000),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO starships VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, starships)
    
    # =========================
    # SAMPLE DATA: DESTINATIONS
    # =========================
    destinations = [
        ("DEST-001", "Lunar Gateway Hotel", "Moon", "Lunar Orbit L1", "Orbital Station", 50,
         json.dumps(["Moonwalk", "Earth-rise Viewing", "Zero-G Spa", "Lunar Rover Tours"]),
         "Year-round", 384400, 5, 500000),
        
        ("DEST-002", "Shackleton Crater Resort", "Moon", "South Pole -89.9°", "Surface Dome", 30,
         json.dumps(["Crater Exploration", "Ice Mining Tour", "Astronomy Sessions", "Low-G Sports"]),
         "Year-round", 384400, 5, 800000),
        
        ("DEST-003", "Starbase Alpha", "Mars", "Jezero Crater 18.4°N", "Underground Colony", 100,
         json.dumps(["Rover Racing", "Olympus Mons Hike", "Colony Tour", "Martian Garden", "Ice Caves"]),
         "Every 26 months", 225000000, 4, 1200000),
        
        ("DEST-004", "ISS-2 Space Station", "Earth Orbit", "LEO 400km", "Orbital Station", 20,
         json.dumps(["Spacewalk", "Earth Observation", "Zero-G Research", "Manufacturing Tour"]),
         "Year-round", 400, 4, 300000),
        
        ("DEST-005", "Asteroid 16 Psyche Base", "Asteroid Belt", "Psyche Asteroid", "Mining Outpost", 8,
         json.dumps(["Zero-G Mining", "Precious Metal Collection", "Deep Space Views", "Exclusive Access"]),
         "Every 5 years", 450000000, 5, 2000000),
        
        ("DEST-006", "Titan Floating City", "Saturn Moon", "Titan Kraken Mare", "Floating Platform", 40,
         json.dumps(["Methane Lake Cruise", "Thick Atmosphere Walk", "Hydrocarbon Rain Experience"]),
         "Every 29 years", 1400000000, 5, 5000000),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO destinations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, destinations)
    
    # =========================
    # SAMPLE DATA: LAUNCH WINDOWS
    # =========================
    base_date = datetime.now()
    launch_windows = [
        ("LW-001", "Earth", "Moon", 
         (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
         (base_date + timedelta(days=30)).strftime("%Y-%m-%d"),
         3, 0.95, "direct"),
        
        ("LW-002", "Earth", "Mars",
         (base_date + timedelta(days=15)).strftime("%Y-%m-%d"),
         (base_date + timedelta(days=45)).strftime("%Y-%m-%d"),
         180, 0.88, "hohmann"),
        
        ("LW-003", "Moon", "Mars",
         (base_date + timedelta(days=20)).strftime("%Y-%m-%d"),
         (base_date + timedelta(days=50)).strftime("%Y-%m-%d"),
         175, 0.90, "hohmann"),
        
        ("LW-004", "Earth", "Asteroid Belt",
         (base_date + timedelta(days=60)).strftime("%Y-%m-%d"),
         (base_date + timedelta(days=120)).strftime("%Y-%m-%d"),
         400, 0.75, "fast"),
        
        ("LW-005", "Mars", "Earth",
         (base_date + timedelta(days=200)).strftime("%Y-%m-%d"),
         (base_date + timedelta(days=230)).strftime("%Y-%m-%d"),
         180, 0.87, "hohmann"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO launch_windows VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, launch_windows)
    
    # =========================
    # SAMPLE DATA: VVIP PROFILES
    # =========================
    vvip_profiles = [
        ("VVIP-001", "Elon Musk", 
         json.dumps(["Mars", "Moon", "ISS"]),
         "speed", "None", "None", 10, "moderate"),
        
        ("VVIP-002", "Jeff Bezos",
         json.dumps(["Moon", "ISS"]),
         "luxury", "Vegetarian", "None", 7, "maximum"),
        
        ("VVIP-003", "Richard Branson",
         json.dumps(["Suborbital", "ISS"]),
         "luxury", "None", "None", 9, "social"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO vvip_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, vvip_profiles)
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("Database initialized with sample data!")
    print(f"Created: {len(starships)} starships, {len(destinations)} destinations")
    print(f"Launch windows: {len(launch_windows)}")
    print(f"VVIP profiles: {len(vvip_profiles)}")

if __name__ == "__main__":
    init_database()
