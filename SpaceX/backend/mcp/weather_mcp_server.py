"""
MCP WEATHER SERVER - Stellar Voyage AI Space Weather Service

WHY THIS FILE?
- Implements a proper Anthropic Model Context Protocol (MCP) server
- Exposes 4 space weather tools consumable by any MCP client
  (Claude Desktop, Windsurf, custom clients, etc.)
- Data sources: NASA DONKI API + NOAA SWPC + Curiosity REMS

HOW TO RUN (standalone MCP server):
    set PYTHONPATH=%CD%
    uv run python backend/mcp/weather_mcp_server.py

TOOLS EXPOSED:
    - get_mars_weather          : Curiosity rover REMS sensor data
    - get_moon_conditions       : Derived from NOAA solar wind
    - get_space_weather         : Kp-index, solar flares, CMEs
    - get_destination_conditions: Unified dispatcher for all destinations

ENVIRONMENT:
    NASA_API_KEY in .env — free from https://api.nasa.gov (falls back to DEMO_KEY)
"""

import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NOAA_SWPC_BASE = "https://services.swpc.noaa.gov"
NASA_DONKI_BASE = "https://api.nasa.gov/DONKI"
MARS_REMS_URL = "https://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php"

mcp = FastMCP("Stellar Voyage Space Weather")


# =========================
# INTERNAL HELPERS
# =========================

def _fetch(url: str, params: dict = None) -> dict | list:
    """Safe HTTP fetch with SSL bypass for corporate networks."""
    try:
        with httpx.Client(verify=False, timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _mars_fallback() -> dict:
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


def _moon_fallback() -> dict:
    return {
        "source": "NOAA SWPC (fallback — API unavailable)",
        "solar_wind_speed_km_s": 450.0,
        "solar_wind_density_cm3": 5.0,
        "radiation_level": "moderate",
        "safe_for_eva": True,
        "eva_recommendation": "EVA conditions nominal.",
    }


def _space_weather_fallback() -> dict:
    return {
        "source": "NOAA SWPC + NASA DONKI (fallback)",
        "kp_index": 2.0,
        "geomagnetic_storm_active": False,
        "solar_flares_today": [],
        "solar_flare_alert": False,
        "radiation_belt_status": "normal",
        "safe_for_deep_space_travel": True,
    }


# =========================
# MCP TOOLS
# =========================

@mcp.tool()
def get_mars_weather() -> dict:
    """
    Get current Mars surface weather from the Curiosity Rover REMS sensor.

    Returns temperature (min/max), atmospheric pressure, UV index, storm risk,
    and EVA/surface activity safety flag.
    """
    data = _fetch(MARS_REMS_URL)

    if isinstance(data, dict) and "error" in data:
        return _mars_fallback()

    try:
        sol_keys = data.get("sol_keys", [])
        if sol_keys:
            latest_sol = sol_keys[-1]
            sol = data[latest_sol]
            min_temp = sol.get("min_temp", -73)
            max_temp = sol.get("max_temp", -5)
            pressure = float(sol.get("pressure", 815) or 815)
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
    except Exception:
        pass

    return _mars_fallback()


@mcp.tool()
def get_moon_conditions() -> dict:
    """
    Get current Moon surface conditions derived from NOAA solar wind data.

    The Moon has no atmosphere, so surface conditions are driven entirely by
    solar wind speed and particle density. Returns radiation level and EVA safety.
    """
    data = _fetch(f"{NOAA_SWPC_BASE}/products/solar-wind/plasma-7-day.json")

    if isinstance(data, dict) and "error" in data:
        return _moon_fallback()

    try:
        if isinstance(data, list) and len(data) > 1:
            latest = data[-1]  # Last data point
            density = float(latest[1]) if latest[1] and latest[1] != "" else 5.0
            speed = float(latest[2]) if latest[2] and latest[2] != "" else 450.0

            if speed > 700 or density > 20:
                radiation_level = "high"
                safe_for_eva = False
                recommendation = "EVA NOT recommended — elevated solar wind event in progress."
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
                "timestamp": latest[0] if latest[0] else datetime.utcnow().isoformat(),
                "solar_wind_speed_km_s": round(speed, 1),
                "solar_wind_density_cm3": round(density, 2),
                "radiation_level": radiation_level,
                "safe_for_eva": safe_for_eva,
                "eva_recommendation": recommendation,
            }
    except Exception:
        pass

    return _moon_fallback()


