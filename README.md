# Healthcare AI Bot 

**A HIPAA-safe AI-powered Telegram bot** for healthcare assistance.  
Provides **real-time outbreak alerts, vaccination schedules, disease symptoms, and nearby hospital search**, with offline caching in a database and optional RAG integration for verified medical sources.

---

## Features

- **AI Question Answering**: Ask medical questions with `/ask <question>`  
- **Disease Outbreak Alerts**: `/outbreak` shows recent outbreaks (< 1 year)  
- **Hospital Finder**: `/hospital <city>` finds nearby hospitals  
- **Vaccination Schedule**: `/vaccine <disease>` shows verified schedules  
- **Disease Symptoms**: `/symptoms <disease>`  
- **Automatic Outbreak Broadcast**: Alerts users based on country subscription  
- **HIPAA-Safe Architecture**: No personal data stored without consent  
- **Extensible**: Ready for LangGraph/LangChain orchestration and RAG integration

---

## Tech Stack

- **Python 3.11+**
- **Telegram Bot API** (python-telegram-bot v20+)
- **LangChain / LangGraph / Ollama LLM**
- **SQLModel / SQLite** (database for caching)
- **Requests** (fetch WHO outbreak data)
- **Asyncio** (background tasks and notifications)

---

## Installation

install ollama 
git clone https://github.com/yourusername/healthcare-ai-bot.git
cd healthcare-ai-bot
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
after install required python libraries via pip 
