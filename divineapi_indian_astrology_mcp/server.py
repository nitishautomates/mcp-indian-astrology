#!/usr/bin/env python3
"""
Divine API - Indian Astrology MCP Server

Official MCP server by Divine API for Indian/Vedic Astrology services.
Provides tools for Panchang, Kundli, Matchmaking, Dasha, KP, Jaimini,
Ashtakvarga, Transits, Festivals, and Monthly Lists.

Setup:
    1. Get your API key and auth token from https://divineapi.com/api-keys
    2. Set environment variables: DIVINE_API_KEY and DIVINE_AUTH_TOKEN
    3. Add to your MCP client configuration (Claude Desktop, Cursor, etc.)

Documentation: https://developers.divineapi.com/indian-api
"""

import json
import os
import sys

import httpx
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ──────────────────────────────────────────────
# Server Initialization
# ──────────────────────────────────────────────

_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")

mcp = FastMCP(
    "divineapi_indian_astrology_mcp",
    stateless_http=(_TRANSPORT == "http"),
)

# ──────────────────────────────────────────────
# Configuration — Base URLs for API hosts
# ──────────────────────────────────────────────

API_HOST_1 = "https://astroapi-1.divineapi.com"  # Panchang basics
API_HOST_2 = "https://astroapi-2.divineapi.com"  # Choghadiya, calendars, sun/moon
API_HOST_3 = "https://astroapi-3.divineapi.com"  # Kundli, matching, festivals, dasha
API_HOST_8 = "https://astroapi-8.divineapi.com"  # Monthly lists

DIVINE_API_KEY = os.environ.get("DIVINE_API_KEY", "")
DIVINE_AUTH_TOKEN = os.environ.get("DIVINE_AUTH_TOKEN", "")

if _TRANSPORT == "stdio" and (not DIVINE_API_KEY or not DIVINE_AUTH_TOKEN):
    print(
        "WARNING: DIVINE_API_KEY and DIVINE_AUTH_TOKEN environment variables are required. "
        "Get yours at https://divineapi.com/api-keys",
        file=sys.stderr,
    )


def _get_credentials(ctx: Context | None = None) -> tuple[str, str]:
    """Extract Divine API credentials from request headers or env vars."""
    api_key = DIVINE_API_KEY
    auth_token = DIVINE_AUTH_TOKEN
    if ctx:
        try:
            headers = ctx.request_context.get("headers", {}) if ctx.request_context else {}
            api_key = headers.get("x-divine-api-key", api_key)
            auth_token = headers.get("x-divine-auth-token", auth_token)
        except Exception:
            pass
    if not api_key or not auth_token:
        raise ValueError(
            "Divine API credentials required. "
            "Set X-Divine-Api-Key and X-Divine-Auth-Token headers, "
            "or DIVINE_API_KEY and DIVINE_AUTH_TOKEN environment variables. "
            "Get yours at https://divineapi.com/api-keys"
        )
    return api_key, auth_token

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

VALID_GENDERS = {"male", "female"}

VALID_CHART_IDS = {
    "D1", "D2", "D3", "D4", "D5", "D7", "D8", "D9", "D10",
    "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45",
    "D60", "chalit", "sun", "moon",
}

VALID_HINDU_MONTHS = {
    "margashirsha", "pausha", "magha", "phalguna", "chaitra",
    "vaishakha", "jyeshtha", "ashadha", "shravana", "bhadrapada",
    "ashvina", "kartika",
}

VALID_PLANETS = {
    "sun", "moon", "mars", "mercury", "jupiter",
    "venus", "saturn", "rahu", "ketu",
}

TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}

# ──────────────────────────────────────────────
# Pydantic Models
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
    p1_full_name: str = Field(..., description="Full name of person 1", min_length=1)
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
    p2_full_name: str = Field(..., description="Full name of person 2", min_length=1)
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


async def _call_divine_api(
    endpoint: str,
    payload: dict,
    base_url: str = API_HOST_3,
    api_key: str | None = None,
    auth_token: str | None = None,
) -> str:
    """Make a POST request to Divine API and return formatted JSON response."""
    payload["api_key"] = api_key or DIVINE_API_KEY
    clean_payload = {k: v for k, v in payload.items() if v is not None}
    url = f"{base_url}{endpoint}"
    bearer = auth_token or DIVINE_AUTH_TOKEN

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {bearer}"},
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
        return f"Error: Unexpected error - {type(e).__name__}: {str(e)}"


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
            "You've exceeded your request limit or are sending too many concurrent requests. "
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
    return {
        "year": params.year,
        "Place": params.place,
        "lat": params.lat,
        "lon": params.lon,
        "tzone": params.tzone,
    }


def _kundli_params_payload(**kwargs) -> dict:
    """Build kundli payload from individual keyword arguments."""
    return {
        "full_name": kwargs["full_name"], "day": kwargs["day"], "month": kwargs["month"],
        "year": kwargs["year"], "hour": kwargs["hour"], "min": kwargs["min"],
        "sec": kwargs.get("sec", "0"), "gender": kwargs["gender"],
        "place": kwargs["place"], "lat": kwargs["lat"], "lon": kwargs["lon"],
        "tzone": kwargs["tzone"], "lan": kwargs.get("lan", "en"),
    }


