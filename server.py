#!/usr/bin/env python3
"""
Divine API - Indian Astrology MCP Server

Official MCP server by Divine API for Indian/Vedic Astrology services.
Provides tools for Panchang, Kundli, Matchmaking, and Festival lookups.

Setup:
    1. Get your API key and auth token from https://divineapi.com/api-keys
    2. Set environment variables: DIVINE_API_KEY and DIVINE_AUTH_TOKEN
    3. Add to your MCP client configuration (Claude Desktop, Cursor, etc.)

Documentation: https://developers.divineapi.com/indian-api
"""

import json
import os
import sys
from enum import Enum
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ──────────────────────────────────────────────
# Server Initialization
# ──────────────────────────────────────────────

mcp = FastMCP("divineapi_indian_astrology_mcp")

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

BASE_URL = "https://astroapi-3.divineapi.com"
DIVINE_API_KEY = os.environ.get("DIVINE_API_KEY", "")
DIVINE_AUTH_TOKEN = os.environ.get("DIVINE_AUTH_TOKEN", "")

if not DIVINE_API_KEY or not DIVINE_AUTH_TOKEN:
    print(
        "WARNING: DIVINE_API_KEY and DIVINE_AUTH_TOKEN environment variables are required. "
        "Get yours at https://divineapi.com/api-keys",
        file=sys.stderr,
    )

# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

VALID_GENDERS = {"male", "female"}

VALID_CHART_IDS = {
    "D1", "D2", "D3", "D4", "D5", "D7", "D8", "D9", "D10",
    "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45",
    "D60", "chalit", "sun", "moon",
}

VALID_HINDU_MONTHS = {
    "margashirsha", "paush", "magha", "phalguna", "chaitra",
    "vaishakha", "jyeshtha", "ashadha", "shravana", "bhadrapada",
    "ashwin", "kartik",
}

# ──────────────────────────────────────────────
# Shared Pydantic Models
# ──────────────────────────────────────────────


class PanchangInput(BaseModel):
    """Input for Panchang (daily calendar) API calls. Requires date, location, and timezone."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    day: str = Field(..., description="Day of the month (e.g., '24')", min_length=1, max_length=2)
    month: str = Field(..., description="Month number (e.g., '05' for May)", min_length=1, max_length=2)
    year: str = Field(..., description="Year (e.g., '2025')", min_length=4, max_length=4)
    place: str = Field(..., description="Place name (e.g., 'New Delhi')", min_length=1, max_length=200)
    lat: str = Field(..., description="Latitude of the place (e.g., '28.6139')")
    lon: str = Field(..., description="Longitude of the place (e.g., '77.2090')")
    tzone: str = Field(..., description="Timezone offset from UTC (e.g., '5.5' for IST)")
    lan: str = Field(default="en", description="Language code for response (default 'en'). Supported: en, hi, ta, te, kn, ml, bn, gu, mr, pa, or, ur")


class KundliInput(BaseModel):
    """Input for Kundli (birth chart) API calls. Requires full birth details including time."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    full_name: str = Field(..., description="Full name of the person (e.g., 'Rahul Kumar')", min_length=1, max_length=200)
    day: str = Field(..., description="Birth day (e.g., '24')", min_length=1, max_length=2)
    month: str = Field(..., description="Birth month (e.g., '05')", min_length=1, max_length=2)
    year: str = Field(..., description="Birth year (e.g., '1990')", min_length=4, max_length=4)
    hour: str = Field(..., description="Birth hour in 24h format (e.g., '14')", min_length=1, max_length=2)
    min: str = Field(..., description="Birth minute (e.g., '40')", min_length=1, max_length=2)
    sec: str = Field(default="0", description="Birth second (e.g., '0')", max_length=2)
    gender: str = Field(..., description="Gender: 'male' or 'female'")
    place: str = Field(..., description="Birth place (e.g., 'New Delhi')", min_length=1, max_length=200)
    lat: str = Field(..., description="Latitude of birth place (e.g., '28.7041')")
    lon: str = Field(..., description="Longitude of birth place (e.g., '77.1025')")
    tzone: str = Field(..., description="Timezone offset from UTC (e.g., '5.5' for IST)")
    lan: str = Field(default="en", description="Language code for response (default 'en')")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_GENDERS:
            raise ValueError(f"Gender must be 'male' or 'female', got '{v}'")
        return v


