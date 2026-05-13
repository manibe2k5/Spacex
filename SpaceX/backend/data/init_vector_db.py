"""
Vector Database Initialization (Chroma)

WHY THIS FILE?
- Creates vector database for semantic search
- Stores unstructured knowledge (guides, tips, descriptions)
- Enables RAG to find relevant context for user queries

HOW IT WORKS:
1. Takes text documents about space travel
2. Converts them to embeddings (numerical vectors)
3. Stores in Chroma database
4. Later: User query → Find similar documents → Send to LLM
"""

import chromadb
from chromadb.config import Settings
from backend.utils.llm_client import get_embedding
from backend.config import CHROMA_DB_PATH

def init_vector_db():
    """
    Initialize Chroma vector database with space travel knowledge
    
    WHY CHROMA?
    - Fast semantic search
    - Stores embeddings efficiently
    - Easy to query by similarity
    """
    
    print("Initializing Chroma Vector Database...")
    
    # Create Chroma client
    # persist_directory: Where to save the database
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Delete existing collection if it exists (fresh start)
    try:
        client.delete_collection("space_travel_knowledge")
    except:
        pass
    
    # Create new collection
    # WHY COLLECTION? Like a table in SQL, groups related documents
    collection = client.create_collection(
        name="space_travel_knowledge",
        metadata={"description": "Space travel guides and information"}
    )
    
    print("Adding knowledge documents...")
    
    # =========================
    # KNOWLEDGE DOCUMENTS
    # =========================
    # These are the "facts" the AI will retrieve to answer questions
    # In production, you'd have thousands of these from real sources
    
    documents = [
        # LUNAR TRAVEL
        {
            "id": "doc_001",
            "text": """
            Lunar Gateway Hotel: The premier orbital accommodation around the Moon.
            Located at the L1 Lagrange point, offering stunning Earth-rise views.
            Features include zero-gravity spa, observation decks, and Michelin-star dining.
            Travel time from Earth: 3 days via direct trajectory.
            Best for: First-time space travelers, romantic getaways, corporate retreats.
            Amenities: 50 luxury suites, medical bay, emergency escape pods, AI concierge.
            Price range: $500,000 per night. Booking requires 6 months advance notice.
            """,
            "metadata": {"category": "accommodation", "location": "Moon", "type": "orbital"}
        },
        {
            "id": "doc_002",
            "text": """
            Shackleton Crater Resort: Exclusive lunar surface experience.
            Located at Moon's South Pole with permanent ice deposits nearby.
            Pressurized dome architecture with Earth-view windows.
            Activities: Moonwalks (guided), rover expeditions, low-gravity sports, ice mining tours.
            Travel time from Lunar Gateway: 6 hours via lunar shuttle.
            Best for: Adventure seekers, geology enthusiasts, extreme luxury travelers.
            Safety: Full life support, radiation shielding, emergency return capability.
            Price: $800,000 per night including all activities.
            """,
            "metadata": {"category": "accommodation", "location": "Moon", "type": "surface"}
        },
        
        # MARS TRAVEL
        {
            "id": "doc_003",
            "text": """
            Mars Travel Guide: Journey to the Red Planet.
            Optimal launch windows occur every 26 months when Earth and Mars align.
            Travel duration: 6-9 months depending on trajectory (Hohmann transfer orbit).
            Modern nuclear propulsion can reduce this to 45 days.
            Requirements: Medical clearance, radiation exposure waiver, psychological evaluation.
            What to expect: Zero-gravity transit, potential cryo-sleep, stunning views of Earth shrinking.
            Landing sites: Jezero Crater (Starbase Alpha), Valles Marineris (Starbase Beta).
            Cost: $50M-$150M per person depending on ship class and amenities.
            """,
            "metadata": {"category": "travel_guide", "location": "Mars", "type": "transit"}
        },
        {
            "id": "doc_004",
            "text": """
            Starbase Alpha - Mars Colony Experience.
            Located in Jezero Crater, site of ancient river delta.
            Underground biodome architecture protects from radiation and dust storms.
            Population: 500 permanent residents, 100 tourist capacity.
            Activities: Rover racing on Martian terrain, Olympus Mons virtual hike,
            colony infrastructure tour, Martian garden (growing Earth plants in Martian soil),
            underground ice cave exploration, meet-and-greet with colonists.
            Dining: Hydroponic vegetables, 3D-printed proteins, imported delicacies from Earth.
            Duration: Minimum 30-day stay (due to launch window constraints).
            Price: $1.2M per night, all-inclusive.
            """,
            "metadata": {"category": "accommodation", "location": "Mars", "type": "colony"}
        },
        
        # ASTEROID BELT
        {
            "id": "doc_005",
            "text": """
            Asteroid 16 Psyche Expedition: The Ultimate Exclusive Experience.
            Psyche is a rare metallic asteroid composed of iron, nickel, gold, and platinum.
            Estimated value: $10,000 quadrillion (more than Earth's entire economy).
            Travel time from Earth: 2-3 years (only for the most adventurous VVIPs).
            Experience: Zero-gravity mining demonstration, collect precious metal samples,
            witness deep space phenomena, exclusive access (only 8 guests per expedition).
            Scientific significance: Believed to be exposed core of early planet.
            Requirements: Extensive medical screening, cryo-sleep capability, emergency protocols.
            Price: $2M per night at mining outpost, minimum 60-day stay.
            Booking: Only 2 expeditions per decade due to orbital mechanics.
            """,
            "metadata": {"category": "destination", "location": "Asteroid Belt", "type": "expedition"}
        },
        
        # SPACECRAFT
        {
            "id": "doc_006",
            "text": """
            Olympus Cruiser: Luxury Interplanetary Starship.
            Capacity: 12 passengers in ultra-luxury configuration.
            Range: 400 million km (Earth to Jupiter).
            Amenities: Zero-G swimming pool, holographic entertainment cinema,
            Michelin 3-star restaurant with celebrity chef, observation deck with 360° views,
            AI personal trainer, private cabins with Earth-view windows, medical bay.
            Propulsion: Ion drive with solar panels, nuclear backup.
            Speed: 50,000 km/h cruise speed.
            Best for: Leisurely interplanetary cruises, corporate executive retreats.
            Cost: $5M per day charter.
            """,
            "metadata": {"category": "spacecraft", "type": "luxury", "capacity": "12"}
        },
        {
            "id": "doc_007",
            "text": """
            Velocity Express: Speed-Optimized Starship.
            Capacity: 6 passengers in compact luxury.
            Range: 600 million km.
            Propulsion: Nuclear thermal rocket (fastest civilian spacecraft).
            Speed: 150,000 km/h - reduces Mars transit to 45 days.
            Amenities: Compact luxury suites, fast-transit cryo-sleep pods,
            emergency medical bay, entertainment system.
            Best for: Time-sensitive travelers, executives with tight schedules.
            Trade-off: Less spacious than Olympus Cruiser but 3x faster.
            Cost: $6M per day charter.
            """,
            "metadata": {"category": "spacecraft", "type": "speed", "capacity": "6"}
        },
        
        # SAFETY & REGULATIONS
        {
            "id": "doc_008",
            "text": """
            Space Travel Safety Protocols.
            Medical requirements: Cardiovascular health check, bone density scan,
            radiation exposure baseline, psychological evaluation.
            Age restrictions: 18-70 years (exceptions with medical clearance).
            Training: 2-week pre-flight training including zero-G adaptation,
            emergency procedures, life support systems, spacewalk basics.
            Radiation exposure: Monitored continuously, annual limits enforced.
            Emergency protocols: All ships have escape pods, emergency return trajectories,
            real-time communication with Earth mission control.
            Insurance: Mandatory $10M space travel insurance.
            Legal: Waiver of liability, next-of-kin notification, will documentation.
            """,
            "metadata": {"category": "safety", "type": "regulations"}
        },
        
        # SPACE WEATHER
        {
            "id": "doc_009",
            "text": """
            Space Weather and Travel Planning.
            Solar flares: X-class flares can delay launches by 12-48 hours.
            Coronal Mass Ejections (CME): Require trajectory adjustments or delays.
            Radiation storms: Ships have enhanced shielding, but severe storms require shelter.
            Monitoring: Real-time space weather forecasts from NOAA and ESA.
            Impact on itineraries: 15% of launches experience minor delays.
            Mitigation: AI systems automatically calculate safer alternative routes.
            Passenger safety: Always prioritized over schedule adherence.
            Compensation: Full refund for delays over 72 hours, or complimentary upgrade.
            """,
            "metadata": {"category": "space_weather", "type": "planning"}
        },
        
        # VVIP EXPERIENCES
        {
            "id": "doc_010",
            "text": """
            Exclusive VVIP Experiences.
            Private spacewalk: $5M per person, 4-hour duration, professional astronaut guide.
            Name a crater: $5M donation to space research, permanent lunar/Mars crater naming rights.
            Zero-G wedding: $10M package, ceremony in orbit with Earth backdrop.
            Exoplanet discovery: Access to James Webb Space Telescope, name newly discovered planet.
            Meet Mars colonists: Private dinner with first-generation Martians.
            Asteroid sample collection: Keep precious metal samples from Psyche (up to 1kg).
            Aurora re-entry: Timed spacecraft re-entry through Northern Lights.
            Celebrity astronaut escort: Travel with famous astronauts (Buzz Aldrin's grandson, etc.).
            """,
            "metadata": {"category": "experiences", "type": "vvip_exclusive"}
        },
        
        # COST OPTIMIZATION
        {
            "id": "doc_011",
            "text": """
            Cost Optimization for Interplanetary Travel.
            Launch windows: Traveling during optimal planetary alignment saves 30-40% fuel costs.
            Ship selection: Luxury cruisers cost more but offer better experience for long journeys.
            Group bookings: 10+ passengers receive 15% discount on charter costs.
            Off-peak travel: Non-holiday periods offer 20% savings.
            Flexible itineraries: Allowing AI to optimize routes can save $10-20M.
            Cryo-sleep option: Reduces life support costs by 50% for journeys over 60 days.
            Shared charters: Split costs with other VVIPs (privacy maintained via separate modules).
            Early booking: 12+ months advance booking receives 10% discount.
            """,
            "metadata": {"category": "cost", "type": "optimization"}
        },
        
        # TITAN (SATURN MOON)
        {
            "id": "doc_012",
            "text": """
            Titan Floating City: The Most Remote Luxury Destination.
            Location: Saturn's largest moon, 1.4 billion km from Earth.
            Travel time: 7 years via conventional propulsion, 2 years via nuclear.
            Unique features: Thick atmosphere (only moon with substantial atmosphere),
            methane lakes and rivers, hydrocarbon rain, orange sky.
            Accommodation: Floating platform on Kraken Mare (methane sea).
            Experience: Walk outside without spacesuit (just oxygen mask - atmosphere is dense),
            methane lake cruise, witness hydrocarbon weather, view Saturn's rings.
            Capacity: 40 guests maximum.
            Cost: $5M per night (includes 2-year round-trip travel).
            Best for: Ultimate bragging rights, once-in-a-lifetime experience.
            Booking: Only 1 expedition per decade.
            """,
            "metadata": {"category": "destination", "location": "Titan", "type": "extreme_luxury"}
        },
    ]
    
    # =========================
    # ADD DOCUMENTS TO CHROMA
    # =========================
    print(f"Processing {len(documents)} documents...")
    
    for i, doc in enumerate(documents):
        print(f"  [{i+1}/{len(documents)}] Embedding: {doc['id']}")
        
        # Generate embedding for the document text
        # This converts text to a 3072-dimensional vector
        embedding = get_embedding(doc["text"])
        
        # Add to Chroma collection
        collection.add(
            ids=[doc["id"]],
            embeddings=[embedding],
            documents=[doc["text"]],
            metadatas=[doc["metadata"]]
        )
    
    print(f"Vector database initialized with {len(documents)} documents!")
    print(f"Database location: {CHROMA_DB_PATH}")
    
    return collection

if __name__ == "__main__":
    init_vector_db()