# ══════════════════════════════════════════════
# PANCHANG TOOLS — astroapi-1.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_panchang", annotations=TOOL_ANNOTATIONS)
async def divine_get_panchang(params: PanchangInput, ctx: Context) -> str:
    """Get the complete daily Panchang for a given date and location.

    Returns comprehensive Vedic calendar data including tithi, nakshatra, yoga,
    karana, sunrise/sunset, moonrise/moonset, rahu kaal, and more.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-panchang", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_tithi", annotations=TOOL_ANNOTATIONS)
async def divine_get_tithi(params: PanchangInput, ctx: Context) -> str:
    """Get tithi (lunar day) details for a given date and location.

    Returns the current tithi, paksha (Shukla/Krishna), start/end times, and deity.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-tithi", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_nakshatra", annotations=TOOL_ANNOTATIONS)
async def divine_get_nakshatra(params: PanchangInput, ctx: Context) -> str:
    """Get nakshatra (lunar mansion) details for a given date and location.

    Returns the current nakshatra, its start/end time, lord, and related details.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-nakshatra", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_karana", annotations=TOOL_ANNOTATIONS)
async def divine_get_karana(params: PanchangInput, ctx: Context) -> str:
    """Get karana details for a given date and location.

    Karana is half of a tithi. There are 11 karanas in Vedic astrology,
    each with specific qualities for timing activities.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-karana", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_surya_nakshatra", annotations=TOOL_ANNOTATIONS)
async def divine_get_surya_nakshatra(params: PanchangInput, ctx: Context) -> str:
    """Get Surya (Sun) Nakshatra details for a given date and location.

    Returns the nakshatra occupied by the Sun, useful for solar-based
    astrological calculations and rashi sandhi analysis.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-surya-nakshatra", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_yoga_panchang", annotations=TOOL_ANNOTATIONS)
async def divine_get_yoga_panchang(params: PanchangInput, ctx: Context) -> str:
    """Get yoga (Sun-Moon angular relationship) for a given date and location.

    Returns the current yoga from the 27 Nitya Yogas, each indicating
    auspicious or inauspicious qualities for the day.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-yoga", _panchang_payload(params), API_HOST_1, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# PANCHANG EXTENDED — astroapi-2.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_choghadiya", annotations=TOOL_ANNOTATIONS)
async def divine_get_choghadiya(params: PanchangInput, ctx: Context) -> str:
    """Get Choghadiya (auspicious time slots) for a given date and location.

    Divides the day and night into multiple slots, each ruled by a different
    planet, indicating good/bad periods for various activities.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-choghadiya", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_nivas_and_shool", annotations=TOOL_ANNOTATIONS)
async def divine_get_nivas_and_shool(params: PanchangInput, ctx: Context) -> str:
    """Get Nivas and Shool (directional inauspicious timings) for a date and location.

    Shool indicates inauspicious directions for travel on specific days.
    Nivas shows the resting place of certain deities.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-nivas-and-shool", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_ritu_and_anaya", annotations=TOOL_ANNOTATIONS)
async def divine_get_ritu_and_anaya(params: PanchangInput, ctx: Context) -> str:
    """Get Ritu (season) and Anaya details for a given date and location.

    Returns the current Hindu season (Vasant, Grishma, Varsha, Sharad,
    Hemant, Shishir) and related calendar information.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-ritu-and-anaya", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_samvath", annotations=TOOL_ANNOTATIONS)
async def divine_get_samvath(params: PanchangInput, ctx: Context) -> str:
    """Get Samvath (Hindu calendar year) details for a given date and location.

    Returns the current Vikram Samvat, Shaka Samvat year names and numbers.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-samvath", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_chandrabalam_and_tarabalam", annotations=TOOL_ANNOTATIONS)
async def divine_get_chandrabalam_and_tarabalam(params: PanchangInput, ctx: Context) -> str:
    """Get Chandrabalam and Tarabalam for a given date and location.

    Chandrabalam is Moon's strength for each rashi. Tarabalam is the
    auspiciousness based on birth nakshatra. Both important for muhurta selection.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-chandrabalam-and-tarabalam", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_other_calendars_and_epoch", annotations=TOOL_ANNOTATIONS)
async def divine_get_other_calendars_and_epoch(params: PanchangInput, ctx: Context) -> str:
    """Get dates in other calendar systems and epoch values for a given date.

    Returns conversions to Vikram Samvat, Shaka Samvat, Kali Yuga,
    and Julian day numbers.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-other-calendars-and-epoch", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_sun_moon", annotations=TOOL_ANNOTATIONS)
async def divine_get_sun_moon(params: PanchangInput, ctx: Context) -> str:
    """Get sun and moon rise/set timings for a given date and location.

    Returns sunrise, sunset, moonrise, moonset times and related astronomical data.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/find-sun-and-moon", _panchang_payload(params), API_HOST_2, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# TIMINGS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_auspicious_timings", annotations=TOOL_ANNOTATIONS)
async def divine_get_auspicious_timings(params: PanchangInput, ctx: Context) -> str:
    """Get auspicious timings (shubh muhurat) for a given date and location.

    Returns favorable time windows for important activities like weddings,
    house-warming, travel, etc. (Abhijit Muhurat, Amrit Kaal, etc.).
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/auspicious-timings", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_inauspicious_timings", annotations=TOOL_ANNOTATIONS)
async def divine_get_inauspicious_timings(params: PanchangInput, ctx: Context) -> str:
    """Get inauspicious timings for a given date and location.

    Returns unfavorable time windows: Rahu Kaal, Yamaganda, Gulika Kaal,
    Dur Muhurat. Useful for avoiding inauspicious activities.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/inauspicious-timings", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# KUNDLI BASICS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_basic_astro_details", annotations=TOOL_ANNOTATIONS)
async def divine_get_basic_astro_details(params: KundliInput, ctx: Context) -> str:
    """Get basic astrological details for a person based on their birth data.

    Returns tithi, nakshatra, rashi, sun sign, moon sign, yoga, karana,
    varna, vashya, yoni, gana, nadi, ayanamsha, and more.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v3/basic-astro-details", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_planetary_positions", annotations=TOOL_ANNOTATIONS)
