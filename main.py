import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from sqlmodel import Session

from db import init_db, engine
from models import User
from agents import medical_agent
from outbreak import fetch_outbreaks
from hospital import find_hospitals
from vaccine import get_vaccine_schedule
from symptoms import get_symptoms

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_URL = f"{BASE_URL}/webhook"

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(engine) as s:
        s.add(User(
            telegram_id=update.effective_user.id,
            country="India"
        ))
        s.commit()

    await update.message.reply_text(
        "Healthcare AI Bot Ready\n\n"
        "/ask <question>\n"
        "/outbreak\n"
        "/hospital <city>\n"
        "/vaccine <disease>\n"
        "/symptoms <disease>"
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args)
    result = medical_agent.invoke({"query": q})
    await update.message.reply_text(result["final_answer"])

async def outbreak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outbreaks = fetch_outbreaks()
    msg = ""
    for o in outbreaks[:5]:
        msg += f"{o['disease']} ({o['year']})\n{o['country']}\n\n"
    await update.message.reply_text(msg or "No outbreaks found")

async def hospital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args)
    hospitals = find_hospitals(city)
    msg = ""
    for h in hospitals:
        msg += f"{h.get('display_name', 'Unknown')}\n\n"
    await update.message.reply_text(msg or "No hospitals found")

async def vaccine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    disease = " ".join(context.args).lower()
    if not disease:
        await update.message.reply_text("Usage: /vaccine <disease>")
        return
    info = get_vaccine_schedule(disease)
    if not info:
        await update.message.reply_text("No vaccine data found")
        return
    await update.message.reply_text(
        f"Vaccine: {info.vaccine_name}\n"
        f"Disease: {disease.title()}\n"
        f"Age Group: {info.age_group}\n"
        f"Schedule: {info.schedule}\n"
        f"Doses: {info.doses}\n"
        f"Source: {info.source}"
    )

async def symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    disease = " ".join(context.args).lower()
    if not disease:
        await update.message.reply_text("Usage: /symptoms <disease>")
        return
    data = get_symptoms(disease)
    await update.message.reply_text(data or "No symptom data found")

# --- APPLICATION BUILDER ---
def build_application() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("outbreak", outbreak))
    app.add_handler(CommandHandler("hospital", hospital))
    app.add_handler(CommandHandler("vaccine", vaccine))
    app.add_handler(CommandHandler("symptoms", symptoms))
    return app

telegram_app = build_application()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set successfully to {WEBHOOK_URL}")
    yield
    # Shutdown logic
    await telegram_app.shutdown()

fastapi_app = FastAPI(lifespan=lifespan)

@fastapi_app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

if __name__ == "__main__":
    # Running on port 8000 (make sure ngrok is pointing to this port)
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)