class MatchmakingInput(BaseModel):
    """Input for Kundli Matchmaking APIs. Requires birth details for both persons (P1 and P2)."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    # Person 1
    p1_full_name: str = Field(..., description="Full name of person 1 (e.g., 'Rahul Kumar')", min_length=1)
    p1_day: str = Field(..., description="Birth day of person 1 (e.g., '24')")
    p1_month: str = Field(..., description="Birth month of person 1 (e.g., '05')")
    p1_year: str = Field(..., description="Birth year of person 1 (e.g., '1998')")
    p1_hour: str = Field(..., description="Birth hour of person 1 in 24h format (e.g., '14')")
    p1_min: str = Field(..., description="Birth minute of person 1 (e.g., '40')")
    p1_sec: str = Field(default="0", description="Birth second of person 1")
    p1_gender: str = Field(..., description="Gender of person 1: 'male' or 'female'")
    p1_place: str = Field(..., description="Birth place of person 1 (e.g., 'New Delhi')")
    p1_lat: str = Field(..., description="Latitude of person 1's birth place (e.g., '28.7041')")
    p1_lon: str = Field(..., description="Longitude of person 1's birth place (e.g., '77.1025')")
    p1_tzone: str = Field(..., description="Timezone of person 1 (e.g., '5.5')")

    # Person 2
    p2_full_name: str = Field(..., description="Full name of person 2 (e.g., 'Simran Kumari')", min_length=1)
    p2_day: str = Field(..., description="Birth day of person 2 (e.g., '24')")
    p2_month: str = Field(..., description="Birth month of person 2 (e.g., '05')")
    p2_year: str = Field(..., description="Birth year of person 2 (e.g., '1998')")
    p2_hour: str = Field(..., description="Birth hour of person 2 in 24h format (e.g., '14')")
    p2_min: str = Field(..., description="Birth minute of person 2 (e.g., '40')")
    p2_sec: str = Field(default="0", description="Birth second of person 2")
    p2_gender: str = Field(..., description="Gender of person 2: 'male' or 'female'")
    p2_place: str = Field(..., description="Birth place of person 2 (e.g., 'New Delhi')")
    p2_lat: str = Field(..., description="Latitude of person 2's birth place (e.g., '28.7041')")
    p2_lon: str = Field(..., description="Longitude of person 2's birth place (e.g., '77.1025')")
    p2_tzone: str = Field(..., description="Timezone of person 2 (e.g., '5.5')")

    lan: str = Field(default="en", description="Language code for response (default 'en')")


class FestivalInput(BaseModel):
    """Input for Festival API calls. Requires year and location."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    year: str = Field(..., description="Year (e.g., '2025')", min_length=4, max_length=4)
    place: str = Field(..., description="Place name (e.g., 'New Delhi')", min_length=1, max_length=200)
    lat: str = Field(..., description="Latitude (e.g., '28.6139')")
    lon: str = Field(..., description="Longitude (e.g., '77.2090')")
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')")


# ──────────────────────────────────────────────
# Shared API Client
# ──────────────────────────────────────────────


async def _call_divine_api(endpoint: str, payload: dict) -> str:
    """Make a POST request to Divine API and return formatted JSON response.

    Args:
        endpoint: API path (e.g., '/indian-api/v1/panchang')
        payload: Form data to send (api_key is added automatically)

    Returns:
        str: JSON-formatted response string
    """
    payload["api_key"] = DIVINE_API_KEY

    # Remove None values and convert Place key if needed
    clean_payload = {k: v for k, v in payload.items() if v is not None}

    url = f"{BASE_URL}{endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {DIVINE_AUTH_TOKEN}"},
                data=clean_payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)

    except httpx.HTTPStatusError as e:
        return _handle_http_error(e)
    except httpx.TimeoutException:
        return "Error: Request timed out. The Divine API server may be slow. Please try again."
    except httpx.ConnectError:
        return "Error: Could not connect to Divine API. Please check your internet connection."
    except Exception as e:
        return f"Error: Unexpected error — {type(e).__name__}: {str(e)}"