async def divine_get_planetary_positions(params: KundliInput, ctx: Context) -> str:
    """Get planetary positions in the birth chart (Kundli).

    Returns positions of all 9 Vedic planets (Sun, Moon, Mars, Mercury, Jupiter,
    Venus, Saturn, Rahu, Ketu) with sign, degree, nakshatra, and house placement.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/planetary-positions", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_horoscope_chart", annotations=TOOL_ANNOTATIONS)
async def divine_get_horoscope_chart(
    chart_id: str = Field(..., description="Chart type: D1 (Lagna), D2 (Hora), D3 (Drekkana), D9 (Navamsha), D10 (Dashamsha), chalit, sun, moon, etc."),
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
    ctx: Context = None,
) -> str:
    """Generate a Vedic horoscope chart (Kundli diagram) as SVG and image.

    Supports divisional charts: D1 (Lagna/Rashi), D2 (Hora), D3 (Drekkana),
    D9 (Navamsha), D10 (Dashamsha), chalit, sun, moon, and more.
    """
    chart_id_upper = chart_id.upper() if chart_id.lower() not in ("chalit", "sun", "moon") else chart_id.lower()
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v1/horoscope-chart/{chart_id_upper}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_bhava_kundli", annotations=TOOL_ANNOTATIONS)
async def divine_get_bhava_kundli(
    chart_id: str = Field(..., description="Chart type: D1, D2, D3, D9, D10, chalit, sun, moon, etc."),
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
    ctx: Context = None,
) -> str:
    """Get Bhava Kundli (house-based chart) for a given chart type.

    Unlike the rashi chart which shows sign placements, the Bhava chart
    shows exact house cusps and planetary positions within houses.
    """
    chart_id_upper = chart_id.upper() if chart_id.lower() not in ("chalit", "sun", "moon") else chart_id.lower()
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v1/bhava-kundli/{chart_id_upper}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_planet_analysis", annotations=TOOL_ANNOTATIONS)
async def divine_get_planet_analysis(params: KundliInput, ctx: Context) -> str:
    """Get detailed analysis of all planets in the birth chart.

    Returns interpretation of each planet's placement including house lordship,
    aspects, conjunctions, strengths, and effects.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/planet-analysis", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_ascendant_report", annotations=TOOL_ANNOTATIONS)
async def divine_get_ascendant_report(params: KundliInput, ctx: Context) -> str:
    """Get a detailed report based on the ascendant (Lagna) sign.

    Returns personality traits, physical characteristics, and life tendencies
    based on the rising sign at the time of birth.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/ascendant-report", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_uday_lagna", annotations=TOOL_ANNOTATIONS)
async def divine_get_uday_lagna(params: KundliInput, ctx: Context) -> str:
    """Get Uday Lagna (rising sign) details for the birth chart.

    Returns the exact degree, sign, and nakshatra of the ascendant
    at the moment of birth with precise calculations.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/uday-lagna", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_chandramasa", annotations=TOOL_ANNOTATIONS)
async def divine_get_chandramasa(params: PanchangInput, ctx: Context) -> str:
    """Get Chandramasa (Hindu lunar month) details for a given date and location.

    Returns the current Hindu lunar month name, Purnimant/Amant system,
    and the start/end dates of the lunar month.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/chandramasa", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_chandrashtama", annotations=TOOL_ANNOTATIONS)
async def divine_get_chandrashtama(params: PanchangInput, ctx: Context) -> str:
    """Get Chandrashtama details for a given date and location.

    Chandrashtama is when Moon transits through the 8th house from one's
    birth Moon sign, considered inauspicious for new ventures.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/chandrashtama", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# DOSHAS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_manglik_dosha", annotations=TOOL_ANNOTATIONS)
async def divine_get_manglik_dosha(params: KundliInput, ctx: Context) -> str:
    """Check for Manglik Dosha (Mangal Dosha / Kuja Dosha) in the birth chart.

    Important for marriage compatibility. Returns Manglik status,
    percentage, and cancellation factors.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/manglik-dosha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kaal_sarpa_yoga", annotations=TOOL_ANNOTATIONS)
async def divine_get_kaal_sarpa_yoga(params: KundliInput, ctx: Context) -> str:
    """Check for Kaal Sarpa Yoga in the birth chart.

    Occurs when all planets are hemmed between Rahu and Ketu.
    Returns the type of Kaal Sarpa Yoga and its effects.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kaal-sarpa-yoga", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_pitra_dosha", annotations=TOOL_ANNOTATIONS)
