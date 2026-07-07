# Changelog

## [Unreleased] - 2026-07-07

### Added

**New tool: `divine_get_tamil_festivals`.**
Wraps `POST /indian-api/v1/tamil-festivals` (astroapi-3). Returns major Tamil
festivals (Thai Pongal, Puthandu, Karthigai Deepam, Vaikuntha Ekadashi, etc.)
for a given year and location. Params: year, place, lat, lon, tzone.
Verified against the live endpoint before adding.

**New tool: `divine_get_malayalam_festivals`.**
Wraps `POST /indian-api/v1/malayalam-festivals` (astroapi-3). Returns major
Kerala festivals (Vishu Kani, Onam, Thrissur Pooram, Guruvayur Ekadashi, etc.)
for a given year and location. Params: year, place, lat, lon, tzone (no lan).
Verified against the live endpoint before adding.

## [Unreleased] - 2026-07-06

### Added

**New tool: `divine_get_gowri_panchangam`.**
Wraps the new backend endpoint `POST /indian-api/v1/find-gowri-panchangam`
(astroapi-3). Returns Gowri Panchangam auspicious/inauspicious day and night
segments plus Nalla Neram periods for a date and location. Standard
`PanchangInput` (date + place), no selector fields. Verified against the live
endpoint before adding.

## [Released] - 2026-06-29

Three MCP-wrapper bugs found while debugging a customer report. All fixed and deployed.

### Fixed

**1. Eight selector-style tools were uncallable.**
These tools proxy to a backend endpoint that requires a selector field (which
planet / which dasha), but the selector was never exposed in the tool's input
schema. Because `params` uses `additionalProperties: false`, clients could not
pass it inside `params`, and a sibling field was silently dropped, so the
backend always replied "please enter valid planet/dasha type." The selectors are
now top-level tool arguments. New input fields:

| Tool | New required field(s) | Valid values |
|---|---|---|
| `divine_get_planet_analysis` | `analysis_planet` (+ birth details) | sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu |
| `divine_get_vimshottari_dasha` | `dasha_type` (+ birth details) | maha-dasha, antar-dasha, pratyantar-dasha, sookshma-dasha, prana-dasha, deha-dasha |
| `divine_get_maha_dasha_analysis` | `maha_dasha` | planet (9) — no birth data needed |
| `divine_get_antar_dasha_analysis` | `maha_dasha`, `antar_dasha` | planet (9) each — no birth data needed |
| `divine_get_pratyantar_dasha_analysis` | `maha_dasha`, `antar_dasha`, `pratyantar_dasha` | planet (9) each — no birth data needed |
| `divine_get_kundli_transit_ascendant` | `transit_day`, `transit_month`, `transit_year` (+ birth details) | date parts |
| `divine_get_kundli_transit_moon` | `transit_day`, `transit_month`, `transit_year` (+ birth details) | date parts |
| `divine_get_nav_pancham_yoga` | two-person input (`p1_*`, `p2_*`) | replaced incorrect single-person input |

Conditionals on `divine_get_vimshottari_dasha`:
- `maha_dasha` (planet) required when `dasha_type` is `prana-dasha` or `deha-dasha`
- `antar_dasha` (planet) required when `dasha_type` is `deha-dasha`

"planet (9)" = sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu.
All planet/dasha inputs are validated; invalid values return a clear error
listing the accepted options.

**2. Monthly-list tools returned an error that looked like an entitlement gap.**
`divine_get_chandramasa_list`, `divine_get_month_tithi_list`,
`divine_get_month_nakshatra_list`, `divine_get_month_sunrise_sunset_list`, and
`divine_get_month_surya_nakshatra_list` proxy to the astroapi-8 host, which
strictly requires a lowercase `place` form field. The shared payload builders
sent capital `Place`. astroapi-1/2/3 accept either casing, which hid the bug;
astroapi-8 rejected it. This was **not** a plan/entitlement issue — the same key
returns HTTP 200 once `place` is lowercased. Fixed in `_panchang_payload`,
`_festival_payload`, and the inline festival payloads.

**3. Upstream failures were reported as successful (`isError: false`).**
`_call_divine_api` caught every error and returned it as a normal string, so
MCP clients saw a success result whose text merely contained "Error: ...".
It now raises `ToolError` on non-2xx responses, network errors, and on the
HTTP-200 error envelopes used by the backend hosts
(`{"success": 3, ...}` on astroapi-3, `{"status": "error", ...}` on astroapi-8),
so `isError` is `true` and clients can detect failures.

### Known issues (backend, not in this wrapper)

- **astroapi-3 returns HTTP 200 on auth failure** (`{"success": 3, "msg":
  "Invalid authorization token!"}`). This wrapper now detects and surfaces it as
  an error, but the backend should return 401/403. Tracked separately with the
  DivineAPI API team.