@mcp.tool()
def get_space_weather() -> dict:
    """
    Get current space weather: Kp-index, solar flares, and CME status.

    Data from NOAA SWPC planetary K-index and NASA DONKI solar flare feed.
    Relevant for all deep-space and Earth-orbit travel.
    """
    kp_data = _fetch(f"{NOAA_SWPC_BASE}/json/planetary_k_index_1m.json")
    flare_data = _fetch(
        f"{NASA_DONKI_BASE}/FLR",
        params={"startDate": datetime.utcnow().strftime("%Y-%m-%d"), "api_key": NASA_API_KEY},
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
    except Exception:
        pass

    try:
        if isinstance(flare_data, list):
            for flare in flare_data[-3:]:
                solar_flares.append({
                    "class": flare.get("classType", "unknown"),
                    "peak_time": flare.get("peakTime", ""),
                })
    except Exception:
        pass

    return {
        "source": "NOAA SWPC + NASA DONKI",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "kp_index": kp_index,
        "geomagnetic_storm_active": geomagnetic_storm,
        "solar_flares_today": solar_flares,
        "solar_flare_alert": len(solar_flares) > 0,
        "radiation_belt_status": "storm" if kp_index >= 7 else "elevated" if kp_index >= 5 else "normal",
        "safe_for_deep_space_travel": kp_index < 7,
    }


@mcp.tool()
def get_destination_conditions(destination: str) -> dict:
    """
    Get real-time environmental conditions for a specific space destination.

    Args:
        destination: One of Moon, Mars, Earth Orbit, Asteroid Belt, or Titan.

    Returns:
        Current conditions report including temperature, radiation, EVA safety,
        and any active weather alerts.
    """
    dest_lower = destination.lower()

    if "moon" in dest_lower or "lunar" in dest_lower:
        return {"destination": "Moon", **get_moon_conditions()}

    if "mars" in dest_lower:
        return {"destination": "Mars", **get_mars_weather()}

    if "orbit" in dest_lower or "iss" in dest_lower or "earth orbit" in dest_lower:
        space = get_space_weather()
        return {
            "destination": "Earth Orbit (ISS-2)",
            "source": "NOAA SWPC + NASA DONKI",
            "temperature_range_celsius": {"min": -157, "max": 121},
            "radiation_level": space["radiation_belt_status"],
            "solar_flare_alert": space["solar_flare_alert"],
            "kp_index": space["kp_index"],
            "safe_for_eva": space["kp_index"] < 5,
            "eva_recommendation": (
                "EVA conditions nominal."
                if space["kp_index"] < 5
                else "Geomagnetic storm active — EVA not recommended."
            ),
        }

    if "asteroid" in dest_lower or "psyche" in dest_lower or "belt" in dest_lower:
        space = get_space_weather()
        return {
            "destination": "Asteroid Belt (16 Psyche)",
            "source": "NOAA SWPC + NASA DONKI",
            "deep_space_radiation": space["radiation_belt_status"],
            "solar_flare_alert": space["solar_flare_alert"],
            "micrometeorite_risk": "moderate",
            "temperature_celsius": -100,
            "safe_for_mining_operations": not space["solar_flare_alert"],
        }

    if "titan" in dest_lower:
        return {
            "destination": "Titan (Saturn Moon)",
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
        "destination": destination,
        "status": "unknown",
        "message": f"No weather data available for '{destination}'.",
    }


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    mcp.run(transport="stdio")