async def divine_get_pitra_dosha(params: KundliInput, ctx: Context) -> str:
    """Check for Pitra Dosha (ancestral affliction) in the birth chart.

    Indicates karmic debts from ancestors affecting family harmony,
    progeny, and prosperity. Returns remedial measures.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/pitra-dosha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_sadhe_sati", annotations=TOOL_ANNOTATIONS)
async def divine_get_sadhe_sati(params: KundliInput, ctx: Context) -> str:
    """Check Sadhe Sati (Saturn transit) status for the person.

    The 7.5-year period of Saturn transiting through the 12th, 1st, and 2nd
    houses from Moon sign. Returns current phase and dates.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v3/sadhe-sati", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# DASHA SYSTEMS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_vimshottari_dasha", annotations=TOOL_ANNOTATIONS)
async def divine_get_vimshottari_dasha(params: KundliInput, ctx: Context) -> str:
    """Get Vimshottari Dasha periods for a birth chart.

    The most widely used dasha system. Returns Maha Dasha and Antar Dasha
    periods with exact start/end dates.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/vimshottari-dasha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_maha_dasha_analysis", annotations=TOOL_ANNOTATIONS)
async def divine_get_maha_dasha_analysis(params: KundliInput, ctx: Context) -> str:
    """Get detailed Maha Dasha analysis for a birth chart.

    Returns interpretation and predictions for each Maha Dasha period
    including effects on career, health, relationships, and finances.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/maha-dasha-analysis", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_antar_dasha_analysis", annotations=TOOL_ANNOTATIONS)
async def divine_get_antar_dasha_analysis(params: KundliInput, ctx: Context) -> str:
    """Get detailed Antar Dasha (sub-period) analysis for a birth chart.

    Returns interpretation for each Antar Dasha within the current
    Maha Dasha, providing more granular timing predictions.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/antar-dasha-analysis", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_pratyantar_dasha_analysis", annotations=TOOL_ANNOTATIONS)
async def divine_get_pratyantar_dasha_analysis(params: KundliInput, ctx: Context) -> str:
    """Get Pratyantar Dasha (sub-sub-period) analysis for a birth chart.

    The most granular level of Vimshottari Dasha, useful for precise
    event timing and short-term predictions.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/pratyantar-dasha-analysis", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_yogini_dasha", annotations=TOOL_ANNOTATIONS)
async def divine_get_yogini_dasha(params: KundliInput, ctx: Context) -> str:
    """Get Yogini Dasha periods for a birth chart.

    An alternative dasha system based on 8 Yoginis with a 36-year cycle.
    Popular for quick predictions and event timing.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/yogini-dasha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kaal_chakra_dasha", annotations=TOOL_ANNOTATIONS)
async def divine_get_kaal_chakra_dasha(params: KundliInput, ctx: Context) -> str:
    """Get Kaal Chakra Dasha periods for a birth chart.

    A nakshatra-based dasha system described by Parashar. Each nakshatra
    pada maps to specific signs creating unique dasha sequences.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kaal-chakra-dasha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# YOGAS & STRENGTHS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_yogas", annotations=TOOL_ANNOTATIONS)
async def divine_get_yogas(params: KundliInput, ctx: Context) -> str:
    """Get all yogas (planetary combinations) present in the birth chart.

    Returns special planetary combinations indicating specific life outcomes:
    wealth (Dhana Yoga), fame (Raja Yoga), spiritual growth, etc.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/yogas", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_nav_pancham_yoga", annotations=TOOL_ANNOTATIONS)
async def divine_get_nav_pancham_yoga(params: KundliInput, ctx: Context) -> str:
    """Get Nav Pancham Yoga analysis for a birth chart.

    Analyzes the 5th and 9th house relationship (trine houses) indicating
    fortune, past-life merit, children, and higher education.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/nav-pancham-yoga", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_shadbala", annotations=TOOL_ANNOTATIONS)
async def divine_get_shadbala(params: KundliInput, ctx: Context) -> str:
    """Get Shadbala (six-fold planetary strength) for a birth chart.

    Calculates six types of strength: Sthana Bala, Dig Bala, Kala Bala,
    Chesta Bala, Naisargika Bala, and Drik Bala for each planet.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/shadbala", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_composite_friendship", annotations=TOOL_ANNOTATIONS)
async def divine_get_composite_friendship(params: KundliInput, ctx: Context) -> str:
    """Get composite (Panchda) friendship table for all planets.

    Shows natural, temporal, and composite friendship/enmity relationships
    between all planet pairs in the birth chart.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/composite-friendship", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_ghata_chakra", annotations=TOOL_ANNOTATIONS)
async def divine_get_ghata_chakra(params: KundliInput, ctx: Context) -> str:
    """Get Ghata Chakra (adverse combinations) for a birth chart.

    Returns the inauspicious day, tithi, nakshatra, yoga, karana, and
    lagna specific to the person's birth nakshatra.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/ghata-chakra", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_sudarshana_chakra", annotations=TOOL_ANNOTATIONS)
async def divine_get_sudarshana_chakra(params: KundliInput, ctx: Context) -> str:
    """Get Sudarshana Chakra for a birth chart.

    Overlays Lagna, Moon, and Sun charts concentrically for comprehensive
    life prediction year by year.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/sudarshana-chakra", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_panchak_rahita", annotations=TOOL_ANNOTATIONS)
async def divine_get_panchak_rahita(params: PanchangInput, ctx: Context) -> str:
    """Check Panchak status for a given date and location.

    Panchak is a 5-nakshatra period (Dhanishta to Revati) considered
    inauspicious for certain activities like construction and travel.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/panchak-rahita", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_gemstone_suggestion", annotations=TOOL_ANNOTATIONS)
async def divine_get_gemstone_suggestion(params: KundliInput, ctx: Context) -> str:
    """Get gemstone recommendations based on the birth chart.

    Returns suggested gemstones based on planetary positions, including
    primary gemstone, alternative stones, and wearing instructions.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/gemstone-suggestion", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# ASHTAKVARGA — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_ashtakvarga", annotations=TOOL_ANNOTATIONS)
