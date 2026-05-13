"""
WEATHER AGENT - Live Space Conditions Fetcher

WHY THIS AGENT?
- Fetches real-time space weather from NASA/NOAA public APIs
- Injects live environmental context into the LangGraph pipeline
- Uses the same data sources as the MCP server (backend/mcp/weather_mcp_server.py)

HOW IT WORKS:
1. Parses user query + constraints to find destination keywords
2. Fetches global space weather (Kp-index, solar flares) from NOAA SWPC + NASA DONKI
3. Fetches per-destination conditions (Mars REMS / Moon solar wind / orbit radiation)
4. Returns a structured weather_context dict consumed by OptimizerAgent and ValidatorAgent

MCP SERVER (standalone — for Claude Desktop / Windsurf):
    set PYTHONPATH=%CD%
    uv run python backend/mcp/weather_mcp_server.py

APIS USED:
    - NOAA SWPC: https://services.swpc.noaa.gov  (no key required)
    - NASA DONKI: https://api.nasa.gov/DONKI      (NASA_API_KEY in .env)
    - Mars REMS:  https://cab.inta-csic.es/rems   (no key required)
"""

from typing import Dict, List
import httpx
from datetime import datetime
from backend.config import NASA_API_KEY

NOAA_SWPC_BASE = "https://services.swpc.noaa.gov"
NASA_DONKI_BASE = "https://api.nasa.gov/DONKI"
MARS_REMS_URL = "https://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php"

DESTINATION_KEYWORDS: Dict[str, List[str]] = {
    "Moon": ["moon", "lunar"],
    "Mars": ["mars"],
    "Earth Orbit": ["orbit", "iss", "earth orbit"],
    "Asteroid Belt": ["asteroid", "psyche", "belt"],
    "Titan": ["titan"],
}