def _handle_http_error(e: httpx.HTTPStatusError) -> str:
    """Return actionable error messages for HTTP errors."""
    status = e.response.status_code
    if status == 401:
        return (
            "Error: Authentication failed (401). "
            "Please check your DIVINE_API_KEY and DIVINE_AUTH_TOKEN environment variables. "
            "Get your credentials at https://divineapi.com/api-keys"
        )
    elif status == 403:
        return (
            "Error: Access forbidden (403). "
            "Your API plan may not include Indian Astrology APIs. "
            "Check your subscription at https://divineapi.com/pricing"
        )
    elif status == 429:
        return (
            "Error: Rate limit exceeded (429). "
            "You've exceeded 300K requests/month or are sending too many concurrent requests. "
            "Please wait and try again."
        )
    elif status == 404:
        return "Error: Endpoint not found (404). This API endpoint may not be available on your plan."
    else:
        body = ""
        try:
            body = e.response.text[:500]
        except Exception:
            pass
        return f"Error: API returned status {status}. Response: {body}"


def _panchang_payload(params: PanchangInput) -> dict:
    """Convert PanchangInput to API payload dict."""
    return {
        "day": params.day,
        "month": params.month,
        "year": params.year,
        "Place": params.place,
        "lat": params.lat,
        "lon": params.lon,
        "tzone": params.tzone,
        "lan": params.lan,
    }


def _kundli_payload(params: KundliInput) -> dict:
    """Convert KundliInput to API payload dict."""
    return {
        "full_name": params.full_name,
        "day": params.day,
        "month": params.month,
        "year": params.year,
        "hour": params.hour,
        "min": params.min,
        "sec": params.sec,
        "gender": params.gender,
        "place": params.place,
        "lat": params.lat,
        "lon": params.lon,
        "tzone": params.tzone,
        "lan": params.lan,
    }


def _matchmaking_payload(params: MatchmakingInput) -> dict:
    """Convert MatchmakingInput to API payload dict."""
    return {
        "p1_full_name": params.p1_full_name,
        "p1_day": params.p1_day,
        "p1_month": params.p1_month,
        "p1_year": params.p1_year,
        "p1_hour": params.p1_hour,
        "p1_min": params.p1_min,
        "p1_sec": params.p1_sec,
        "p1_gender": params.p1_gender,
        "p1_place": params.p1_place,
        "p1_lat": params.p1_lat,
        "p1_lon": params.p1_lon,
        "p1_tzone": params.p1_tzone,
        "p2_full_name": params.p2_full_name,
        "p2_day": params.p2_day,
        "p2_month": params.p2_month,
        "p2_year": params.p2_year,
        "p2_hour": params.p2_hour,
        "p2_min": params.p2_min,
        "p2_sec": params.p2_sec,
        "p2_gender": params.p2_gender,
        "p2_place": params.p2_place,
        "p2_lat": params.p2_lat,
        "p2_lon": params.p2_lon,
        "p2_tzone": params.p2_tzone,
        "lan": params.lan,
    }


def _festival_payload(params: FestivalInput) -> dict:
    """Convert FestivalInput to API payload dict."""
    return {
        "year": params.year,
        "Place": params.place,
        "lat": params.lat,
        "lon": params.lon,
        "tzone": params.tzone,
    }


# ══════════════════════════════════════════════
# PANCHANG TOOLS (Daily Calendar)
# ══════════════════════════════════════════════