async def divine_get_ashtakvarga(params: KundliInput, ctx: Context) -> str:
    """Get Bhinnashtakvarga (individual Ashtakvarga) tables for all planets.

    Returns the 8x12 benefic dots table for each planet showing strength
    in each sign. Used for transit prediction and sign strength analysis.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/bhinnashtakvarga/ashtakvarga", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_prasthara_chakra", annotations=TOOL_ANNOTATIONS)
async def divine_get_prasthara_chakra(params: KundliInput, ctx: Context) -> str:
    """Get Prasthara Chakra (expanded Ashtakvarga) for a birth chart.

    Shows the detailed breakdown of benefic contributions from each
    planet to every sign in the Ashtakvarga system.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/bhinnashtakvarga/prasthara-chakra", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_sarvashtakavarga", annotations=TOOL_ANNOTATIONS)
async def divine_get_sarvashtakavarga(
    chart: str = Field(..., description="Chart type for Sarvashtakavarga: D1, D9, etc."),
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
    ctx: Context = None,
) -> str:
    """Get Sarvashtakavarga (combined Ashtakvarga) for a specific chart.

    The sum of all individual Ashtakvarga tables, showing overall strength
    of each sign. Key for transit predictions.
    """
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v1/bhinnashtakvarga/sarvashtakavarga/{chart}", payload, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# SUB PLANETS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_sub_planet_positions", annotations=TOOL_ANNOTATIONS)
async def divine_get_sub_planet_positions(params: KundliInput, ctx: Context) -> str:
    """Get sub-planet (Upagraha) positions for a birth chart.

    Returns positions of sub-planets like Dhuma, Vyatipata, Parivesha,
    Indra Chapa, and Upaketu with sign, degree, and nakshatra details.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/sub-planet-positions", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_sub_planet_chart", annotations=TOOL_ANNOTATIONS)
async def divine_get_sub_planet_chart(
    chart_type: str = Field(default="north", description="Chart style: 'north' (diamond) or 'south' (square)"),
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
    ctx: Context = None,
) -> str:
    """Generate a sub-planet (Upagraha) chart as SVG and image.

    Returns a visual chart showing the placement of sub-planets
    (Dhuma, Vyatipata, Parivesha, etc.) in North or South Indian style.
    """
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    payload["chart_type"] = chart_type
    return await _call_divine_api("/indian-api/v1/sub-planet-chart", payload, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# JAIMINI ASTROLOGY — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_jaimini_chara_dasha", annotations=TOOL_ANNOTATIONS)
async def divine_get_jaimini_chara_dasha(params: KundliInput, ctx: Context) -> str:
    """Get Jaimini Chara Dasha periods for a birth chart.

    A rashi-based dasha system where signs (not planets) rule the dasha
    periods. Excellent for timing events in Jaimini astrology.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/jaimini-astrology/chara-dasha", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_jaimini_karakamsha_lagna", annotations=TOOL_ANNOTATIONS)
async def divine_get_jaimini_karakamsha_lagna(params: KundliInput, ctx: Context) -> str:
    """Get Karakamsha Lagna from Jaimini astrology for a birth chart.

    The sign occupied by the Atmakaraka in the Navamsha chart.
    Reveals the soul's desire and spiritual inclinations.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/jaimini-astrology/karakamsha-lagna", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_jaimini_padas", annotations=TOOL_ANNOTATIONS)
async def divine_get_jaimini_padas(params: KundliInput, ctx: Context) -> str:
    """Get Jaimini Padas (Arudha Padas) for all houses in a birth chart.

    Arudha Padas show how the world perceives the native regarding
    each house signification (wealth, marriage, career, etc.).
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/jaimini-astrology/padas", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_jaimini_planetary_positions", annotations=TOOL_ANNOTATIONS)
async def divine_get_jaimini_planetary_positions(params: KundliInput, ctx: Context) -> str:
    """Get Jaimini-specific planetary positions and karakas.

    Returns Chara Karakas (variable significators) like Atmakaraka,
    Amatyakaraka, etc. based on planetary degrees.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/jaimini-astrology/planetary-positions", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# KP (KRISHNAMURTI PADDHATI) — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_kp_cuspal_sub", annotations=TOOL_ANNOTATIONS)
async def divine_get_kp_cuspal_sub(params: KundliInput, ctx: Context) -> str:
    """Get KP Cuspal Sub Lords for all house cusps.

    Returns the sub lord of each house cusp, the primary factor for
    KP-based predictions about that house's significations.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kp/cuspal-sub", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kp_planetary_sub", annotations=TOOL_ANNOTATIONS)
async def divine_get_kp_planetary_sub(params: KundliInput, ctx: Context) -> str:
    """Get KP Planetary Sub Lords for all planets.

    Returns the star lord and sub lord for each planet in the KP system,
    essential for KP-based event prediction.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kp/planetary-sub", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kp_cuspal_significator", annotations=TOOL_ANNOTATIONS)
async def divine_get_kp_cuspal_significator(params: KundliInput, ctx: Context) -> str:
    """Get KP Planetary-Cuspal Significator Table.

    A comprehensive table showing which houses each planet signifies
    as star lord and sub lord. Core of KP prediction methodology.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kp/planetary-cuspal-significator-table", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kp_cuspal", annotations=TOOL_ANNOTATIONS)
