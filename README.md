# 🙏 Divine API — Indian Astrology MCP Server

The official [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for **[Divine API's](https://divineapi.com) Indian/Vedic Astrology** services.

Connect your AI assistant (Claude, Cursor, VS Code Copilot, etc.) to the power of Vedic astrology — Panchang, Kundli, Matchmaking, Festivals, and more — all through natural language.

## ✨ What Can It Do?

Just chat naturally with your AI assistant:

| You say... | The MCP calls... |
|---|---|
| *"What's today's Panchang for Delhi?"* | `divine_get_panchang` |
| *"Generate my Kundli — born March 15, 1990, 2:30 PM, Mumbai"* | `divine_get_basic_astro_details` |
| *"Am I Manglik?"* | `divine_get_manglik_dosha` |
| *"Match Kundli for Rahul and Simran"* | `divine_get_ashtakoot_milan` |
| *"What festivals are in Kartik month 2025?"* | `divine_get_festivals_by_month` |
| *"Show me the Navamsha (D9) chart"* | `divine_get_horoscope_chart` |
| *"What gemstone should I wear?"* | `divine_get_gemstone_suggestions` |
| *"Is Sadhe Sati active for me?"* | `divine_get_sadhe_sati` |

---

## 🚀 Quick Start

### 1. Get Your API Credentials

Sign up at **[divineapi.com](https://divineapi.com)** and get your:
- **API Key** — from [divineapi.com/api-keys](https://divineapi.com/api-keys)
- **Auth Token** (Bearer Token) — from your profile page

You get a **7-day free trial** — no charges until you decide to continue.

### 2. Install

```bash
pip install divineapi-indian-astrology-mcp
```

Or with `uv` (recommended):
```bash
uv pip install divineapi-indian-astrology-mcp
```

### 3. Configure Your AI Client

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "divine-indian-astrology": {
      "command": "python",
      "args": ["-m", "divineapi_indian_astrology_mcp"],
      "env": {
        "DIVINE_API_KEY": "your-api-key-here",
        "DIVINE_AUTH_TOKEN": "your-bearer-token-here"
      }
    }
  }
}
```

#### Cursor / VS Code

Add to your MCP settings:

```json
{
  "divine-indian-astrology": {
    "command": "python",
    "args": ["-m", "divineapi_indian_astrology_mcp"],
    "env": {
      "DIVINE_API_KEY": "your-api-key-here",
      "DIVINE_AUTH_TOKEN": "your-bearer-token-here"
    }
  }
}
```

#### Claude Code

```bash
claude mcp add divine-indian-astrology \
  -e DIVINE_API_KEY=your-api-key-here \
  -e DIVINE_AUTH_TOKEN=your-bearer-token-here \
  -- python -m divineapi_indian_astrology_mcp
```

### 4. Restart your AI client and start chatting!

---

## 📋 Available Tools (81 Total)

### 🗓️ Panchang (Daily Vedic Calendar) — 6 Tools

| Tool | Description |
|------|-------------|
| `divine_get_panchang` | Get the complete daily Panchang for a given date and location |
| `divine_get_tithi` | Get tithi (lunar day) details for a given date and location |
| `divine_get_nakshatra` | Get nakshatra (lunar mansion) details for a given date and location |
| `divine_get_karana` | Get karana details for a given date and location |
| `divine_get_surya_nakshatra` | Get Surya (Sun) Nakshatra details for a given date and location |
| `divine_get_yoga_panchang` | Get yoga (Sun-Moon angular relationship) for a given date and location |

### 🗓️ Panchang Extended — 7 Tools

| Tool | Description |
|------|-------------|
| `divine_get_choghadiya` | Get Choghadiya (auspicious time slots) for a given date and location |
| `divine_get_nivas_and_shool` | Get Nivas and Shool (directional inauspicious timings) for a date and location |
| `divine_get_ritu_and_anaya` | Get Ritu (season) and Anaya details for a given date and location |
| `divine_get_samvat` | Get Samvat (Hindu calendar year) details for a given date and location |
| `divine_get_chandrabalam_and_tarabalam` | Get Chandrabalam and Tarabalam for a given date and location |
| `divine_get_other_calendars_and_epoch` | Get dates in other calendar systems and epoch values for a given date |
| `divine_get_sun_moon` | Get sun and moon rise/set timings for a given date and location |

### ⏰ Timings (Muhurat & Gowri Panchangam) — 3 Tools

| Tool | Description |
|------|-------------|
| `divine_get_auspicious_timings` | Get auspicious timings (shubh muhurat) for a given date and location |
| `divine_get_inauspicious_timings` | Get inauspicious timings for a given date and location |
| `divine_get_gowri_panchangam` | Get the Gowri Panchangam for a given date and location |

### 🔮 Kundli (Birth Chart) Basics — 9 Tools

| Tool | Description |
|------|-------------|
| `divine_get_basic_astro_details` | Get basic astrological details for a person based on their birth data |
| `divine_get_planetary_positions` | Get planetary positions in the birth chart (Kundli) |
| `divine_get_horoscope_chart` | Generate a Vedic horoscope chart (Kundli diagram) as SVG and image |
| `divine_get_bhava_kundli` | Get Bhava Kundli (house-based chart) for a given bhava chart number |
| `divine_get_planet_analysis` | Get detailed analysis of one planet in the birth chart |
| `divine_get_ascendant_report` | Get a detailed report based on the ascendant (Lagna) sign |
| `divine_get_uday_lagna` | Get Uday Lagna (rising sign) timings for a given date and location |
| `divine_get_chandramasa` | Get Chandramasa (Hindu lunar month) details for a given date and location |
| `divine_get_chandrashtama` | Get Chandrashtama periods for a given month and location |

### ⚠️ Doshas — 4 Tools

| Tool | Description |
|------|-------------|
| `divine_get_manglik_dosha` | Check for Manglik Dosha (Mangal Dosha / Kuja Dosha) in the birth chart |
| `divine_get_kaal_sarpa_yoga` | Check for Kaal Sarpa Yoga in the birth chart |
| `divine_get_pitra_dosha` | Check for Pitra Dosha (ancestral affliction) in the birth chart |
| `divine_get_sadhe_sati` | Check Sadhe Sati (Saturn transit) status for the person |

### 🪐 Dasha Systems — 6 Tools

| Tool | Description |
|------|-------------|
| `divine_get_vimshottari_dasha` | Get Vimshottari Dasha periods for a birth chart at the requested granularity |
| `divine_get_maha_dasha_analysis` | Get textual interpretation of a Maha Dasha period (no birth data needed) |
| `divine_get_antar_dasha_analysis` | Get textual interpretation of an Antar Dasha (Maha→Antar) period |
| `divine_get_pratyantar_dasha_analysis` | Get textual interpretation of a Pratyantar Dasha (Maha→Antar→Pratyantar) period |
| `divine_get_yogini_dasha` | Get Yogini Dasha periods for a birth chart |
| `divine_get_kaal_chakra_dasha` | Get Kaal Chakra Dasha periods for a birth chart |

### 💪 Yogas & Strengths — 8 Tools

| Tool | Description |
|------|-------------|
| `divine_get_yogas` | Get all yogas (planetary combinations) present in the birth chart |
| `divine_get_nav_pancham_yoga` | Get Nav Pancham Yoga compatibility analysis between two charts |
| `divine_get_shadbala` | Get Shadbala (six-fold planetary strength) for a birth chart |
| `divine_get_composite_friendship` | Get composite (Panchda) friendship table for all planets |
| `divine_get_ghata_chakra` | Get Ghata Chakra (adverse combinations) for a birth chart |
| `divine_get_sudarshana_chakra` | Get Sudarshana Chakra for a birth chart |
| `divine_get_panchak_rahita` | Check Panchak status for a given date and location |
| `divine_get_gemstone_suggestion` | Get gemstone recommendations based on the birth chart |

### 📊 Ashtakvarga — 3 Tools

| Tool | Description |
|------|-------------|
| `divine_get_ashtakvarga` | Get Bhinnashtakvarga (individual Ashtakvarga) tables for all planets |
| `divine_get_prasthara_chakra` | Get Prasthara Chakra (expanded Ashtakvarga) for a birth chart |
| `divine_get_sarvashtakavarga` | Get Sarvashtakavarga (combined Ashtakvarga) for a specific chart |

### 🌑 Sub Planets (Upagrahas) — 2 Tools

| Tool | Description |
|------|-------------|
| `divine_get_sub_planet_positions` | Get sub-planet (Upagraha) positions for a birth chart |
| `divine_get_sub_planet_chart` | Generate a sub-planet (Upagraha) chart as SVG and image |

### 📜 Jaimini Astrology — 4 Tools

| Tool | Description |
|------|-------------|
| `divine_get_jaimini_chara_dasha` | Get Jaimini Chara Dasha periods for a birth chart |
| `divine_get_jaimini_karakamsha_lagna` | Get Karakamsha Lagna from Jaimini astrology for a birth chart |
| `divine_get_jaimini_padas` | Get Jaimini Padas (Arudha Padas) for all houses in a birth chart |
| `divine_get_jaimini_planetary_positions` | Get Jaimini-specific planetary positions and karakas |

### 🎯 KP (Krishnamurti Paddhati) — 5 Tools

| Tool | Description |
|------|-------------|
| `divine_get_kp_cuspal_sub` | Get KP Cuspal Sub Lords for all house cusps |
| `divine_get_kp_planetary_sub` | Get KP Planetary Sub Lords for all planets |
| `divine_get_kp_cuspal_significator` | Get KP Planetary-Cuspal Significator Table |
| `divine_get_kp_cuspal` | Get KP Cuspal chart data for a birth chart |
| `divine_get_kp_planetary_positions` | Get KP Planetary Positions for a birth chart |

### 🚀 Transits — 6 Tools

| Tool | Description |
|------|-------------|
| `divine_get_kundli_transit_ascendant` | Get transit analysis from the Ascendant (Lagna) on a chosen transit date |
| `divine_get_kundli_transit_moon` | Get transit analysis from the Moon sign on a chosen transit date |
| `divine_get_grah_gochar` | Get Grah Gochar (planetary transit) data for a specific planet |
| `divine_get_planet_combustion_transit` | Get planet combustion (Asta) transit details for a specific planet |
| `divine_get_planet_nakshatra_transit` | Get nakshatra transit details for a specific planet |
| `divine_get_planet_retrograde_transit` | Get retrograde transit details for a specific planet |

### 💑 Matchmaking (Kundli Milan) — 7 Tools

| Tool | Description |
|------|-------------|
| `divine_get_ashtakoot_milan` | Perform Ashtakoot Milan (8-point compatibility matching) for two people |
| `divine_get_dashakoot_milan` | Perform Dashakoot Milan (10-point compatibility matching) for two people |
| `divine_get_matching_manglik` | Check Manglik Dosha for both people in a matchmaking context |
| `divine_get_matching_basic_astro` | Get basic astrological details for both persons in matchmaking |
| `divine_get_matching_horoscope_chart` |  |
| `divine_get_matching_vimshottari_dasha` | Get Vimshottari Dasha for both persons in matchmaking |
| `divine_get_matching_planetary_positions` | Get planetary positions for both persons in matchmaking |

### 🎉 Festivals — 6 Tools

| Tool | Description |
|------|-------------|
| `divine_get_festivals_by_date` | Get festivals falling on a specific date |
| `divine_get_english_calendar_festivals` | Get all Hindu festivals for a specific English calendar month |
| `divine_find_festival` | Find the date(s) of a specific festival in a given year |
| `divine_get_festivals_by_month` | Get all Hindu festivals for a specific Hindu calendar month |
| `divine_get_malayalam_festivals` | Get major Malayalam (Kerala) festivals for a year |
| `divine_get_tamil_festivals` | Get major Tamil festivals for a year |

### 📅 Monthly Lists — 5 Tools

| Tool | Description |
|------|-------------|
| `divine_get_chandramasa_list` | Get list of Chandramasa (Hindu lunar months) for a given period |
| `divine_get_month_nakshatra_list` | Get daily nakshatra list for a given month |
| `divine_get_month_sunrise_sunset_list` | Get daily sunrise and sunset times for a given month |
| `divine_get_month_surya_nakshatra_list` | Get daily Surya (Sun) Nakshatra list for a given month |
| `divine_get_month_tithi_list` | Get daily tithi list for a given month |

## 🌐 Language Support

All tools support multiple Indian languages via the `lan` parameter:

| Code | Language |
|---|---|
| `en` | English (default) |
| `hi` | Hindi |
| `ta` | Tamil |
| `te` | Telugu |
| `kn` | Kannada |
| `ml` | Malayalam |
| `bn` | Bengali |
| `gu` | Gujarati |
| `mr` | Marathi |
| `pa` | Punjabi |
| `or` | Odia |
| `ur` | Urdu |

---

## 🛠️ Development / Running from Source

If you want to run from source instead of installing via pip:

```bash
# Clone the repository
git clone https://github.com/DivineAPI/mcp-indian-astrology.git
cd mcp-indian-astrology

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DIVINE_API_KEY="your-api-key"
export DIVINE_AUTH_TOKEN="your-bearer-token"

# Run the server
python server.py
```

Then configure your MCP client to point to the local file:

```json
{
  "mcpServers": {
    "divine-indian-astrology": {
      "command": "python",
      "args": ["/full/path/to/mcp-indian-astrology/server.py"],
      "env": {
        "DIVINE_API_KEY": "your-api-key",
        "DIVINE_AUTH_TOKEN": "your-bearer-token"
      }
    }
  }
}
```

---

## 🔑 Getting Your API Credentials

1. Go to [divineapi.com](https://divineapi.com) and sign up
2. Start your **7-day free trial** (no charges)
3. Find your **API Key** at [divineapi.com/api-keys](https://divineapi.com/api-keys)
4. Find your **Auth Token** on your profile page
5. Set them as environment variables or in your MCP client config

---

## 📖 API Documentation

- **Full API Docs**: [developers.divineapi.com/indian-api](https://developers.divineapi.com/indian-api)
- **Support**: [support.divineapi.com](https://support.divineapi.com)
- **Pricing**: [divineapi.com/pricing](https://divineapi.com/pricing)

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🏢 About Divine API

[Divine API](https://divineapi.com) is a leading astrology technology company based in New Delhi, offering comprehensive Astrology, Kundali, Horoscope, Tarot, and Numerology APIs for businesses worldwide.

**Contact**: admin@divineapi.com
