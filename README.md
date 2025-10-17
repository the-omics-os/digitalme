# healthOS

**Multi-factor, all-in-one health assistant accessible via Telegram**

healthOS combines conversational AI with evidence-based health intelligence powered by INDRA bio-ontology. Ask health questions and get answers backed by scientific research, or chat naturally for everyday tasks.

## Features

**Health Intelligence (INDRA Bio-Ontology)**
- Causal pathway analysis backed by scientific papers
- Biomarker and exposure relationship discovery
- Personalized insights based on genetics and location history
- Evidence-based responses from peer-reviewed research

**Conversational AI (OpenAI GPT-4)**
- Natural language chat for general queries
- Image generation with DALL-E
- Voice message transcription
- Web search integration
- Multiple personality modes (assistant, artist, code helper)

**Data Persistence**
- MongoDB for user profiles and chat history
- Health data storage (genetics, biomarkers, locations)
- Usage tracking and analytics

## Architecture

```
User → Telegram Bot
         ↓
    [Query Detection]
         ↓
    ┌────┴────┐
    ↓         ↓
Health Query  General Query
    ↓         ↓
INDRA Agent   OpenAI GPT-4
(Bio-ontology) (Conversational)
    ↓         ↓
   Response   Response
```

**Integration**: INDRA agent runs inside the bot via direct Python imports (no HTTP overhead)

**Auto-routing**: Health keywords automatically trigger INDRA bio-ontology analysis

**Fallback**: Falls back to OpenAI for non-health queries or if INDRA unavailable

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Telegram bot token ([create one](https://t.me/botfather))
- OpenAI API key
- AWS Bedrock access (for health intelligence)
- MongoDB (included in docker-compose)

### Setup

1. **Configure credentials**

Edit `healthos_bot/config/config.env`:

```bash
# Telegram & OpenAI
TELEGRAM_TOKEN=your-telegram-bot-token
OPENAI_API_KEY=your-openai-api-key

# AWS Bedrock (for health intelligence)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# MongoDB (defaults are fine)
MONGODB_PORT=27017
```

Edit `healthos_bot/config/config.yml`:

```yaml
telegram_token: ${TELEGRAM_TOKEN}
openai_api_key: ${OPENAI_API_KEY}
allowed_telegram_usernames: []  # Empty = allow all users
```

2. **Start the bot**

```bash
cd healthos_bot/
docker-compose --env-file config/config.env up --build
```

3. **Chat with your bot**

Open Telegram and search for your bot, then send:
- `/start` - Initialize bot
- `/help` - See available commands

## Usage Examples

### Health Queries (Triggers INDRA)

**Keywords**: biomarker, inflammation, pollution, genetic, crp, il-6, pm2.5, oxidative stress, causal, pathway

**Example**: "How does PM2.5 pollution affect CRP biomarkers?"

**Response**:
```
🧬 Health Intelligence Report

📊 Key Insights:
1. PM2.5 exposure increases inflammatory biomarkers through oxidative stress
2. Causal chain: PM2.5 → NF-κB → IL-6 → CRP
3. Based on 312 peer-reviewed papers

🔬 Causal Analysis:
• 5 biological entities identified
• 4 causal relationships found
• Analysis time: 2.8s

🔗 Top Pathways:
  PM2.5 ⬆️ NF-κB (47 papers, effect: 0.82)
  NF-κB ⬆️ IL-6 (89 papers, effect: 0.87)
  IL-6 ⬆️ CRP (312 papers, effect: 0.98)
```

### General Queries (Uses OpenAI)

**Example**: "What's the weather like today?"

**Response**: [Standard ChatGPT conversational response]

### Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/new` - Start new conversation
- `/mode` - Switch chat mode (assistant/artist/code)
- `/search [query]` - Web search

## User Health Data

Store personal health context for personalized insights:

**Genetics**:
```python
db.set_user_attribute(user_id, 'health_genetics', {
    'GSTM1': 'null',
    'CYP1A1': 'T/T'
})
```

**Biomarkers**:
```python
db.set_user_attribute(user_id, 'health_biomarkers', {
    'CRP': 5.2,  # mg/L
    'IL-6': 3.8  # pg/mL
})
```

**Location History** (for environmental exposure):
```python
db.set_user_attribute(user_id, 'health_location_history', [
    {
        'city': 'San Francisco',
        'start_date': '2024-01-01',
        'end_date': '2024-06-01',
        'avg_pm25': 12.5
    }
])
```

## Project Structure

```
digitalme/
├── healthos_bot/              # Telegram bot
│   ├── bot/
│   │   ├── bot.py            # Main bot (imports indra_agent)
│   │   ├── database.py       # MongoDB abstraction
│   │   └── openai_utils.py   # OpenAI utilities
│   ├── config/
│   │   ├── config.yml        # Bot settings
│   │   ├── config.env        # Environment variables
│   │   ├── chat_modes.yml    # Bot personalities
│   │   └── models.yml        # OpenAI models
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── indra_agent/              # Health intelligence (integrated)
    ├── agents/               # LangGraph agents
    ├── core/                 # Client & models
    ├── services/             # INDRA API, grounding, graph building
    └── config/               # Agent prompts, cached responses
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -e .
cd healthos_bot/
pip install -r requirements.txt

# Run bot
python3 bot/bot.py
```

### Viewing Logs

```bash
# Docker logs
docker logs chatgpt_telegram_bot -f

# Check INDRA initialization
docker logs chatgpt_telegram_bot | grep "INDRA"
```

### Database Admin

MongoDB Express admin UI: http://localhost:8081

## Troubleshooting

### "Module not found: indra_agent"

Rebuild with correct context:
```bash
cd healthos_bot/
docker-compose down
docker-compose --env-file config/config.env up --build
```

### AWS Bedrock Access Denied

Add valid credentials to `healthos_bot/config/config.env`:
```bash
AWS_ACCESS_KEY_ID=your-real-key
AWS_SECRET_ACCESS_KEY=your-real-secret
AWS_REGION=us-east-1
```

Verify Bedrock access in your AWS account.

### Health Queries Not Detected

Add more keywords to `is_health_query()` in `healthos_bot/bot/bot.py:111`

Current keywords: biomarker, crp, il-6, inflammation, pollution, pm2.5, genetic, health, causal, pathway

### Bot Not Responding

Check Docker status:
```bash
docker-compose ps
```

Restart services:
```bash
docker-compose restart
```

## Technology Stack

**Bot Framework**: python-telegram-bot
**AI Models**:
- OpenAI GPT-4, GPT-4o, DALL-E, Whisper
- AWS Bedrock Claude Sonnet 4.5
**Health Intelligence**: INDRA bio-ontology, LangGraph
**Database**: MongoDB
**Deployment**: Docker

## Documentation

- **CLAUDE.md** - Detailed technical documentation
- **agentic-system-spec.md** - API specification for INDRA agent

## License

MIT License

## Contributing

This project was built for a hackathon. Contributions welcome!