async def divine_get_kp_cuspal(params: KundliInput, ctx: Context) -> str:
    """Get KP Cuspal chart data for a birth chart.

    Returns detailed cuspal positions with sign, star, and sub divisions
    using the KP ayanamsha and unequal house system.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/kp/cuspal", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kp_planetary_positions", annotations=TOOL_ANNOTATIONS)
async def divine_get_kp_planetary_positions(params: KundliInput, ctx: Context) -> str:
    """Get KP Planetary Positions for a birth chart.

    Returns planetary positions calculated using KP ayanamsha with
    sign lord, star lord, and sub lord for each planet.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/kp/planetary-positions", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# TRANSITS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_kundli_transit_ascendant", annotations=TOOL_ANNOTATIONS)
async def divine_get_kundli_transit_ascendant(params: KundliInput, ctx: Context) -> str:
    """Get transit analysis from the Ascendant (Lagna) for a birth chart.

    Shows current planetary transits analyzed from the birth Ascendant,
    indicating effects on different life areas.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kundli-transit/ascendant", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_kundli_transit_moon", annotations=TOOL_ANNOTATIONS)
async def divine_get_kundli_transit_moon(params: KundliInput, ctx: Context) -> str:
    """Get transit analysis from the Moon sign for a birth chart.

    Shows current planetary transits analyzed from the birth Moon sign,
    the most commonly used transit reference in Vedic astrology.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/kundli-transit/moon", _kundli_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_grah_gochar", annotations=TOOL_ANNOTATIONS)
async def divine_get_grah_gochar(
    planet: str = Field(..., description="Planet: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu"),
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
    ctx: Context = None,
) -> str:
    """Get Grah Gochar (planetary transit) data for a specific planet.

    Returns detailed transit information including sign changes,
    nakshatra transits, and effects on the native.
    """
    planet_lower = planet.lower().strip()
    if planet_lower not in VALID_PLANETS:
        return f"Error: Invalid planet '{planet}'. Must be one of: {', '.join(sorted(VALID_PLANETS))}"
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v2/grah-gochar/{planet_lower}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_planet_combustion_transit", annotations=TOOL_ANNOTATIONS)
async def divine_get_planet_combustion_transit(
    planet: str = Field(..., description="Planet: mars, mercury, jupiter, venus, or saturn"),
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
    ctx: Context = None,
) -> str:
    """Get planet combustion (Asta) transit details for a specific planet.

    Combustion occurs when a planet is too close to the Sun and loses
    strength. Returns combustion periods and their effects.
    """
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v2/planet-combustion-transit/{planet.lower().strip()}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_planet_nakshatra_transit", annotations=TOOL_ANNOTATIONS)
async def divine_get_planet_nakshatra_transit(
    planet: str = Field(..., description="Planet: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu"),
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
    ctx: Context = None,
) -> str:
    """Get nakshatra transit details for a specific planet.

    Returns when the planet enters and exits each nakshatra,
    useful for fine-tuning transit predictions.
    """
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v2/planet-nakshatra-transit/{planet.lower().strip()}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_planet_retrograde_transit", annotations=TOOL_ANNOTATIONS)
async def divine_get_planet_retrograde_transit(
    planet: str = Field(..., description="Planet: mars, mercury, jupiter, venus, or saturn"),
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
    ctx: Context = None,
) -> str:
    """Get retrograde transit details for a specific planet.

    Returns retrograde and direct motion periods for the planet,
    along with their effects on the native.
    """
    api_key, auth_token = _get_credentials(ctx)
    payload = _kundli_params_payload(**{
        "full_name": full_name, "day": day, "month": month, "year": year,
        "hour": hour, "min": min, "sec": sec, "gender": gender,
        "place": place, "lat": lat, "lon": lon, "tzone": tzone, "lan": lan,
    })
    return await _call_divine_api(f"/indian-api/v2/planet-retrograde-transit/{planet.lower().strip()}", payload, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# MATCHMAKING — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_ashtakoot_milan", annotations=TOOL_ANNOTATIONS)
async def divine_get_ashtakoot_milan(params: MatchmakingInput, ctx: Context) -> str:
    """Perform Ashtakoot Milan (8-point compatibility matching) for two people.

    The most popular matching method in North India. Evaluates 8 Gunas:
    Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi (max 36).
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/ashtakoot-milan", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_dashakoot_milan", annotations=TOOL_ANNOTATIONS)
async def divine_get_dashakoot_milan(params: MatchmakingInput, ctx: Context) -> str:
    """Perform Dashakoot Milan (10-point compatibility matching) for two people.

    Popular in South India. Evaluates 10 categories with max score of 36.
    More comprehensive than Ashtakoot Milan.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/dashakoot-milan", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_matching_manglik", annotations=TOOL_ANNOTATIONS)
async def divine_get_matching_manglik(params: MatchmakingInput, ctx: Context) -> str:
    """Check Manglik Dosha for both people in a matchmaking context.

    Compares Manglik status of both individuals to assess marriage
    compatibility when either person is Manglik.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/matching/manglik-dosha", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_matching_basic_astro", annotations=TOOL_ANNOTATIONS)
async def divine_get_matching_basic_astro(params: MatchmakingInput, ctx: Context) -> str:
    """Get basic astrological details for both persons in matchmaking.

    Returns rashi, nakshatra, tithi, gana, nadi, varna, etc. for both
    P1 and P2 side by side for comparison.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v3/matching/basic-astro-details", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_matching_horoscope_chart", annotations=TOOL_ANNOTATIONS)
