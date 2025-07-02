#!/usr/bin/env python3
"""
Telegram bot for providing gambling game signals with user management and premium features.
"""

import requests
import time
import threading
import statistics
import asyncio
import os
import math
import numpy as np
from datetime import datetime, timedelta
import pytz
import random
import logging

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
    from telegram.constants import ParseMode
    import telegram
except ImportError:
    import telegram
    from telegram import Bot, Update
    from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
    
    # For older version compatibility
    ContextTypes = None
    filters = Filters
    ParseMode = telegram.ParseMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
# Use environment variables for sensitive data with fallbacks for development
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7625816736:AAHsVVvFj7EF1soZopp56HvP1mhKh6x4sKA")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ExpertCasino123")
ADMIN_ID = os.getenv("ADMIN_ID", "8174450681")
API_URL = os.getenv("API_URL", "https://crash-gateway-orc-cr.gamedev-tech.cc/history?id_n=01961b11-3302-74d5-9609-fcce6c9a7843&id_i=077dee8d-c923-4c02-9bee-757573662e69&round_id=0197a7dc-e8c6-748e-bdf7-85dfc0e275a4")

# Supported countries with language and timezone information
COUNTRIES = {
    "CI": {"name": "Côte d'Ivoire", "lang": "fr", "timezone": "Africa/Abidjan"},
    "FR": {"name": "France", "lang": "fr", "timezone": "Europe/Paris"},
}

# Localized messages
MESSAGES = {
    "fr": {
        "choose_country": "🌍 Choisissez votre pays :",
        "welcome": "Bienvenue sur EXpPERT CASINO PRO 🚀",
        "join_channel": "👋 Pour accéder au bot, rejoins notre canal 👇",
        "not_joined": "❌ Tu dois d'abord rejoindre le canal.",
        "error_check": "❌ Erreur lors de la vérification. Réessaie.",
        "menu_prompt": "📋 Menu principal :",
    }
}

# Global data storage
USER_DATA = {}  # Stores user country preferences
SIGNAL_DATA = {}  # Stores user signal counts
TOURS = []  # Stores game rounds data