class WeatherAgent:
    """
    Fetches real-time space weather for destinations in the user's travel query.

    Uses the same underlying API calls as backend/mcp/weather_mcp_server.py so
    the MCP tools and this agent always return consistent data.
    """

    def __init__(self):
        self.api_key = NASA_API_KEY or "DEMO_KEY"
        print("Weather Agent initialized!")

    # =========================
    # PUBLIC INTERFACE
    # =========================

    def get_weather_context(self, user_query: str, user_constraints: Dict = None) -> Dict:
        """
        Fetch live weather for all destinations found in the query.

        Args:
            user_query: Natural-language travel request
            user_constraints: May include 'location' key

        Returns:
            weather_context dict with:
              - fetched_at    : ISO timestamp
              - destinations  : per-destination condition dicts
              - space_weather : global Kp/flare/radiation status
              - safety_alerts : list of human-readable warnings
        """
        print("\nWeather Agent: Fetching live space conditions...")

        destinations_to_check = self._detect_destinations(user_query, user_constraints)

        weather_context: Dict = {
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "destinations": {},
            "space_weather": {},
            "safety_alerts": [],
        }

        # Always fetch global space weather first (needed by all destinations)
        space_weather = self._get_space_weather()
        weather_context["space_weather"] = space_weather

        # Global alerts
        if space_weather.get("solar_flare_alert"):
            weather_context["safety_alerts"].append(
                "Solar flare detected today — consider rescheduling EVA activities"
            )
        if space_weather.get("geomagnetic_storm_active"):
            weather_context["safety_alerts"].append(
                f"Geomagnetic storm active (Kp={space_weather.get('kp_index', '?')}) "
                "— enhanced radiation shielding required for all destinations"
            )
        if not space_weather.get("safe_for_deep_space_travel", True):
            weather_context["safety_alerts"].append(
                "Extreme space weather (Kp>=7) — deep-space travel not recommended"
            )

        # Per-destination conditions
        for dest in destinations_to_check:
            conditions = self._get_destination_conditions(dest, space_weather)
            weather_context["destinations"][dest] = conditions

            if not conditions.get("safe_for_eva", True):
                weather_context["safety_alerts"].append(
                    f"{dest}: {conditions.get('eva_recommendation', 'EVA not recommended under current conditions')}"
                )
            if dest == "Mars" and conditions.get("storm_risk") == "high":
                weather_context["safety_alerts"].append(
                    "Mars: Dust storm risk is HIGH — outdoor rover activities should be postponed"
                )

        print(f"  Destinations checked : {list(weather_context['destinations'].keys())}")
        print(f"  Safety alerts        : {len(weather_context['safety_alerts'])}")

        return weather_context

    # =========================
    # DESTINATION DETECTION
    # =========================

    def _detect_destinations(self, user_query: str, user_constraints: Dict = None) -> List[str]:
        """Parse the query and constraints to find which destinations to fetch."""
        query_lower = user_query.lower()
        found = []

        for dest, keywords in DESTINATION_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                found.append(dest)

        if user_constraints and "location" in user_constraints:
            loc = str(user_constraints["location"]).lower()
            for dest, keywords in DESTINATION_KEYWORDS.items():
                if any(kw in loc for kw in keywords) and dest not in found:
                    found.append(dest)

        # Default: at minimum fetch Moon data so we always have something
        if not found:
            found = ["Moon"]

        return found

    # =========================
    # API FETCH HELPERS
    # =========================

    def _fetch(self, url: str, params: dict = None) -> dict | list:
        """HTTP GET with SSL bypass for corporate networks. Returns dict/list or error dict."""
        try:
            with httpx.Client(verify=False, timeout=10.0, follow_redirects=True) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            return {"error": str(e)}

    # =========================
    # DATA FETCHERS
    # =========================

    def _get_space_weather(self) -> dict:
        """Fetch Kp-index from NOAA SWPC and solar flares from NASA DONKI."""
        kp_data = self._fetch(f"{NOAA_SWPC_BASE}/json/planetary_k_index_1m.json")
        flare_data = self._fetch(
            f"{NASA_DONKI_BASE}/FLR",
            params={
                "startDate": datetime.utcnow().strftime("%Y-%m-%d"),
                "api_key": self.api_key,
            },
        )

        kp_index = 2.0
        geomagnetic_storm = False
        solar_flares = []

        try:
            if isinstance(kp_data, list) and len(kp_data) > 0:
                for entry in reversed(kp_data):
                    if isinstance(entry, dict) and entry.get("kp_index"):
                        kp_index = float(entry["kp_index"])
                        break
                geomagnetic_storm = kp_index >= 5
        except Exception as e:
            print(f"  Kp-index parse error: {e}")

        try:
            if isinstance(flare_data, list):
                for flare in flare_data[-3:]:
                    solar_flares.append({
                        "class": flare.get("classType", "unknown"),
                        "peak_time": flare.get("peakTime", ""),
                    })
        except Exception as e:
            print(f"  Solar flare parse error: {e}")

        return {
            "source": "NOAA SWPC + NASA DONKI",
            "kp_index": kp_index,
            "geomagnetic_storm_active": geomagnetic_storm,
            "solar_flares_today": solar_flares,
            "solar_flare_alert": len(solar_flares) > 0,
            "radiation_belt_status": (
                "storm" if kp_index >= 7 else "elevated" if kp_index >= 5 else "normal"
            ),
            "safe_for_deep_space_travel": kp_index < 7,
        }

    def _get_mars_weather(self) -> dict:
        """Fetch Mars surface conditions from Curiosity Rover REMS."""
        data = self._fetch(MARS_REMS_URL)

        if isinstance(data, dict) and "error" in data:
            print(f"  Mars REMS unavailable ({data['error']}) — using fallback values")
            return {
                "source": "Mars REMS (fallback — API unavailable)",
                "temperature_min_celsius": -73,
                "temperature_max_celsius": -5,
                "pressure_pa": 815,
                "uv_index": "moderate",
                "storm_risk": "low",
                "safe_for_surface_activity": True,
                "safe_for_eva": True,
            }

        try:
            sol_keys = data.get("sol_keys", [])
            if sol_keys:
                latest_sol = sol_keys[-1]
                sol = data[latest_sol]
                min_temp = sol.get("min_temp", -73)
                max_temp = sol.get("max_temp", -5)
                pressure = float(sol.get("pressure") or 815)
                uv = sol.get("local_uv_irradiance_index", "moderate")
                storm_risk = "high" if pressure < 600 else "low"
                return {
                    "source": "Mars REMS (Curiosity Rover)",
                    "sol": latest_sol,
                    "terrestrial_date": sol.get("terrestrial_date", ""),
                    "temperature_min_celsius": min_temp,
                    "temperature_max_celsius": max_temp,
                    "pressure_pa": pressure,
                    "uv_index": uv,
                    "storm_risk": storm_risk,
                    "safe_for_surface_activity": storm_risk != "high",
                    "safe_for_eva": storm_risk != "high",
                }
        except Exception as e:
            print(f"  Mars REMS parse error: {e}")

        return {
            "source": "Mars REMS (parse error — using defaults)",
            "temperature_min_celsius": -73,
            "temperature_max_celsius": -5,
            "pressure_pa": 815,
            "storm_risk": "low",
            "safe_for_surface_activity": True,
            "safe_for_eva": True,
        }

    def _get_moon_conditions(self) -> dict:
        """Derive Moon surface conditions from NOAA solar wind plasma data."""
        data = self._fetch(f"{NOAA_SWPC_BASE}/products/solar-wind/plasma-7-day.json")

        if isinstance(data, dict) and "error" in data:
            print(f"  NOAA solar wind unavailable ({data['error']}) — using fallback values")
            return {
                "source": "NOAA SWPC Solar Wind (fallback)",
                "solar_wind_speed_km_s": 450.0,
                "solar_wind_density_cm3": 5.0,
                "radiation_level": "moderate",
                "safe_for_eva": True,
                "eva_recommendation": "EVA conditions nominal.",
            }

        try:
            if isinstance(data, list) and len(data) > 1:
                latest = data[-1]
                density = float(latest[1]) if latest[1] and latest[1] != "" else 5.0
                speed = float(latest[2]) if latest[2] and latest[2] != "" else 450.0

                if speed > 700 or density > 20:
                    radiation_level = "high"
                    safe_for_eva = False
                    recommendation = "EVA NOT recommended — solar wind storm in progress."
                elif speed > 550:
                    radiation_level = "moderate-high"
                    safe_for_eva = True
                    recommendation = "EVA permitted with enhanced radiation shielding."
                else:
                    radiation_level = "moderate"
                    safe_for_eva = True
                    recommendation = "EVA conditions nominal."

                return {
                    "source": "NOAA SWPC Solar Wind",
                    "solar_wind_speed_km_s": round(speed, 1),
                    "solar_wind_density_cm3": round(density, 2),
                    "radiation_level": radiation_level,
                    "safe_for_eva": safe_for_eva,
                    "eva_recommendation": recommendation,
                }
        except Exception as e:
            print(f"  Moon conditions parse error: {e}")

        return {
            "source": "NOAA SWPC Solar Wind (parse error)",
            "solar_wind_speed_km_s": 450.0,
            "radiation_level": "moderate",
            "safe_for_eva": True,
            "eva_recommendation": "EVA conditions nominal.",
        }

    def _get_destination_conditions(self, destination: str, space_weather: dict) -> dict:
        """Dispatch to the right data fetcher for each destination."""
        if destination == "Moon":
            return self._get_moon_conditions()

        if destination == "Mars":
            return self._get_mars_weather()

        if destination == "Earth Orbit":
            kp = space_weather.get("kp_index", 2.0)
            return {
                "source": "NOAA SWPC + NASA DONKI",
                "temperature_range_celsius": {"min": -157, "max": 121},
                "radiation_level": space_weather.get("radiation_belt_status", "normal"),
                "solar_flare_alert": space_weather.get("solar_flare_alert", False),
                "kp_index": kp,
                "safe_for_eva": kp < 5,
                "eva_recommendation": (
                    "EVA conditions nominal."
                    if kp < 5
                    else "Geomagnetic storm active — EVA not recommended."
                ),
            }

        if destination == "Asteroid Belt":
            return {
                "source": "NOAA SWPC + NASA DONKI",
                "deep_space_radiation": space_weather.get("radiation_belt_status", "normal"),
                "solar_flare_alert": space_weather.get("solar_flare_alert", False),
                "micrometeorite_risk": "moderate",
                "temperature_celsius": -100,
                "safe_for_mining_operations": not space_weather.get("solar_flare_alert", False),
            }

        if destination == "Titan":
            return {
                "source": "NASA Cassini Atmospheric Models",
                "temperature_celsius": -179,
                "atmospheric_pressure_bar": 1.45,
                "wind_speed_ms": 3,
                "haze_level": "thick orange haze",
                "methane_rain": "possible",
                "safe_for_eva": True,
                "safe_for_surface_ops": True,
                "note": "Real-time Titan telemetry unavailable — using Cassini mission models.",
            }

        return {
            "status": "unknown",
            "message": f"No weather data available for '{destination}'.",
        }