@mcp.tool(
    name="divine_get_panchang",
    annotations={
        "title": "Get Daily Panchang",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_panchang(params: PanchangInput) -> str:
    """Get the complete daily Panchang for a given date and location.

    Returns comprehensive Vedic calendar data including tithi, nakshatra, yoga,
    karana, sunrise/sunset, moonrise/moonset, rahu kaal, and more.

    Args:
        params (PanchangInput): Date and location details:
            - day (str): Day of month (e.g., '24')
            - month (str): Month number (e.g., '05')
            - year (str): Year (e.g., '2025')
            - place (str): Location name (e.g., 'New Delhi')
            - lat (str): Latitude (e.g., '28.6139')
            - lon (str): Longitude (e.g., '77.2090')
            - tzone (str): Timezone offset (e.g., '5.5')
            - lan (str): Language code (default 'en')

    Returns:
        str: JSON with panchang details including tithi, nakshatra, yoga, karana, timings.
    """
    return await _call_divine_api("/indian-api/v1/panchang", _panchang_payload(params))


@mcp.tool(
    name="divine_get_sun_moon",
    annotations={
        "title": "Get Sun and Moon Timings",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_sun_moon(params: PanchangInput) -> str:
    """Get sun and moon rise/set timings for a given date and location.

    Returns sunrise, sunset, moonrise, moonset times and related astronomical data.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with sunrise, sunset, moonrise, moonset timings.
    """
    return await _call_divine_api("/indian-api/v1/sun-moon", _panchang_payload(params))


@mcp.tool(
    name="divine_get_nakshatra",
    annotations={
        "title": "Get Nakshatra Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_nakshatra(params: PanchangInput) -> str:
    """Get nakshatra (lunar mansion) details for a given date and location.

    Returns the current nakshatra, its start/end time, lord, and related details.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with nakshatra name, number, lord, start/end timings.
    """
    return await _call_divine_api("/indian-api/v1/nakshatra", _panchang_payload(params))


@mcp.tool(
    name="divine_get_tithi",
    annotations={
        "title": "Get Tithi Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_tithi(params: PanchangInput) -> str:
    """Get tithi (lunar day) details for a given date and location.

    Returns the current tithi, paksha (Shukla/Krishna), start/end times, and deity.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with tithi name, number, paksha, deity, start/end timings.
    """
    return await _call_divine_api("/indian-api/v1/tithi", _panchang_payload(params))


@mcp.tool(
    name="divine_get_auspicious_timings",
    annotations={
        "title": "Get Auspicious Timings (Shubh Muhurat)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_auspicious_timings(params: PanchangInput) -> str:
    """Get auspicious timings (shubh muhurat) for a given date and location.

    Returns favorable time windows for important activities like weddings,
    house-warming, travel, etc. based on Vedic astrology calculations.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with auspicious time windows (Abhijit Muhurat, Amrit Kaal, etc.).
    """
    return await _call_divine_api("/indian-api/v1/auspicious-timings", _panchang_payload(params))


@mcp.tool(
    name="divine_get_inauspicious_timings",
    annotations={
        "title": "Get Inauspicious Timings (Ashubh Kaal)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_inauspicious_timings(params: PanchangInput) -> str:
    """Get inauspicious timings for a given date and location.

    Returns unfavorable time windows like Rahu Kaal, Yamaganda, Gulika Kaal, etc.
    Useful for avoiding inauspicious activities.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with Rahu Kaal, Yamaganda, Gulika Kaal, Dur Muhurat timings.
    """
    return await _call_divine_api("/indian-api/v1/inauspicious-timings", _panchang_payload(params))


@mcp.tool(
    name="divine_get_choghadiya",
    annotations={
        "title": "Get Choghadiya",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_choghadiya(params: PanchangInput) -> str:
    """Get Choghadiya (auspicious time slots) for a given date and location.

    Choghadiya divides the day and night into multiple slots, each ruled by a
    different planet, indicating good/bad periods for various activities.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with day and night Choghadiya slots with their qualities.
    """
    return await _call_divine_api("/indian-api/v1/choghadiya", _panchang_payload(params))


@mcp.tool(
    name="divine_get_planet_transit",
    annotations={
        "title": "Get Planet Transit (Grah Gochar)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_planet_transit(params: PanchangInput) -> str:
    """Get current planetary transit (Grah Gochar) data for a given date and location.

    Returns which planets are transiting through which signs/nakshatras,
    useful for transit-based predictions.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with planetary transit positions and details.
    """
    return await _call_divine_api("/indian-api/v1/grah-gochar", _panchang_payload(params))


@mcp.tool(
    name="divine_get_chandrashtama",
    annotations={
        "title": "Get Chandrashtama",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_chandrashtama(params: PanchangInput) -> str:
    """Get Chandrashtama details for a given date and location.

    Chandrashtama is the period when Moon transits through the 8th house
    from one's birth Moon sign — considered inauspicious for new ventures.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with Chandrashtama timings for each moon sign.
    """
    return await _call_divine_api("/indian-api/v1/chandrashtama", _panchang_payload(params))


# ══════════════════════════════════════════════
# KUNDLI TOOLS (Birth Chart)
# ══════════════════════════════════════════════


@mcp.tool(
    name="divine_get_basic_astro_details",
    annotations={
        "title": "Get Basic Astrological Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_basic_astro_details(params: KundliInput) -> str:
    """Get basic astrological details for a person based on their birth data.

    Returns fundamental Vedic astrology parameters: tithi, nakshatra, rashi (moon sign),
    sun sign, yoga, karana, varna, vashya, yoni, gana, nadi, and more.
    This is the foundation for all Kundli-based analysis.

    Args:
        params (KundliInput): Full birth details including name, date, time, place, and coordinates.

    Returns:
        str: JSON with tithi, nakshatra, rashi, sunsign, moonsign, yoga, karana,
             varna, vashya, yoni, gana, nadi, ayanamsha, and more.
    """
    return await _call_divine_api("/indian-api/v3/basic-astro-details", _kundli_payload(params))


@mcp.tool(
    name="divine_get_planetary_positions",
    annotations={
        "title": "Get Planetary Positions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_planetary_positions(params: KundliInput) -> str:
    """Get planetary positions in the birth chart (Kundli).

    Returns positions of all 9 Vedic planets (Sun, Moon, Mars, Mercury, Jupiter,
    Venus, Saturn, Rahu, Ketu) with their sign, degree, nakshatra, and house placement.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with each planet's sign, degree, nakshatra, house, retrograde status, etc.
    """
    return await _call_divine_api("/indian-api/v1/planetary-positions", _kundli_payload(params))


@mcp.tool(
    name="divine_get_horoscope_chart",
    annotations={
        "title": "Get Horoscope Chart (Kundli Chart)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_horoscope_chart(
    chart_id: str = Field(..., description="Chart type: D1 (Lagna), D2 (Hora), D3 (Drekkana), D9 (Navamsha), D10 (Dashamsha), D12 (Dwadashamsha), chalit, sun, moon, etc."),
    full_name: str = Field(..., description="Full name of the person"),
    day: str = Field(..., description="Birth day (e.g., '24')"),
    month: str = Field(..., description="Birth month (e.g., '05')"),
    year: str = Field(..., description="Birth year (e.g., '1990')"),
    hour: str = Field(..., description="Birth hour in 24h format (e.g., '14')"),
    min: str = Field(..., description="Birth minute (e.g., '40')"),
    sec: str = Field(default="0", description="Birth second"),
    gender: str = Field(..., description="Gender: 'male' or 'female'"),
    place: str = Field(..., description="Birth place (e.g., 'New Delhi')"),
    lat: str = Field(..., description="Latitude (e.g., '28.7041')"),
    lon: str = Field(..., description="Longitude (e.g., '77.1025')"),
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')"),
    lan: str = Field(default="en", description="Language code"),
) -> str:
    """Generate a Vedic horoscope chart (Kundli diagram) as SVG and base64 image.

    Supports multiple divisional charts: D1 (Lagna/Rashi), D2 (Hora), D3 (Drekkana),
    D9 (Navamsha), D10 (Dashamsha), chalit chart, sun chart, moon chart, and more.

    Args:
        chart_id: Chart type ID. Common values: 'D1' (main birth chart), 'D9' (Navamsha),
                  'D10' (career), 'chalit', 'sun', 'moon'.
        full_name: Person's full name.
        day, month, year: Birth date.
        hour, min, sec: Birth time in 24h format.
        gender: 'male' or 'female'.
        place: Birth place name.
        lat, lon: Birth place coordinates.
        tzone: Timezone offset from UTC.
        lan: Language code (default 'en').

    Returns:
        str: JSON with SVG code, raw chart data, and base64 encoded image.
    """
    chart_id_upper = chart_id.upper() if chart_id.lower() not in ("chalit", "sun", "moon") else chart_id.lower()

    payload = {
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    }
    return await _call_divine_api(f"/indian-api/v1/horoscope-chart/{chart_id_upper}", payload)


@mcp.tool(
    name="divine_get_vimshottari_dasha",
    annotations={
        "title": "Get Vimshottari Dasha",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_vimshottari_dasha(params: KundliInput) -> str:
    """Get Vimshottari Dasha periods for a person's birth chart.

    Vimshottari is the most widely used dasha system in Vedic astrology.
    Returns the sequence of Maha Dasha, Antar Dasha periods with exact dates,
    showing which planetary period the person is currently in.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with complete Maha Dasha and Antar Dasha periods with start/end dates.
    """
    return await _call_divine_api("/indian-api/v1/vimshottari-dasha", _kundli_payload(params))


@mcp.tool(
    name="divine_get_manglik_dosha",
    annotations={
        "title": "Check Manglik Dosha",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_manglik_dosha(params: KundliInput) -> str:
    """Check for Manglik Dosha (Mangal Dosha / Kuja Dosha) in the birth chart.

    Manglik Dosha is caused by Mars placement in certain houses and is important
    for marriage compatibility analysis. Returns whether the person is Manglik
    and the severity/cancellation factors.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with Manglik status, percentage, and cancellation details.
    """
    return await _call_divine_api("/indian-api/v1/manglik-dosha", _kundli_payload(params))


@mcp.tool(
    name="divine_get_kaal_sarpa_dosha",
    annotations={
        "title": "Check Kaal Sarpa Dosha",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_kaal_sarpa_dosha(params: KundliInput) -> str:
    """Check for Kaal Sarpa Dosha in the birth chart.

    Kaal Sarpa Dosha occurs when all planets are hemmed between Rahu and Ketu.
    Returns the type of Kaal Sarpa Yoga and its effects.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with Kaal Sarpa Dosha presence, type, and details.
    """
    return await _call_divine_api("/indian-api/v1/kaal-sarpa-dosha", _kundli_payload(params))


@mcp.tool(
    name="divine_get_sadhe_sati",
    annotations={
        "title": "Check Sadhe Sati Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_sadhe_sati(params: KundliInput) -> str:
    """Check Sadhe Sati (Saturn transit) status for the person.

    Sadhe Sati is the 7.5-year period of Saturn transiting through the 12th,
    1st, and 2nd houses from Moon sign. Returns current phase and dates.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with Sadhe Sati status, current phase, and period dates.
    """
    return await _call_divine_api("/indian-api/v1/sadhe-sati", _kundli_payload(params))


@mcp.tool(
    name="divine_get_gemstone_suggestions",
    annotations={
        "title": "Get Gemstone Suggestions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_gemstone_suggestions(params: KundliInput) -> str:
    """Get gemstone recommendations based on the birth chart.

    Returns suggested gemstones based on planetary positions, including the
    primary gemstone, alternative stones, and wearing instructions.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with recommended gemstones, metals, and wearing instructions.
    """
    return await _call_divine_api("/indian-api/v1/gemstone-suggestions", _kundli_payload(params))


@mcp.tool(
    name="divine_get_yogas",
    annotations={
        "title": "Get Yogas in Birth Chart",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_yogas(params: KundliInput) -> str:
    """Get all yogas (planetary combinations) present in the birth chart.

    Yogas are special planetary combinations that indicate specific life outcomes —
    wealth (Dhana Yoga), fame (Raja Yoga), spiritual growth, etc.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with list of yogas found, their descriptions and effects.
    """
    return await _call_divine_api("/indian-api/v1/yogas", _kundli_payload(params))


@mcp.tool(
    name="divine_get_ascendant_report",
    annotations={
        "title": "Get Ascendant (Lagna) Report",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_ascendant_report(params: KundliInput) -> str:
    """Get a detailed report based on the ascendant (Lagna) sign.

    Returns personality traits, physical characteristics, and life tendencies
    based on the rising sign at the time of birth.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with ascendant sign details, personality report, and predictions.
    """
    return await _call_divine_api("/indian-api/v1/ascendant-report", _kundli_payload(params))


@mcp.tool(
    name="divine_get_pitra_dosha",
    annotations={
        "title": "Check Pitra Dosha",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_pitra_dosha(params: KundliInput) -> str:
    """Check for Pitra Dosha (ancestral affliction) in the birth chart.

    Pitra Dosha indicates karmic debts from ancestors and can affect family
    harmony, progeny, and prosperity. Returns remedial measures.

    Args:
        params (KundliInput): Full birth details.

    Returns:
        str: JSON with Pitra Dosha presence, effects, and remedies.
    """
    return await _call_divine_api("/indian-api/v1/pitra-dosha", _kundli_payload(params))


# ══════════════════════════════════════════════
# MATCHMAKING TOOLS (Kundli Milan)
# ══════════════════════════════════════════════


@mcp.tool(
    name="divine_get_ashtakoot_milan",
    annotations={
        "title": "Ashtakoot Milan (8-Point Matching)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_ashtakoot_milan(params: MatchmakingInput) -> str:
    """Perform Ashtakoot Milan (8-point compatibility matching) for two people.

    The most popular Kundli matching method in North India. Evaluates compatibility
    across 8 categories (Gunas): Varna, Vashya, Tara, Yoni, Graha Maitri,
    Gana, Bhakoot, and Nadi — with a maximum score of 36.

    Args:
        params (MatchmakingInput): Birth details of both person 1 and person 2.

    Returns:
        str: JSON with total score (out of 36), individual category scores, and compatibility verdict.
    """
    return await _call_divine_api("/indian-api/v1/ashtakoot-milan", _matchmaking_payload(params))


@mcp.tool(
    name="divine_get_dashakoot_milan",
    annotations={
        "title": "Dashakoot Milan (10-Point Matching)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_dashakoot_milan(params: MatchmakingInput) -> str:
    """Perform Dashakoot Milan (10-point compatibility matching) for two people.

    Popular in South India, evaluates compatibility across 10 categories
    with a maximum score of 36. More comprehensive than Ashtakoot.

    Args:
        params (MatchmakingInput): Birth details of both person 1 and person 2.

    Returns:
        str: JSON with total score, individual category scores, and compatibility analysis.
    """
    return await _call_divine_api("/indian-api/v1/dashakoot-milan", _matchmaking_payload(params))


@mcp.tool(
    name="divine_get_matching_manglik",
    annotations={
        "title": "Matching Manglik Dosha Check",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_matching_manglik(params: MatchmakingInput) -> str:
    """Check Manglik Dosha for both people in a matchmaking context.

    Compares the Manglik status of both individuals to assess marriage
    compatibility. Important when either person is Manglik.

    Args:
        params (MatchmakingInput): Birth details of both person 1 and person 2.

    Returns:
        str: JSON with Manglik status for both persons and compatibility assessment.
    """
    return await _call_divine_api("/indian-api/v1/matching/manglik-dosha", _matchmaking_payload(params))


@mcp.tool(
    name="divine_get_matching_basic_astro",
    annotations={
        "title": "Matching Basic Astro Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_matching_basic_astro(params: MatchmakingInput) -> str:
    """Get basic astrological details for both persons in a matchmaking context.

    Returns fundamental astrological parameters for both P1 and P2 side by side,
    including rashi, nakshatra, tithi, gana, nadi, varna, etc.

    Args:
        params (MatchmakingInput): Birth details of both person 1 and person 2.

    Returns:
        str: JSON with basic astro details for both persons for comparison.
    """
    return await _call_divine_api("/indian-api/v3/matching/basic-astro-details", _matchmaking_payload(params))


# ══════════════════════════════════════════════
# FESTIVAL TOOLS
# ══════════════════════════════════════════════


@mcp.tool(
    name="divine_get_festivals_by_month",
    annotations={
        "title": "Get Hindu Festivals by Month",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_festivals_by_month(
    hindu_month: str = Field(..., description="Hindu calendar month name: margashirsha, paush, magha, phalguna, chaitra, vaishakha, jyeshtha, ashadha, shravana, bhadrapada, ashwin, kartik"),
    year: str = Field(..., description="Year (e.g., '2025')"),
    place: str = Field(..., description="Place name (e.g., 'New Delhi')"),
    lat: str = Field(..., description="Latitude (e.g., '28.6139')"),
    lon: str = Field(..., description="Longitude (e.g., '77.2090')"),
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')"),
) -> str:
    """Get all Hindu festivals for a specific Hindu calendar month.

    Returns festival dates and details for any of the 12 Hindu months:
    Margashirsha, Paush, Magha, Phalguna, Chaitra, Vaishakha, Jyeshtha,
    Ashadha, Shravana, Bhadrapada, Ashwin, Kartik.

    Args:
        hindu_month: Hindu month name (lowercase).
        year: Year.
        place: Location name.
        lat, lon: Coordinates.
        tzone: Timezone offset.

    Returns:
        str: JSON with list of festivals, their dates, and details for that month.
    """
    month_lower = hindu_month.lower().strip()
    if month_lower not in VALID_HINDU_MONTHS:
        return f"Error: Invalid Hindu month '{hindu_month}'. Must be one of: {', '.join(sorted(VALID_HINDU_MONTHS))}"

    # Map month names to API endpoint names
    endpoint_map = {
        "margashirsha": "margashirsh-festivals",
        "paush": "paush-festivals",
        "magha": "magha-festivals",
        "phalguna": "phalguna-festivals",
        "chaitra": "chaitra-festivals",
        "vaishakha": "vaishakha-festivals",
        "jyeshtha": "jyeshtha-festivals",
        "ashadha": "ashadha-festivals",
        "shravana": "shravana-festivals",
        "bhadrapada": "bhadrapada-festivals",
        "ashwin": "ashwin-festivals",
        "kartik": "kartik-festivals",
    }

    payload = {
        "year": year,
        "Place": place,
        "lat": lat,
        "lon": lon,
        "tzone": tzone,
    }
    return await _call_divine_api(f"/indian-api/v1/{endpoint_map[month_lower]}", payload)


@mcp.tool(
    name="divine_get_festivals_by_date",
    annotations={
        "title": "Get Festivals by Date",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_festivals_by_date(params: PanchangInput) -> str:
    """Get festivals falling on a specific date.

    Returns all Hindu festivals and observances for a given date and location.

    Args:
        params (PanchangInput): Date and location details.

    Returns:
        str: JSON with festival names and details for the given date.
    """
    return await _call_divine_api("/indian-api/v1/date-specific-festivals", _panchang_payload(params))


@mcp.tool(
    name="divine_get_english_calendar_festivals",
    annotations={
        "title": "Get Festivals by English Month",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def divine_get_english_calendar_festivals(
    month: str = Field(..., description="English month number (e.g., '01' for January, '12' for December)"),
    year: str = Field(..., description="Year (e.g., '2025')"),
    place: str = Field(..., description="Place name (e.g., 'New Delhi')"),
    lat: str = Field(..., description="Latitude (e.g., '28.6139')"),
    lon: str = Field(..., description="Longitude (e.g., '77.2090')"),
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')"),
) -> str:
    """Get all Hindu festivals for a specific English calendar month.

    Returns festivals falling within a given month of the Gregorian calendar.

    Args:
        month: English month number ('01' to '12').
        year: Year.
        place: Location name.
        lat, lon: Coordinates.
        tzone: Timezone offset.

    Returns:
        str: JSON with festivals and their dates for that English calendar month.
    """
    payload = {
        "month": month,
        "year": year,
        "Place": place,
        "lat": lat,
        "lon": lon,
        "tzone": tzone,
    }
    return await _call_divine_api("/indian-api/v1/english-calendar-festivals", payload)


# ──────────────────────────────────────────────
# Server Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