# === KEYBOARD LAYOUTS ===
def get_main_keyboard(user_id):
    """Generate main menu keyboard based on user permissions"""
    keyboard = [["📊 Signal", "💎 Premium"], ["👤 Mon compte"]]
    if str(user_id) == ADMIN_ID:
        keyboard.append(["🛠 Admin Panel", "📈 Statistiques"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Generate admin panel keyboard"""
    return ReplyKeyboardMarkup(
        [["➕ Ajouter Signaux", "➖ Réduit Signaux"], ["⛔ Désactiver Signaux"], ["🔙 Retour"]],
        resize_keyboard=True
    )

# === BOT COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show channel join prompt"""
    keyboard = [
        [InlineKeyboardButton("📢 Rejoindre le canal", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ Vérifier", callback_data="check_subscription")]
    ]
    await update.message.reply_text(
        MESSAGES["fr"]["join_channel"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify if user has joined the required channel"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if member.status in ["member", "administrator", "creator"]:
            await ask_country(query, context)
        else:
            await query.edit_message_text(MESSAGES["fr"]["not_joined"])
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}")
        await query.edit_message_text(MESSAGES["fr"]["error_check"])

async def ask_country(query_or_update, context: ContextTypes.DEFAULT_TYPE, lang="fr"):
    """Show country selection menu"""
    keyboard = [
        [InlineKeyboardButton(COUNTRIES[c]["name"], callback_data=f"country_{c}")] for c in COUNTRIES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = MESSAGES.get(lang, MESSAGES["fr"])["choose_country"]

    try:
        if hasattr(query_or_update, "edit_message_text"):
            await query_or_update.edit_message_text(text, reply_markup=reply_markup)
        else:
            await query_or_update.message.reply_text(text, reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Error in ask_country: {e}")
            raise

async def country_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle country selection and show welcome message"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    code = query.data.split("_")[1]
    
    # Store user's country preference
    USER_DATA[user_id] = code
    lang = COUNTRIES[code]["lang"]
    tz = pytz.timezone(COUNTRIES[code]["timezone"])
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    await query.edit_message_text(
        f"{MESSAGES.get(lang, MESSAGES['fr'])['welcome']}\n"
        f"🕓 Heure locale : {now}\n🌍 Pays : {COUNTRIES[code]['name']}"
    )
    
    # Show main menu
    await context.bot.send_message(
        chat_id=user_id,
        text=MESSAGES.get(lang, MESSAGES['fr'])['menu_prompt'],
        reply_markup=get_main_keyboard(user_id)
    )

async def mon_compte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user account information"""
    user = update.message.from_user
    signaux = SIGNAL_DATA.get(user.id, 0)
    await update.message.reply_text(
        f"👤 *Ton compte*\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Nom: {user.full_name}\n"
        f"📡 Signaux restants: {signaux}/10",
        parse_mode=ParseMode.MARKDOWN
    )

# === SIGNAL ANALYSIS FUNCTIONS ===
def extract_coefficients(tours):
    """Extract coefficient values from game rounds data"""
    coeffs = []
    for t in tours:
        # Try different possible keys for coefficient values
        for key in ("top_coefficient", "coefficient", "coef", "value"):
            if key in t:
                try:
                    coeffs.append(float(t[key]))
                    break
                except (ValueError, TypeError):
                    continue
    return coeffs

def analyse_signal(tours):
    """Analyze game data to generate standard signal predictions"""
    coeffs = [c for c in extract_coefficients(tours) if 2.1 <= c <= 7.0]
    if not coeffs:
        return None, None
    
    # Use median for stability and add some randomization
    coeff = round(statistics.median(coeffs), 2)
    assurance = round(random.uniform(1.7, min(4.0, coeff - 0.1)), 2)
    return coeff, assurance

def analyse_premium(tours):
    """Analyze game data to generate premium signal predictions"""
    coeffs = [c for c in extract_coefficients(tours) if 10 <= c <= 70]
    if not coeffs:
        return None, None
    
    # Use maximum value for premium signals
    coeff = round(max(coeffs), 2)
    assurance = round(coeff * 0.4, 2)
    return coeff, assurance

# === SIGNAL DELIVERY WITH LOADING ANIMATION ===
async def envoyer_avec_chargement(context, chat_id, analyse_func, is_premium, timezone):
    """Send signal with loading animation"""
    # Start loading animation
    msg = await context.bot.send_message(chat_id, "📡 Analyse en cours...\n[▒▒▒▒▒▒▒▒▒▒] 0%")
    barre = ["▒"] * 10
    
    # Animate loading bar
    for i in range(1, 11):
        barre[:i] = ["█"] * i
        pourcent = i * 10
        await asyncio.sleep(0.4)
        await msg.edit_text(f"📡 Analyse en cours...\n[{''.join(barre)}] {pourcent}%")

    # Analyze data and generate signal
    coeff, assurance = analyse_func(TOURS)
    if coeff is None:
        await context.bot.send_message(chat_id, "❌ Données insuffisantes pour faire une prédiction.")
        return

    now = datetime.now(timezone)
    
    if is_premium:
        # Premium signal format
        debut = (now + timedelta(minutes=7)).strftime("%H:%M")
        fin = (now + timedelta(minutes=8)).strftime("%H:%M")
        await context.bot.send_message(
            chat_id,
            f"💎 LUCKY JET PREMIUM SIGNAL\n"
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"┠ ◆ COEFFICIENT VISÉ : 🚀 x{coeff}\n"
            f"┠ ◆ 🔒 Assurance estimée : x{assurance}\n"
            f"┠ ◆ PLAGE HORAIRE      : 🕒 {debut} - {fin}\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Nombre de tours analysés : {len(TOURS)}\n"
            f"📌 Signal premium basé sur une analyse approfondie du cycle actuel."
        )
    else:
        # Standard signal format
        heure = (now + timedelta(minutes=5)).strftime("%H:%M")
        await context.bot.send_message(
            chat_id,
            f"🚀 LUCKY JET SIGNAL BOT\n"
            f"┏━━━━━━━━━━━━━━━\n"
            f"┠ ◆ COEFFICIENT : x{coeff}\n"
            f"┠ ◆ ASSURANCE   : x{assurance}\n"
            f"┠ ◆ HEURE       : {heure}\n"
            f"┗━━━━━━━━━━━━━━━\n"
            f"📊 Nombre de tours analysés : {len(TOURS)}"
        )

# === MENU BUTTON HANDLERS ===
async def bouton_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button presses"""
    text = update.message.text
    uid = update.message.from_user.id
    code_pays = USER_DATA.get(uid, "CI")
    tz = pytz.timezone(COUNTRIES.get(code_pays, COUNTRIES["CI"])["timezone"])

    if text == "📊 Signal":
        await envoyer_avec_chargement(context, update.effective_chat.id, analyse_signal, is_premium=False, timezone=tz)
    elif text == "💎 Premium":
        await envoyer_avec_chargement(context, update.effective_chat.id, analyse_premium, is_premium=True, timezone=tz)
    elif text == "📈 Statistiques":
        total = len(TOURS)
        derniers = extract_coefficients(TOURS[-5:])
        resume = "\n".join([f"➡️ {x}" for x in derniers]) if derniers else "Aucun tour."
        await update.message.reply_text(f"📊 Total de tours : {total}\n🎯 5 derniers :\n{resume}")
    elif text == "🛠 Admin Panel":
        if str(uid) == ADMIN_ID:
            await update.message.reply_text("🔧 Bienvenue dans le panneau admin.", reply_markup=get_admin_keyboard())
        else:
            await update.message.reply_text("❌ Accès refusé.")

# === ADMIN PANEL HANDLERS ===
async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel operations"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    # Verify admin access
    if str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ Accès refusé.")
        return

    admin_action = context.user_data.get("admin_action")

    if admin_action:
        # Process admin command input
        parts = text.strip().split()
        
        if admin_action in ("add", "reduce") and len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            target_id = int(parts[0])
            nombre = int(parts[1])
            current = SIGNAL_DATA.get(target_id, 0)
            
            if admin_action == "add":
                SIGNAL_DATA[target_id] = current + nombre
                await update.message.reply_text(f"✅ Ajouté {nombre} signaux à l'utilisateur `{target_id}`.", parse_mode=ParseMode.MARKDOWN)
            else:
                SIGNAL_DATA[target_id] = max(0, current - nombre)
                await update.message.reply_text(f"✅ Réduit {nombre} signaux à l'utilisateur `{target_id}`.", parse_mode=ParseMode.MARKDOWN)
            
            context.user_data.pop("admin_action")
            
        elif admin_action == "disable" and len(parts) == 1 and parts[0].isdigit():
            target_id = int(parts[0])
            SIGNAL_DATA[target_id] = 0
            await update.message.reply_text(f"⛔ Signaux désactivés pour l'utilisateur `{target_id}`.", parse_mode=ParseMode.MARKDOWN)
            context.user_data.pop("admin_action")
        else:
            await update.message.reply_text("❌ Format invalide.")
        
        return await update.message.reply_text("🔧 Retour au menu admin :", reply_markup=get_admin_keyboard())

    # Handle admin menu selections
    if text == "➕ Ajouter Signaux":
        context.user_data["admin_action"] = "add"
        await update.message.reply_text("📥 ID utilisateur et nombre (ex: `12345678 5`)", parse_mode=ParseMode.MARKDOWN)
    elif text == "➖ Réduit Signaux":
        context.user_data["admin_action"] = "reduce"
        await update.message.reply_text("📤 ID utilisateur et nombre (ex: `12345678 3`)", parse_mode=ParseMode.MARKDOWN)
    elif text == "⛔ Désactiver Signaux":
        context.user_data["admin_action"] = "disable"
        await update.message.reply_text("⛔ Envoie l'ID de l'utilisateur.", parse_mode=ParseMode.MARKDOWN)
    elif text == "🔙 Retour":
        await update.message.reply_text(MESSAGES["fr"]["menu_prompt"], reply_markup=get_main_keyboard(user_id))

# === API DATA FETCHING ===
def recuperer_tours():
    """Background task to fetch game data from API"""
    while True:
        try:
            response = requests.get(API_URL, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Add only new rounds to avoid duplicates
                    nouveaux = [t for t in data if t not in TOURS]
                    if nouveaux:
                        TOURS.extend(nouveaux)
                        logger.info(f"[API] Added {len(nouveaux)} new rounds. Total: {len(TOURS)}")
                        
                        # Keep only recent data to prevent memory issues
                        if len(TOURS) > 1000:
                            TOURS[:] = TOURS[-500:]
            else:
                logger.warning(f"[API] HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"[API] Error: {e}")
        
        time.sleep(10)  # Wait 10 seconds before next fetch

# === MAIN BOT FUNCTION ===
async def main():
    """Main function to start the Telegram bot"""
    # Start API data fetching in background thread
    api_thread = threading.Thread(target=recuperer_tours, daemon=True)
    api_thread.start()
    logger.info("API data fetching started")

    # Build and configure the bot application
    app = ApplicationBuilder().token(TOKEN).build()

    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    app.add_handler(CallbackQueryHandler(country_chosen, pattern="country_"))
    app.add_handler(MessageHandler(filters.Regex("^👤 Mon compte$"), mon_compte))
    app.add_handler(MessageHandler(filters.Regex("^(📊 Signal|💎 Premium|📈 Statistiques|🛠 Admin Panel)$"), bouton_placeholder))
    app.add_handler(MessageHandler(filters.Regex("^(➕ Ajouter Signaux|➖ Réduit Signaux|⛔ Désactiver Signaux|🔙 Retour)$"), admin_panel_handler))
    
    # Handle any remaining admin panel input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel_handler))

    logger.info("Starting Telegram bot polling...")
    
    # Start the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        # Keep the bot running
        await asyncio.Event().wait()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
