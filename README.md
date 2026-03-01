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

## 📋 Available Tools (27 Total)

### 🗓️ Panchang (Daily Vedic Calendar) — 9 Tools

| Tool | Description |
|---|---|
| `divine_get_panchang` | Complete daily Panchang (tithi, nakshatra, yoga, karana, timings) |
| `divine_get_sun_moon` | Sunrise, sunset, moonrise, moonset timings |
| `divine_get_nakshatra` | Current nakshatra details with start/end times |
| `divine_get_tithi` | Current tithi, paksha, and deity |
| `divine_get_auspicious_timings` | Shubh Muhurat — favorable time windows |
| `divine_get_inauspicious_timings` | Rahu Kaal, Yamaganda, Gulika Kaal |
| `divine_get_choghadiya` | Day/night Choghadiya time slots |
| `divine_get_planet_transit` | Current Grah Gochar (planetary transits) |
| `divine_get_chandrashtama` | Chandrashtama periods for all moon signs |

### 🔮 Kundli (Birth Chart) — 11 Tools

| Tool | Description |
|---|---|
| `divine_get_basic_astro_details` | Core birth chart data (rashi, nakshatra, tithi, etc.) |
| `divine_get_planetary_positions` | All 9 planet positions with sign, degree, house |
| `divine_get_horoscope_chart` | Generate Kundli chart images (D1, D9, chalit, etc.) |
| `divine_get_vimshottari_dasha` | Maha Dasha and Antar Dasha periods |
| `divine_get_manglik_dosha` | Manglik Dosha check with severity |
| `divine_get_kaal_sarpa_dosha` | Kaal Sarpa Dosha detection |
| `divine_get_sadhe_sati` | Sadhe Sati status and phase |
| `divine_get_gemstone_suggestions` | Recommended gemstones based on chart |
| `divine_get_yogas` | All yogas (planetary combinations) in chart |
| `divine_get_ascendant_report` | Detailed Lagna (rising sign) report |
| `divine_get_pitra_dosha` | Pitra Dosha check with remedies |

### 💑 Matchmaking (Kundli Milan) — 4 Tools

| Tool | Description |
|---|---|
| `divine_get_ashtakoot_milan` | 8-point Guna matching (max 36 score) |
| `divine_get_dashakoot_milan` | 10-point matching (South Indian style) |
| `divine_get_matching_manglik` | Manglik comparison for both persons |
| `divine_get_matching_basic_astro` | Side-by-side astro details for both persons |

### 🎉 Festivals — 3 Tools

| Tool | Description |
|---|---|
| `divine_get_festivals_by_month` | Festivals for a Hindu calendar month |
| `divine_get_festivals_by_date` | Festivals on a specific date |
| `divine_get_english_calendar_festivals` | Festivals in an English calendar month |

---

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
