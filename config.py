#!/usr/bin/env python3
"""
Configuration settings for the Telegram Casino Signals Bot.
This file contains all configurable parameters and environment variable handling.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7625816736:AAHsVVvFj7EF1soZopp56HvP1mhKh6x4sKA")
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ExpertCasino123")
    ADMIN_ID = os.getenv("ADMIN_ID", "8174450681")
    
    # API Configuration
    API_URL = os.getenv("API_URL", "https://crash-gateway-orc-cr.gamedev-tech.cc/history?id_n=01961b11-3302-74d5-9609-fcce6c9a7843&id_i=077dee8d-c923-4c02-9bee-757573662e69&round_id=0197a7dc-e8c6-748e-bdf7-85dfc0e275a4")
    API_FETCH_INTERVAL = int(os.getenv("API_FETCH_INTERVAL", "10"))  # seconds
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # seconds
    
    # Web Server Configuration
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
    
    # Bot Configuration
    MAX_TOURS_STORED = int(os.getenv("MAX_TOURS_STORED", "1000"))
    CLEANUP_THRESHOLD = int(os.getenv("CLEANUP_THRESHOLD", "500"))
    
    # Signal Configuration
    STANDARD_SIGNAL_MIN_COEFF = float(os.getenv("STANDARD_SIGNAL_MIN_COEFF", "2.1"))
    STANDARD_SIGNAL_MAX_COEFF = float(os.getenv("STANDARD_SIGNAL_MAX_COEFF", "7.0"))
    PREMIUM_SIGNAL_MIN_COEFF = float(os.getenv("PREMIUM_SIGNAL_MIN_COEFF", "10.0"))
    PREMIUM_SIGNAL_MAX_COEFF = float(os.getenv("PREMIUM_SIGNAL_MAX_COEFF", "70.0"))
    
    # Timing Configuration
    STANDARD_SIGNAL_DELAY_MINUTES = int(os.getenv("STANDARD_SIGNAL_DELAY_MINUTES", "5"))
    PREMIUM_SIGNAL_START_DELAY_MINUTES = int(os.getenv("PREMIUM_SIGNAL_START_DELAY_MINUTES", "7"))
    PREMIUM_SIGNAL_END_DELAY_MINUTES = int(os.getenv("PREMIUM_SIGNAL_END_DELAY_MINUTES", "8"))
    
    # Loading Animation Configuration
    LOADING_ANIMATION_STEPS = int(os.getenv("LOADING_ANIMATION_STEPS", "10"))
    LOADING_ANIMATION_DELAY = float(os.getenv("LOADING_ANIMATION_DELAY", "0.4"))
    
    # User Configuration
    DEFAULT_SIGNAL_LIMIT = int(os.getenv("DEFAULT_SIGNAL_LIMIT", "10"))
    
    # Supported Countries
    COUNTRIES = {
        "CI": {
            "name": "Côte d'Ivoire", 
            "lang": "fr", 
            "timezone": "Africa/Abidjan",
            "flag": "🇨🇮"
        },
        "FR": {
            "name": "France", 
            "lang": "fr", 
            "timezone": "Europe/Paris",
            "flag": "🇫🇷"
        },
    }
    
    # Localized Messages
    MESSAGES = {
        "fr": {
            "choose_country": "🌍 Choisissez votre pays :",
            "welcome": "Bienvenue sur EXpPERT CASINO PRO 🚀",
            "join_channel": "👋 Pour accéder au bot, rejoins notre canal 👇",
            "not_joined": "❌ Tu dois d'abord rejoindre le canal.",
            "error_check": "❌ Erreur lors de la vérification. Réessaie.",
            "menu_prompt": "📋 Menu principal :",
            "insufficient_data": "❌ Données insuffisantes pour faire une prédiction.",
            "access_denied": "❌ Accès refusé.",
            "invalid_format": "❌ Format invalide.",
            "admin_welcome": "🔧 Bienvenue dans le panneau admin.",
            "signals_added": "✅ Ajouté {count} signaux à l'utilisateur `{user_id}`.",
            "signals_reduced": "✅ Réduit {count} signaux à l'utilisateur `{user_id}`.",
            "signals_disabled": "⛔ Signaux désactivés pour l'utilisateur `{user_id}`.",
            "admin_add_prompt": "📥 ID utilisateur et nombre (ex: `12345678 5`)",
            "admin_reduce_prompt": "📤 ID utilisateur et nombre (ex: `12345678 3`)",
            "admin_disable_prompt": "⛔ Envoie l'ID de l'utilisateur.",
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with more secure defaults for production
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
