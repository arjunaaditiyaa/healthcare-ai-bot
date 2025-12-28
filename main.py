import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlmodel import Session, select

from db import init_db, engine
from models import User
from agents import medical_agent
from outbreak import fetch_outbreaks
from hospital import find_hospitals
from vaccine import get_vaccine_schedule
from symptoms import get_symptoms

TOKEN = "YOUR_TOKEN"

init_db()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(engine) as s:
        s.add(
            User(
                telegram_id=update.effective_user.id,
                country="India"
            )
        )
        s.commit()

    await update.message.reply_text(
        "Healthcare AI Bot Ready\n\n"
        "Available Commands:\n"
        "/ask <question> – Ask medical questions\n"
        "/outbreak – View recent disease outbreaks\n"
        "/hospital <city> – Find nearby hospitals\n"
        "/vaccine <disease> – Get vaccination schedule\n"
        "/symptoms <disease> – View disease symptoms\n"
    )


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args)
    result = medical_agent.invoke({"query": q})
    await update.message.reply_text(result["final_answer"])


async def outbreak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outbreaks = fetch_outbreaks()

    msg = ""
    for o in outbreaks[:5]:
        msg += f"🚨 {o['disease']} ({o['year']})\n{o['country']}\n\n"

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

    msg = (
        f"Vaccine: {info.vaccine_name}\n"
        f"Disease: {disease.title()}\n"
        f"Age Group: {info.age_group}\n"
        f"Schedule: {info.schedule}\n"
        f"Doses: {info.doses}\n"
        f"Source: {info.source}"
    )
    await update.message.reply_text(msg)


async def symptoms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    disease = " ".join(context.args).lower()
    if not disease:
        await update.message.reply_text("Usage: /symptoms <disease>")
        return

    symptoms = get_symptoms(disease)
    if not symptoms:
        await update.message.reply_text("No symptom data found")
        return

    await update.message.reply_text(
        f"Symptoms of {disease.title()}:\n{symptoms}"
    )

async def outbreak_broadcast(context: ContextTypes.DEFAULT_TYPE):
    outbreaks = fetch_outbreaks()

    with Session(engine) as s:
        users = s.exec(select(User)).all()
        user_data = [
            {
                "telegram_id": u.telegram_id,
                "country": u.country
            }
            for u in users
        ]

    for u in user_data:
        for o in outbreaks:
            if u["country"].lower() in o["country"].lower():
                await context.bot.send_message(
                    chat_id=u["telegram_id"],
                    text=f"OUTBREAK ALERT\n{o['disease']} ({o['year']})\n{o['country']}"
                )


async def error_handler(update, context):
    print("Error:", context.error)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("outbreak", outbreak))
    app.add_handler(CommandHandler("hospital", hospital))
    app.add_handler(CommandHandler("vaccine", vaccine))
    app.add_handler(CommandHandler("symptoms", symptoms))

    app.job_queue.run_repeating(
        outbreak_broadcast,
        interval=86400,
        first=10
    )

    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