async def divine_get_matching_horoscope_chart(
    chart_id: str = Field(..., description="Chart type: D1, D9, etc."),
    p1_full_name: str = Field(..., description="Full name of person 1"),
    p1_day: str = Field(..., description="Birth day of person 1"),
    p1_month: str = Field(..., description="Birth month of person 1"),
    p1_year: str = Field(..., description="Birth year of person 1"),
    p1_hour: str = Field(..., description="Birth hour of person 1 (24h)"),
    p1_min: str = Field(..., description="Birth minute of person 1"),
    p1_sec: str = Field(default="0", description="Birth second of person 1"),
    p1_gender: str = Field(..., description="Gender of person 1"),
    p1_place: str = Field(..., description="Birth place of person 1"),
    p1_lat: str = Field(..., description="Latitude of person 1's birth place"),
    p1_lon: str = Field(..., description="Longitude of person 1's birth place"),
    p1_tzone: str = Field(..., description="Timezone of person 1"),
    p2_full_name: str = Field(..., description="Full name of person 2"),
    p2_day: str = Field(..., description="Birth day of person 2"),
    p2_month: str = Field(..., description="Birth month of person 2"),
    p2_year: str = Field(..., description="Birth year of person 2"),
    p2_hour: str = Field(..., description="Birth hour of person 2 (24h)"),
    p2_min: str = Field(..., description="Birth minute of person 2"),
    p2_sec: str = Field(default="0", description="Birth second of person 2"),
    p2_gender: str = Field(..., description="Gender of person 2"),
    p2_place: str = Field(..., description="Birth place of person 2"),
    p2_lat: str = Field(..., description="Latitude of person 2's birth place"),
    p2_lon: str = Field(..., description="Longitude of person 2's birth place"),
    p2_tzone: str = Field(..., description="Timezone of person 2"),
    lan: str = Field(default="en", description="Language code"),
    ctx: Context = None,
) -> str:
    """Generate horoscope charts for both persons in matchmaking.

    Returns charts for both P1 and P2 for the specified divisional chart
    type, enabling visual comparison of birth charts.
    """
    chart_id_upper = chart_id.upper() if chart_id.lower() not in ("chalit", "sun", "moon") else chart_id.lower()
    payload = {
        "p1_full_name": p1_full_name, "p1_day": p1_day, "p1_month": p1_month,
        "p1_year": p1_year, "p1_hour": p1_hour, "p1_min": p1_min,
        "p1_sec": p1_sec, "p1_gender": p1_gender, "p1_place": p1_place,
        "p1_lat": p1_lat, "p1_lon": p1_lon, "p1_tzone": p1_tzone,
        "p2_full_name": p2_full_name, "p2_day": p2_day, "p2_month": p2_month,
        "p2_year": p2_year, "p2_hour": p2_hour, "p2_min": p2_min,
        "p2_sec": p2_sec, "p2_gender": p2_gender, "p2_place": p2_place,
        "p2_lat": p2_lat, "p2_lon": p2_lon, "p2_tzone": p2_tzone,
        "lan": lan,
    }
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api(f"/indian-api/v1/matching/horoscope-chart/{chart_id_upper}", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_matching_vimshottari_dasha", annotations=TOOL_ANNOTATIONS)
async def divine_get_matching_vimshottari_dasha(params: MatchmakingInput, ctx: Context) -> str:
    """Get Vimshottari Dasha for both persons in matchmaking.

    Returns dasha periods for both P1 and P2 to compare planetary
    periods and assess timing compatibility.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/matching/vimshottari-dasha", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_matching_planetary_positions", annotations=TOOL_ANNOTATIONS)
async def divine_get_matching_planetary_positions(params: MatchmakingInput, ctx: Context) -> str:
    """Get planetary positions for both persons in matchmaking.

    Returns side-by-side planetary positions for P1 and P2, useful for
    detailed compatibility analysis beyond standard matching scores.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v2/matching/planetary-positions", _matchmaking_payload(params), api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# FESTIVALS — astroapi-3.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_festivals_by_date", annotations=TOOL_ANNOTATIONS)
async def divine_get_festivals_by_date(params: PanchangInput, ctx: Context) -> str:
    """Get festivals falling on a specific date.

    Returns all Hindu festivals and observances for a given date and location.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/date-specific-festivals", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_english_calendar_festivals", annotations=TOOL_ANNOTATIONS)
async def divine_get_english_calendar_festivals(
    month: str = Field(..., description="English month number ('01' for Jan to '12' for Dec)"),
    year: str = Field(..., description="Year (e.g., '2025')"),
    place: str = Field(..., description="Place name (e.g., 'New Delhi')"),
    lat: str = Field(..., description="Latitude (e.g., '28.6139')"),
    lon: str = Field(..., description="Longitude (e.g., '77.2090')"),
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')"),
    ctx: Context = None,
) -> str:
    """Get all Hindu festivals for a specific English calendar month.

    Returns festivals falling within a given month of the Gregorian calendar.
    """
    payload = {"month": month, "year": year, "Place": place, "lat": lat, "lon": lon, "tzone": tzone}
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/english-calendar-festivals", payload, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_find_festival", annotations=TOOL_ANNOTATIONS)
async def divine_find_festival(params: PanchangInput, ctx: Context) -> str:
    """Find/search for festivals for a given date and location.

    Returns festival information including upcoming festivals,
    their significance, and observance details.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/find-festival", _panchang_payload(params), api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_festivals_by_month", annotations=TOOL_ANNOTATIONS)
