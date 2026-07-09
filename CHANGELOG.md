# Changelog

## [2.4.1] - 2026-07-08

### Added

Add server-level instructions (how-to-use note read at connect) and dasha-chain hints (vimshottari to the dasha-analysis tools, lal-kitab mahadasha to antardasha).

## [2.4.0] - 2026-07-08

### Added

**New tool: `divine_get_sankranti_festivals`.** Wraps
`POST /indian-api/v1/sankranti-festivals` (astroapi-3). Returns the twelve solar
Sankranti transitions (Makar, Kumbha, Meena, Mesha, etc.) for a year with dates,
transition moments, and punya kala windows. Params: year, place, lat, lon, tzone.
Verified live before adding and live-tested after. Tool count: 97 -> 98.

## [2.3.0] - 2026-07-08

### Added

**Lal Kitab suite: 16 new tools.** Wraps the new /indian-api/v1/lal-kitab/*
endpoints (astroapi-3): planetary positions, horoscope chart, house position,
conjunctions, teva, planet analysis (selector), dasha, planet types,
mahadasha/antardasha content (text readings, no birth data; the antardasha
pair must be valid for the mahadasha and the API guides on mismatch), debts,
house signification (house_no 1-12), and the four varshphal (annual chart)
tools taking varshphal_year. Every endpoint live-verified before adding and
every tool live-tested after (18/18 scenarios). Tool count: 81 -> 97.

## [2.2.1] - 2026-07-08

### Fixed

**OAuth: clients registered without a scope are no longer rejected when they
request one.** The metadata advertises scope "astrology", so spec-following
connectors (e.g. ChatGPT) may request it even when their dynamic client
registration omitted it; registration now defaults the client scope to
"astrology" (default_scopes). Verified against the full simulated connector
flow: discovery, registration, PKCE authorize, login, token exchange.

## [2.2.0] - 2026-07-08

### Added

**Single-token authentication: `Authorization: Bearer <api_key>:<auth_token>`.**
For platforms that can send only one credential field and no custom headers
(e.g. the Claude Messages API MCP connector). The middleware splits the value
on the first colon and converts it to the internal JWT, exactly like the
X-Divine header pair. Real OAuth JWTs never contain a colon and pass through
untouched. Existing auth methods are unchanged.

## [2.1.4] - 2026-07-08

Param-parity fix batch. Every change below was verified against the live
backend with curl before coding, and every changed tool passed a live
functional test after coding (28/28).

### Fixed

**`divine_get_samvath` renamed to `divine_get_samvat` (BREAKING, but the old
tool never worked).** The tool called `/indian-api/v1/find-samvath`, which does
not exist (HTTP 404 on every call). The live endpoint is
`/indian-api/v1/find-samvat`. Endpoint and tool name corrected.

**`divine_get_bhava_kundli` selector fixed (BREAKING, but the old tool never
worked).** The tool sent chart ids like `D1`/`chalit`, which the endpoint
rejects with "Please enter valid chart id." on every call. The endpoint accepts
only numeric chart ids `1`-`12`; the schema and validation now reflect that.

**`divine_find_festival` rewired.** It sent a date payload the endpoint
ignores; the endpoint requires a `festival` name identifier (e.g.
`maha_shivratri`) plus year and location, and errored on every previous call.
New signature: `festival` + FestivalInput.

**`divine_get_uday_lagna` no longer demands birth details.** The endpoint is
date+place scoped; full_name/gender/hour/min/sec are ignored by the API
(byte-identical responses). They remain accepted as deprecated optional inputs
for backward compatibility but are not sent upstream.

**Monthly list tools no longer demand `day`.** chandramasa_list,
month_nakshatra_list, month_sunrise_sunset_list, month_surya_nakshatra_list,
month_tithi_list are month-scoped; `day` and `lan` have no effect on
astroapi-8 (verified byte-identical). New `MonthInput` model: day/lan accepted
as deprecated optional inputs, not sent upstream.

**`divine_get_chandrashtama` is month-scoped with a real optional `day`.**
`day` narrows results to one date (verified: output changes); it is now
optional instead of required. `lan` is real and kept.

### Added

**`node_type` on 7 tools** (planetary_positions, kaal_sarpa_yoga,
kp_planetary_positions, kp_planetary_sub, kp_cuspal_significator,
jaimini_karakamsha_lagna, jaimini_planetary_positions): optional
`meannode`/`truenode` Rahu-Ketu calculation selector. The API parses and
validates it on all 7 endpoints.

**`month_type` on chandramasa**: optional `amanta`/`purnimanta` lunar month
system selector (verified: changes output, API validates values).

**Chart styling params** (`chart_type`, `chart_color`, `line_color`,
`planet_color`, `sign_color`, plus `show_planet_degree`/`show_planet_retro`/
`show_modern_planets` where the endpoint supports them) on horoscope_chart,
bhava_kundli, sub_planet_chart, kundli_transit_ascendant, kundli_transit_moon.
**`transit_hour`/`transit_min`/`transit_sec`** on both kundli-transit tools
(verified: changes output).

**`nakshatra_pada` on month_nakshatra_list**: optional flag to include pada
details (verified: changes output).

### Docs

README tool tables: count corrected to 81, malayalam/tamil festival tools
added, renamed samvat row, refreshed descriptions of the fixed tools.

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