async def divine_get_festivals_by_month(
    hindu_month: str = Field(..., description="Hindu month: margashirsha, pausha, magha, phalguna, chaitra, vaishakha, jyeshtha, ashadha, shravana, bhadrapada, ashvina, kartika"),
    year: str = Field(..., description="Year (e.g., '2025')"),
    place: str = Field(..., description="Place name (e.g., 'New Delhi')"),
    lat: str = Field(..., description="Latitude (e.g., '28.6139')"),
    lon: str = Field(..., description="Longitude (e.g., '77.2090')"),
    tzone: str = Field(..., description="Timezone offset (e.g., '5.5')"),
    ctx: Context = None,
) -> str:
    """Get all Hindu festivals for a specific Hindu calendar month.

    Supports all 12 Hindu months: Margashirsha, Pausha, Magha, Phalguna,
    Chaitra, Vaishakha, Jyeshtha, Ashadha, Shravana, Bhadrapada, Ashvina, Kartika.
    """
    month_lower = hindu_month.lower().strip()
    if month_lower not in VALID_HINDU_MONTHS:
        return f"Error: Invalid Hindu month '{hindu_month}'. Must be one of: {', '.join(sorted(VALID_HINDU_MONTHS))}"

    endpoint_map = {
        "margashirsha": "margashirsh-festivals",
        "pausha": "pausha-festivals",
        "magha": "magha-festivals",
        "phalguna": "phalguna-festivals",
        "chaitra": "chaitra-festivals",
        "vaishakha": "vaishakha-festivals",
        "jyeshtha": "jyeshtha-festivals",
        "ashadha": "ashada-festivals",
        "shravana": "shraavana-festivals",
        "bhadrapada": "bhadrapada-festivals",
        "ashvina": "ashvina-festivals",
        "kartika": "kartika-festivals",
    }

    payload = {"year": year, "Place": place, "lat": lat, "lon": lon, "tzone": tzone}
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api(f"/indian-api/v2/{endpoint_map[month_lower]}", payload, api_key=api_key, auth_token=auth_token)


# ══════════════════════════════════════════════
# MONTHLY LISTS — astroapi-8.divineapi.com
# ══════════════════════════════════════════════


@mcp.tool(name="divine_get_chandramasa_list", annotations=TOOL_ANNOTATIONS)
async def divine_get_chandramasa_list(params: PanchangInput, ctx: Context) -> str:
    """Get list of Chandramasa (Hindu lunar months) for a given period.

    Returns the start and end dates of each Hindu lunar month
    for the specified year and location.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/chandramasa-list", _panchang_payload(params), API_HOST_8, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_month_nakshatra_list", annotations=TOOL_ANNOTATIONS)
async def divine_get_month_nakshatra_list(params: PanchangInput, ctx: Context) -> str:
    """Get daily nakshatra list for a given month.

    Returns the nakshatra for each day of the specified month,
    with start/end times and nakshatra lord details.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/month-nakshatra-list", _panchang_payload(params), API_HOST_8, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_month_sunrise_sunset_list", annotations=TOOL_ANNOTATIONS)
async def divine_get_month_sunrise_sunset_list(params: PanchangInput, ctx: Context) -> str:
    """Get daily sunrise and sunset times for a given month.

    Returns sunrise and sunset times for each day of the specified
    month at the given location.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/month-sunrise-sunset-list", _panchang_payload(params), API_HOST_8, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_month_surya_nakshatra_list", annotations=TOOL_ANNOTATIONS)
async def divine_get_month_surya_nakshatra_list(params: PanchangInput, ctx: Context) -> str:
    """Get daily Surya (Sun) Nakshatra list for a given month.

    Returns the Sun's nakshatra position for each day of the month,
    useful for solar-based calendar calculations.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/month-surya-nakshatra-list", _panchang_payload(params), API_HOST_8, api_key=api_key, auth_token=auth_token)


@mcp.tool(name="divine_get_month_tithi_list", annotations=TOOL_ANNOTATIONS)
async def divine_get_month_tithi_list(params: PanchangInput, ctx: Context) -> str:
    """Get daily tithi list for a given month.

    Returns the tithi for each day of the specified month with
    start/end times, paksha, and associated details.
    """
    api_key, auth_token = _get_credentials(ctx)
    return await _call_divine_api("/indian-api/v1/month-tithi-list", _panchang_payload(params), API_HOST_8, api_key=api_key, auth_token=auth_token)


# ──────────────────────────────────────────────
# HTTP / ASGI App
# ──────────────────────────────────────────────


def create_http_app():
    """Create ASGI app for production HTTP deployment with uvicorn."""
    from starlette.middleware.cors import CORSMiddleware

    app = mcp.streamable_http_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "Authorization",
            "Content-Type",
            "X-Divine-Api-Key",
            "X-Divine-Auth-Token",
        ],
        expose_headers=["mcp-session-id"],
    )
    return app


# Module-level ASGI app for uvicorn (only created in HTTP mode)
app = create_http_app() if _TRANSPORT == "http" else None


# ──────────────────────────────────────────────
# Server Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if _TRANSPORT == "http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        mcp.run(transport="stdio")
