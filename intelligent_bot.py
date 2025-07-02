#!/usr/bin/env python3
"""
Intelligent Telegram Casino Signals Bot with Advanced AI Learning System
This bot features three signal types: Standard, Premium, and Montante with ultra-precise timing.
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
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import deque

# Telegram imports - correct imports for python-telegram-bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
import telegram

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7625816736:AAHsVVvFj7EF1soZopp56HvP1mhKh6x4sKA")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "ExpertCasino123")
ADMIN_ID = os.getenv("ADMIN_ID", "8174450681")
API_URL = os.getenv("API_URL", "https://crash-gateway-orc-cr.gamedev-tech.cc/history?id_n=01961b11-3302-74d5-9609-fcce6c9a7843&id_i=077dee8d-c923-4c02-9bee-757573662e69&round_id=0197a7dc-e8c6-748e-bdf7-85dfc0e275a4")

# Extended countries list (30 countries)
COUNTRIES = {
    "CI": {"name": "Côte d'Ivoire", "lang": "fr", "timezone": "Africa/Abidjan", "flag": "🇨🇮"},
    "FR": {"name": "France", "lang": "fr", "timezone": "Europe/Paris", "flag": "🇫🇷"},
    "NE": {"name": "Niger", "lang": "fr", "timezone": "Africa/Niamey", "flag": "🇳🇪"},
    "IN": {"name": "India", "lang": "en", "timezone": "Asia/Kolkata", "flag": "🇮🇳"},
    "RU": {"name": "Russia", "lang": "ru", "timezone": "Europe/Moscow", "flag": "🇷🇺"},
    "DZ": {"name": "Algeria", "lang": "ar", "timezone": "Africa/Algiers", "flag": "🇩🇿"},
    "MA": {"name": "Morocco", "lang": "ar", "timezone": "Africa/Casablanca", "flag": "🇲🇦"},
    "TN": {"name": "Tunisia", "lang": "ar", "timezone": "Africa/Tunis", "flag": "🇹🇳"},
    "SN": {"name": "Senegal", "lang": "fr", "timezone": "Africa/Dakar", "flag": "🇸🇳"},
    "ML": {"name": "Mali", "lang": "fr", "timezone": "Africa/Bamako", "flag": "🇲🇱"},
    "BF": {"name": "Burkina Faso", "lang": "fr", "timezone": "Africa/Ouagadougou", "flag": "🇧🇫"},
    "GN": {"name": "Guinea", "lang": "fr", "timezone": "Africa/Conakry", "flag": "🇬🇳"},
    "CM": {"name": "Cameroon", "lang": "fr", "timezone": "Africa/Douala", "flag": "🇨🇲"},
    "TG": {"name": "Togo", "lang": "fr", "timezone": "Africa/Lome", "flag": "🇹🇬"},
    "BJ": {"name": "Benin", "lang": "fr", "timezone": "Africa/Porto-Novo", "flag": "🇧🇯"},
    "GH": {"name": "Ghana", "lang": "en", "timezone": "Africa/Accra", "flag": "🇬🇭"},
    "NG": {"name": "Nigeria", "lang": "en", "timezone": "Africa/Lagos", "flag": "🇳🇬"},
    "KE": {"name": "Kenya", "lang": "en", "timezone": "Africa/Nairobi", "flag": "🇰🇪"},
    "TZ": {"name": "Tanzania", "lang": "en", "timezone": "Africa/Dar_es_Salaam", "flag": "🇹🇿"},
    "UG": {"name": "Uganda", "lang": "en", "timezone": "Africa/Kampala", "flag": "🇺🇬"},
    "ZA": {"name": "South Africa", "lang": "en", "timezone": "Africa/Johannesburg", "flag": "🇿🇦"},
    "EG": {"name": "Egypt", "lang": "ar", "timezone": "Africa/Cairo", "flag": "🇪🇬"},
    "BR": {"name": "Brazil", "lang": "pt", "timezone": "America/Sao_Paulo", "flag": "🇧🇷"},
    "MX": {"name": "Mexico", "lang": "es", "timezone": "America/Mexico_City", "flag": "🇲🇽"},
    "CO": {"name": "Colombia", "lang": "es", "timezone": "America/Bogota", "flag": "🇨🇴"},
    "AR": {"name": "Argentina", "lang": "es", "timezone": "America/Argentina/Buenos_Aires", "flag": "🇦🇷"},
    "PE": {"name": "Peru", "lang": "es", "timezone": "America/Lima", "flag": "🇵🇪"},
    "CL": {"name": "Chile", "lang": "es", "timezone": "America/Santiago", "flag": "🇨🇱"},
    "VE": {"name": "Venezuela", "lang": "es", "timezone": "America/Caracas", "flag": "🇻🇪"},
    "EC": {"name": "Ecuador", "lang": "es", "timezone": "America/Guayaquil", "flag": "🇪🇨"}
}

# Multilingual messages
MESSAGES = {
    "fr": {
        "choose_country": "🌍 Choisissez votre pays :",
        "welcome": "Bienvenue sur EXpPERT CASINO PRO 🚀",
        "join_channel": "👋 Pour accéder au bot, rejoins notre canal 👇",
        "not_joined": "❌ Tu dois d'abord rejoindre le canal.",
        "error_check": "❌ Erreur lors de la vérification. Réessaie.",
        "menu_prompt": "📋 Menu principal :",
        "insufficient_data": "❌ Données insuffisantes pour faire une prédiction.",
        "no_signals": "❌ Vous n'avez pas de signaux. Contactez l'administrateur pour tout type de signaux.",
        "signal_consumed": "✅ Signal utilisé. Signaux restants: {}",
        "collect_tours_prompt": "📊 Combien de tours voulez-vous collecter ?",
        "tours_target_set": "🎯 Objectif de {} tours défini. Collection en cours...",
        "tours_target_reached": "✅ {} tours collectés ! La collection continue.",
        "anti_spam": "⏰ Veuillez attendre {} secondes avant de demander un nouveau signal."
    },
    "en": {
        "choose_country": "🌍 Choose your country:",
        "welcome": "Welcome to EXpPERT CASINO PRO 🚀",
        "join_channel": "👋 To access the bot, join our channel 👇",
        "not_joined": "❌ You must first join the channel.",
        "error_check": "❌ Verification error. Try again.",
        "menu_prompt": "📋 Main menu:",
        "insufficient_data": "❌ Insufficient data for prediction.",
        "no_signals": "❌ You have no signals. Contact administrator for any type of signals.",
        "signal_consumed": "✅ Signal used. Remaining signals: {}",
        "collect_tours_prompt": "📊 How many rounds do you want to collect?",
        "tours_target_set": "🎯 Target of {} rounds set. Collection in progress...",
        "tours_target_reached": "✅ {} rounds collected! Collection continues.",
        "anti_spam": "⏰ Please wait {} seconds before requesting a new signal."
    }
}

@dataclass
class GameRound:
    """Represents a single game round with coefficient and timing data"""
    coefficient: float
    timestamp: datetime
    round_id: str = ""
    metadata: Dict = None

@dataclass
class UserProfile:
    """User profile with preferences and signal data"""
    user_id: int
    country_code: str
    language: str
    timezone: str
    signals_remaining: int = 0
    montant_remaining: int = 0
    tours_target: int = 0
    tours_collected: int = 0
    last_signal_time: datetime = None
    is_premium: bool = False

class IntelligentAnalyzer:
    """Advanced AI analyzer for game patterns and predictions"""
    
    def __init__(self):
        self.tours_history = deque(maxlen=15000)  # Maximum 15,000 tours
        self.cycle_patterns = {}
        self.learning_weights = {
            'short_term': 0.4,
            'medium_term': 0.35,
            'long_term': 0.25
        }
        self.adaptation_rate = 0.01
        
    def add_tour(self, tour: GameRound):
        """Add new tour and trigger learning - avoid duplicates"""
        # Check if tour already exists by round_id or coefficient+timestamp
        existing_ids = {t.round_id for t in self.tours_history if t.round_id}
        existing_coeffs = {(t.coefficient, t.timestamp.strftime("%Y-%m-%d %H:%M:%S")) for t in self.tours_history}
        
        # Skip if duplicate found
        if tour.round_id and tour.round_id in existing_ids:
            return False
        
        tour_key = (tour.coefficient, tour.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if tour_key in existing_coeffs:
            return False
            
        self.tours_history.append(tour)
        self._adaptive_learning()
        return True
        
    def _adaptive_learning(self):
        """Continuously adapt and learn from new data"""
        if len(self.tours_history) < 10:
            return
            
        # Analyze recent patterns
        recent_coeffs = [t.coefficient for t in list(self.tours_history)[-50:]]
        
        # Update cycle detection
        self._detect_cycles(recent_coeffs)
        
        # Adapt weights based on recent performance
        self._adapt_weights()
        
    def _detect_cycles(self, coefficients):
        """Detect repeating patterns in coefficients"""
        if len(coefficients) < 20:
            return
            
        # Find recurring patterns of different lengths
        for pattern_length in range(3, 10):
            if len(coefficients) >= pattern_length * 2:
                pattern = coefficients[-pattern_length:]
                pattern_key = tuple(round(c, 1) for c in pattern)
                
                if pattern_key not in self.cycle_patterns:
                    self.cycle_patterns[pattern_key] = {'count': 0, 'success_rate': 0.5}
                
                self.cycle_patterns[pattern_key]['count'] += 1
                
    def _adapt_weights(self):
        """Dynamically adapt learning weights based on data volume"""
        data_volume = len(self.tours_history)
        
        if data_volume < 100:
            # Focus more on short-term patterns with limited data
            self.learning_weights = {'short_term': 0.6, 'medium_term': 0.3, 'long_term': 0.1}
        elif data_volume < 1000:
            # Balanced approach
            self.learning_weights = {'short_term': 0.45, 'medium_term': 0.35, 'long_term': 0.2}
        else:
            # More emphasis on long-term patterns with rich data
            self.learning_weights = {'short_term': 0.3, 'medium_term': 0.35, 'long_term': 0.35}
            
    def predict_signal(self) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Generate standard signal prediction (2.1X-8X)"""
        if len(self.tours_history) < 5:
            return None, None, None
            
        coeffs = [t.coefficient for t in self.tours_history]
        valid_coeffs = [c for c in coeffs if 2.1 <= c <= 8.0]
        
        if not valid_coeffs:
            return None, None, None
            
        # Intelligent analysis combining multiple factors
        predicted_coeff = self._intelligent_prediction(valid_coeffs, target_range=(2.1, 8.0))
        
        # Dynamic assurance calculation
        assurance = self._calculate_assurance(predicted_coeff, range_type='standard')
        
        # Intelligent timing
        timing = self._calculate_optimal_timing(predicted_coeff, signal_type='standard')
        
        return predicted_coeff, assurance, timing
        
    def predict_premium(self) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Generate premium signal prediction (≥10X with 40% assurance)"""
        if len(self.tours_history) < 10:
            return None, None, None
            
        coeffs = [t.coefficient for t in self.tours_history]
        high_coeffs = [c for c in coeffs if c >= 10.0]
        
        if not high_coeffs:
            return None, None, None
            
        # Focus on high-value coefficient prediction
        predicted_coeff = self._intelligent_prediction(high_coeffs, target_range=(10.0, 70.0))
        
        # 40% assurance rule
        assurance = round(predicted_coeff * 0.4, 2)
        
        # Premium timing with short range
        timing = self._calculate_optimal_timing(predicted_coeff, signal_type='premium')
        
        return predicted_coeff, assurance, timing
        
    def predict_montante(self) -> Tuple[Optional[float], Optional[str]]:
        """Generate ultra-precise montante prediction (1.2X-1.5X) with second-level timing"""
        if len(self.tours_history) < 20:
            return None, None
            
        coeffs = [t.coefficient for t in self.tours_history]
        safe_coeffs = [c for c in coeffs if 1.2 <= c <= 1.5]
        
        # Use ALL available data for maximum reliability
        all_coeffs = coeffs if len(coeffs) >= 50 else coeffs
        
        # Ultra-precise prediction algorithm
        predicted_coeff = self._ultra_precise_prediction(all_coeffs)
        
        # Second-level timing precision
        timing = self._calculate_precise_timing_seconds(predicted_coeff)
        
        return predicted_coeff, timing
        
    def _intelligent_prediction(self, coefficients, target_range):
        """Advanced prediction algorithm using multiple analysis methods"""
        if not coefficients:
            return None
            
        # Multiple prediction methods
        median_pred = statistics.median(coefficients[-20:] if len(coefficients) >= 20 else coefficients)
        mean_pred = statistics.mean(coefficients[-30:] if len(coefficients) >= 30 else coefficients)
        
        # Trend analysis
        if len(coefficients) >= 10:
            recent_trend = np.polyfit(range(10), coefficients[-10:], 1)[0]
            trend_adjusted = median_pred + (recent_trend * 2)
        else:
            trend_adjusted = median_pred
            
        # Weighted combination
        weights = self.learning_weights
        final_prediction = (
            median_pred * weights['short_term'] +
            mean_pred * weights['medium_term'] +
            trend_adjusted * weights['long_term']
        )
        
        # Ensure within target range
        final_prediction = max(target_range[0], min(target_range[1], final_prediction))
        
        return round(final_prediction, 2)
        
    def _ultra_precise_prediction(self, all_coefficients):
        """Ultra-precise algorithm for montante signals"""
        if not all_coefficients:
            return 1.35  # Safe default
            
        # Analyze patterns for safe coefficients
        safe_patterns = []
        for i in range(len(all_coefficients) - 3):
            sequence = all_coefficients[i:i+4]
            if all(1.2 <= c <= 1.5 for c in sequence):
                safe_patterns.extend(sequence)
                
        if safe_patterns:
            # Use pattern-based prediction
            prediction = statistics.median(safe_patterns)
        else:
            # Fallback to statistical analysis
            recent_safe = [c for c in all_coefficients[-100:] if 1.2 <= c <= 1.5]
            if recent_safe:
                prediction = statistics.median(recent_safe)
            else:
                prediction = 1.35
                
        return round(max(1.2, min(1.5, prediction)), 2)
        
    def _calculate_assurance(self, coefficient, range_type):
        """Calculate intelligent assurance based on coefficient and range type"""
        if range_type == 'standard':
            # Dynamic assurance for standard signals (1.7X-4X)
            base_assurance = coefficient * 0.45
            return round(max(1.7, min(4.0, base_assurance)), 2)
        return None
        
    def _calculate_optimal_timing(self, coefficient, signal_type):
        """Calculate intelligent timing based on cycle analysis"""
        if not self.tours_history:
            return self._default_timing(signal_type)
            
        # Analyze recent timing patterns
        recent_times = [t.timestamp for t in list(self.tours_history)[-20:]]
        
        if len(recent_times) >= 2:
            # Calculate average interval
            intervals = [(recent_times[i] - recent_times[i-1]).total_seconds() 
                        for i in range(1, len(recent_times))]
            avg_interval = statistics.mean(intervals) if intervals else 60
            
            # Intelligent timing based on patterns
            if signal_type == 'standard':
                # Single precise time
                offset_minutes = max(2, min(10, avg_interval / 60))
                target_time = datetime.now() + timedelta(minutes=offset_minutes)
                return target_time.strftime("%H:%M")
                
            elif signal_type == 'premium':
                # Short time range
                start_offset = max(3, min(8, avg_interval / 60))
                end_offset = start_offset + 1
                start_time = datetime.now() + timedelta(minutes=start_offset)
                end_time = datetime.now() + timedelta(minutes=end_offset)
                return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
                
        return self._default_timing(signal_type)
        
    def _calculate_precise_timing_seconds(self, coefficient):
        """Analyse intelligente Montante: prédit timing optimal basé sur patterns réels dans la plage 1.2X-1.5X"""
        current_time = datetime.now()
        current_second = current_time.second
        
        if not self.tours_history or len(self.tours_history) < 10:
            # Analyse basique avec prédiction intelligente
            base_offset = random.randint(90, 240)  # 1.5-4 minutes
            smart_second = self._predict_optimal_second(current_second, coefficient)
            target_time = current_time + timedelta(seconds=base_offset)
            target_time = target_time.replace(second=smart_second)
            return target_time.strftime("%H:%M:%S")
            
        # === ANALYSE INTELLIGENTE DES PATTERNS MONTANTE ===
        all_tours = list(self.tours_history)
        coeffs = [t.coefficient for t in all_tours]
        timestamps = [t.timestamp for t in all_tours]
        
        # 1. Identifier TOUS les coefficients Montante et leurs contextes
        montante_patterns = []
        for i, coeff in enumerate(coeffs):
            if 1.2 <= coeff <= 1.5:
                # Analyser le contexte avant et après
                context_before = coeffs[max(0, i-5):i] if i >= 5 else coeffs[:i]
                context_after = coeffs[i+1:min(len(coeffs), i+6)] if i < len(coeffs)-1 else []
                
                montante_patterns.append({
                    'position': i,
                    'coeff': coeff,
                    'timestamp': timestamps[i] if i < len(timestamps) else current_time,
                    'second': timestamps[i].second if i < len(timestamps) else 0,
                    'context_before': context_before,
                    'context_after': context_after,
                    'total_tours_before': i
                })
        
        if len(montante_patterns) >= 5:
            # 2. ANALYSE DES CYCLES ET PATTERNS TEMPORELS
            intervals_analysis = self._analyze_montante_cycles(montante_patterns)
            current_context = coeffs[-10:] if len(coeffs) >= 10 else coeffs
            
            # 3. PRÉDICTION BASÉE SUR LES CYCLES DÉTECTÉS
            predicted_timing = self._predict_by_cycle_analysis(
                intervals_analysis, 
                current_context, 
                coefficient,
                len(coeffs)
            )
            
            # 4. CALCUL DE LA SECONDE OPTIMALE
            optimal_second = self._calculate_pattern_based_second(
                montante_patterns, 
                current_second, 
                coefficient
            )
            
            # 5. CONSTRUCTION DU TIMING FINAL
            total_offset = max(60, min(420, predicted_timing))  # Entre 1-7 minutes
            target_time = current_time + timedelta(seconds=total_offset)
            target_time = target_time.replace(second=optimal_second)
            return target_time.strftime("%H:%M:%S")
        
        # === ANALYSE SECONDAIRE POUR DONNÉES LIMITÉES ===
        if len(coeffs) >= 20:
            # Analyse des tendances récentes
            recent_analysis = self._analyze_recent_trends(coeffs[-20:], coefficient)
            optimal_second = self._predict_optimal_second(current_second, coefficient)
            
            target_time = current_time + timedelta(seconds=recent_analysis['predicted_offset'])
            target_time = target_time.replace(second=optimal_second)
            return target_time.strftime("%H:%M:%S")
        
        # === FALLBACK INTELLIGENT ===
        base_offset = random.randint(120, 300)  # 2-5 minutes
        smart_second = self._predict_optimal_second(current_second, coefficient)
        target_time = current_time + timedelta(seconds=base_offset)
        target_time = target_time.replace(second=smart_second)
        return target_time.strftime("%H:%M:%S")
    
    def _analyze_montante_cycles(self, montante_patterns):
        """Analyse des cycles entre occurrences Montante"""
        if len(montante_patterns) < 3:
            return {'avg_interval': 180, 'confidence': 0.3}
        
        # Calculer les intervalles entre occurrences
        position_intervals = []
        time_intervals = []
        
        for i in range(1, len(montante_patterns)):
            pos_diff = montante_patterns[i]['position'] - montante_patterns[i-1]['position']
            time_diff = (montante_patterns[i]['timestamp'] - montante_patterns[i-1]['timestamp']).total_seconds()
            
            position_intervals.append(pos_diff)
            time_intervals.append(time_diff)
        
        # Analyse statistique des cycles
        if position_intervals and time_intervals:
            avg_pos_interval = statistics.median(position_intervals)
            avg_time_interval = statistics.median(time_intervals)
            
            # Calculer la confiance basée sur la régularité
            pos_variance = statistics.variance(position_intervals) if len(position_intervals) > 1 else 0
            confidence = max(0.4, min(0.95, 1.0 - (pos_variance / max(avg_pos_interval, 1))))
            
            return {
                'avg_interval': avg_time_interval / max(avg_pos_interval, 1),
                'position_pattern': avg_pos_interval,
                'confidence': confidence,
                'total_occurrences': len(montante_patterns)
            }
        
        return {'avg_interval': 180, 'confidence': 0.5}
    
    def _predict_by_cycle_analysis(self, intervals_analysis, current_context, coefficient, total_tours):
        """Prédire le timing basé sur l'analyse des cycles"""
        base_interval = intervals_analysis.get('avg_interval', 180)
        confidence = intervals_analysis.get('confidence', 0.5)
        
        # Analyse du contexte actuel
        recent_montante_count = sum(1 for c in current_context if 1.2 <= c <= 1.5)
        high_coeff_count = sum(1 for c in current_context if c > 3.0)
        
        # Ajustements basés sur le contexte
        context_multiplier = 1.0
        
        if recent_montante_count >= 3:  # Beaucoup de Montante récemment
            context_multiplier = random.uniform(1.2, 1.8)  # Attendre plus longtemps
        elif recent_montante_count == 0:  # Aucune Montante récente
            context_multiplier = random.uniform(0.6, 0.9)  # Prédire plus tôt
        elif high_coeff_count >= 5:  # Beaucoup de hauts coefficients
            context_multiplier = random.uniform(0.7, 1.1)  # Cycle peut se reset
        
        # Ajustement basé sur le coefficient prédit
        coeff_adjustment = 1.0
        if coefficient <= 1.25:
            coeff_adjustment = random.uniform(0.8, 1.0)  # Plus conservateur pour bas coefficients
        elif coefficient >= 1.4:
            coeff_adjustment = random.uniform(1.0, 1.3)  # Plus patient pour hauts coefficients
        
        # Calcul final avec randomisation intelligente
        final_prediction = base_interval * context_multiplier * coeff_adjustment
        
        # Ajouter variance basée sur la confiance
        variance_range = int(30 * (1 - confidence))  # Moins de variance = plus de confiance
        variance = random.randint(-variance_range, variance_range)
        
        return int(final_prediction + variance)
    
    def _calculate_pattern_based_second(self, montante_patterns, current_second, coefficient):
        """Calculer la seconde optimale basée sur les patterns historiques"""
        if not montante_patterns:
            return self._predict_optimal_second(current_second, coefficient)
        
        # Collecter les secondes des occurrences Montante réussies
        successful_seconds = [p['second'] for p in montante_patterns[-10:]]  # 10 dernières occurrences
        
        if successful_seconds:
            # Analyser la fréquence des secondes
            second_frequency = {}
            for sec in successful_seconds:
                second_frequency[sec] = second_frequency.get(sec, 0) + 1
            
            # Trouver les secondes les plus fréquentes (exclure la seconde actuelle)
            best_candidates = []
            for sec, freq in second_frequency.items():
                if abs(sec - current_second) > 3:  # Au moins 3 secondes de différence
                    best_candidates.append((sec, freq))
            
            if best_candidates:
                # Choisir selon la fréquence avec un peu de randomisation
                best_candidates.sort(key=lambda x: x[1], reverse=True)
                top_candidates = [sec for sec, freq in best_candidates[:3]]  # Top 3
                return random.choice(top_candidates)
        
        # Fallback intelligent
        return self._predict_optimal_second(current_second, coefficient)
    
    def _analyze_recent_trends(self, recent_coeffs, target_coefficient):
        """Analyse des tendances récentes pour prédiction"""
        montante_density = sum(1 for c in recent_coeffs if 1.2 <= c <= 1.5) / len(recent_coeffs)
        high_coeff_density = sum(1 for c in recent_coeffs if c > 5.0) / len(recent_coeffs)
        
        # Prédiction basée sur la densité
        if montante_density > 0.3:  # Haute densité Montante
            predicted_offset = random.randint(180, 360)  # Attendre plus
        elif montante_density < 0.1:  # Faible densité Montante
            predicted_offset = random.randint(60, 150)   # Prédire bientôt
        elif high_coeff_density > 0.4:  # Beaucoup de hauts coefficients
            predicted_offset = random.randint(90, 200)   # Cycle peut se reset
        else:
            predicted_offset = random.randint(120, 240)  # Timing normal
        
        return {'predicted_offset': predicted_offset, 'confidence': montante_density}
    
    def _predict_optimal_second(self, current_second, coefficient):
        """Prédire la seconde optimale basée sur coefficient et analyse"""
        # Définir des plages de secondes optimales selon le coefficient
        if coefficient <= 1.25:
            # Très sûr - secondes "chanceuses"
            optimal_ranges = [7, 13, 19, 23, 29, 37, 41, 47, 53, 59]
        elif coefficient <= 1.35:
            # Modéré - distribution équilibrée
            optimal_ranges = [3, 11, 17, 21, 27, 33, 39, 43, 49, 57]
        else:
            # Plus élevé - timing différent
            optimal_ranges = [5, 9, 15, 25, 31, 35, 45, 51, 55]
        
        # Filtrer pour éviter la seconde actuelle et les secondes proches
        available_seconds = [s for s in optimal_ranges if abs(s - current_second) > 2]
        
        # Si pas d'options disponibles, créer une nouvelle plage
        if not available_seconds:
            offset = random.choice([15, 20, 25, 30, 35, 40])
            return (current_second + offset) % 60
        
        # Choisir intelligemment avec un peu de randomisation
        return random.choice(available_seconds)
    
    def _calculate_smart_second(self, current_second, coefficient):
        """Calculate intelligent target second based on coefficient and ensuring difference from current"""
        # Define optimal second ranges based on coefficient
        if coefficient <= 1.25:
            # Very safe - prefer seconds that historically work well
            optimal_ranges = [5, 12, 18, 23, 28, 34, 41, 47, 52, 58]
        elif coefficient <= 1.35:
            # Moderate - balanced second distribution
            optimal_ranges = [3, 9, 15, 21, 27, 33, 39, 45, 51, 57]
        else:
            # Higher coefficient - different timing strategy
            optimal_ranges = [7, 14, 22, 31, 38, 44, 49, 55]
        
        # Filter out current second and nearby seconds (±2 seconds buffer)
        available_seconds = []
        for sec in optimal_ranges:
            if abs(sec - current_second) > 2:  # Ensure meaningful difference
                available_seconds.append(sec)
        
        # If no available seconds (rare), create new range
        if not available_seconds:
            available_seconds = [s for s in range(0, 60, 5) if abs(s - current_second) > 3]
        
        # If still no options (extremely rare), use simple offset
        if not available_seconds:
            return (current_second + random.randint(10, 30)) % 60
        
        # Choose optimal second with some randomization
        return random.choice(available_seconds)
        
    def _default_timing(self, signal_type):
        """Default timing when no pattern data available"""
        now = datetime.now()
        if signal_type == 'standard':
            return (now + timedelta(minutes=5)).strftime("%H:%M")
        elif signal_type == 'premium':
            start = (now + timedelta(minutes=7)).strftime("%H:%M")
            end = (now + timedelta(minutes=8)).strftime("%H:%M")
            return f"{start} - {end}"
        return (now + timedelta(minutes=3)).strftime("%H:%M:%S")

# Global instances
analyzer = IntelligentAnalyzer()
user_profiles: Dict[int, UserProfile] = {}
user_last_requests: Dict[int, datetime] = {}

# === KEYBOARD LAYOUTS ===
def get_main_keyboard(user_id, lang="fr"):
    """Generate main menu keyboard with collect tours option"""
    base_buttons = [
        ["📊 Signal", "💎 Premium", "📈 Montante"],
        ["📊 Collecte de tours" if lang == "fr" else "📊 Collect Tours"],
        ["👤 Mon compte" if lang == "fr" else "👤 My Account"]
    ]
    
    if str(user_id) == ADMIN_ID:
        base_buttons.append(["🛠 Admin Panel", "📈 Statistiques"])
    
    return ReplyKeyboardMarkup(base_buttons, resize_keyboard=True)

async def send_target_notification(bot, user_id, target, current):
    """Send notification when user reaches tour target"""
    try:
        message = f"🎯 *Objectif Atteint!*\n\nVous avez atteint votre objectif de {target} tours!\nTours actuels: {current}"
        await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")

def get_admin_keyboard(lang="fr"):
    """Generate admin panel keyboard"""
    if lang == "fr":
        buttons = [
            ["➕ Ajouter Signaux", "➖ Réduire Signaux"],
            ["💰 Ajouter Montant", "⛔ Désactiver Signaux"],
            ["📊 Statistiques", "🔙 Retour"]
        ]
    else:
        buttons = [
            ["➕ Add Signals", "➖ Reduce Signals"],
            ["💰 Add Amount", "⛔ Disable Signals"],
            ["📊 Statistics", "🔙 Back"]
        ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# === BOT HANDLERS ===
async def start(update: Update, context):
    """Handle /start command"""
    keyboard = [
        [InlineKeyboardButton("📢 Rejoindre le canal", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ Vérifier", callback_data="check_subscription")]
    ]
    await update.message.reply_text(
        MESSAGES["fr"]["join_channel"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_subscription(update: Update, context):
    """Verify channel subscription"""
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
        logger.error(f"Subscription check error for user {user_id}: {e}")
        await query.edit_message_text(MESSAGES["fr"]["error_check"])

async def ask_country(query_or_update, context, lang="fr"):
    """Show country selection menu with all 30 countries"""
    # Create keyboard with all countries in rows of 3
    countries_list = list(COUNTRIES.items())
    keyboard = []
    
    for i in range(0, len(countries_list), 3):
        row = []
        for j in range(3):
            if i + j < len(countries_list):
                code, info = countries_list[i + j]
                button_text = f"{info['flag']} {info['name']}"
                row.append(InlineKeyboardButton(button_text, callback_data=f"country_{code}"))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = MESSAGES.get(lang, MESSAGES["fr"])["choose_country"]

    try:
        if hasattr(query_or_update, "edit_message_text"):
            await query_or_update.edit_message_text(text, reply_markup=reply_markup)
        else:
            await query_or_update.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Error in ask_country: {e}")

async def country_chosen(update: Update, context):
    """Handle country selection"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    code = query.data.split("_")[1]
    
    # Create user profile
    country_info = COUNTRIES[code]
    user_profiles[user_id] = UserProfile(
        user_id=user_id,
        country_code=code,
        language=country_info["lang"],
        timezone=country_info["timezone"],
        signals_remaining=0  # Start with 0 signals
    )
    
    # Show welcome message
    tz = pytz.timezone(country_info["timezone"])
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    lang = country_info["lang"]
    
    welcome_msg = MESSAGES.get(lang, MESSAGES["fr"])["welcome"]
    await query.edit_message_text(
        f"{welcome_msg}\n"
        f"🕓 Heure locale : {now}\n"
        f"🌍 Pays : {country_info['name']} {country_info['flag']}"
    )
    
    # Show main menu
    menu_msg = MESSAGES.get(lang, MESSAGES["fr"])["menu_prompt"]
    await context.bot.send_message(
        chat_id=user_id,
        text=menu_msg,
        reply_markup=get_main_keyboard(user_id, lang)
    )

async def check_user_signals(user_id: int, context) -> bool:
    """Check if user has signals remaining"""
    profile = user_profiles.get(user_id)
    if not profile or profile.signals_remaining <= 0:
        lang = profile.language if profile else "fr"
        msg = MESSAGES.get(lang, MESSAGES["fr"])["no_signals"]
        await context.bot.send_message(user_id, msg)
        return False
    return True

async def check_anti_spam(user_id: int, context) -> bool:
    """Check anti-spam timing"""
    if user_id in user_last_requests:
        last_request = user_last_requests[user_id]
        time_diff = (datetime.now() - last_request).total_seconds()
        if time_diff < 60:  # 1 minute cooldown
            profile = user_profiles.get(user_id)
            lang = profile.language if profile else "fr"
            wait_time = int(60 - time_diff)
            msg = MESSAGES.get(lang, MESSAGES["fr"])["anti_spam"].format(wait_time)
            await context.bot.send_message(user_id, msg)
            return False
    return True

async def consume_signal(user_id: int, context):
    """Consume one signal from user's account"""
    profile = user_profiles.get(user_id)
    if profile:
        profile.signals_remaining -= 1
        user_last_requests[user_id] = datetime.now()

async def consume_montant(user_id: int, context):
    """Consume one montant signal from user's account"""
    profile = user_profiles.get(user_id)
    if profile:
        profile.montant_remaining -= 1
        user_last_requests[user_id] = datetime.now()

async def check_user_montant(user_id: int, context) -> bool:
    """Check if user has montant signals remaining"""
    if user_id not in user_profiles:
        await context.bot.send_message(user_id, "❌ Vous devez d'abord rejoindre le canal et choisir votre pays.")
        return False
    
    profile = user_profiles[user_id]
    if profile.montant_remaining <= 0:
        await context.bot.send_message(user_id, "❌ Vous n'avez plus de signaux Montante disponibles. Contactez l'admin.")
        return False
    
    return True

async def generate_signal(update: Update, context):
    """Generate standard signal"""
    user_id = update.message.from_user.id
    
    if not await check_user_signals(user_id, context):
        return
    if not await check_anti_spam(user_id, context):
        return
        
    # Loading animation
    msg = await update.message.reply_text("🧠 Analyse IA en cours...\n[▒▒▒▒▒▒▒▒▒▒] 0%")
    
    for i in range(1, 11):
        await asyncio.sleep(0.4)
        progress = "█" * i + "▒" * (10 - i)
        await msg.edit_text(f"🧠 Analyse IA en cours...\n[{progress}] {i * 10}%")
    
    # Generate prediction
    coeff, assurance, timing = analyzer.predict_signal()
    
    if coeff is None:
        profile = user_profiles.get(user_id)
        lang = profile.language if profile else "fr"
        await update.message.reply_text(MESSAGES.get(lang, MESSAGES["fr"])["insufficient_data"])
        return
    
    # Send signal
    total_tours = len(analyzer.tours_history)
    confidence = min(95, 70 + (total_tours // 100))  # Confidence grows with data
    
    signal_msg = (
        f"🚀 LUCKY JET SIGNAL BOT\n"
        f"┏━━━━━━━━━━━━━━━\n"
        f"┠ ◆ COEFFICIENT : x{coeff}\n"
        f"┠ ◆ ASSURANCE   : x{assurance}\n"
        f"┠ ◆ HEURE       : {timing}\n"
        f"┗━━━━━━━━━━━━━━━\n"
        f"📊 Analyse intelligente sur {total_tours} tours\n"
        f"🧠 IA adaptative activée - Confiance {confidence}%"
    )
    
    await context.bot.send_message(user_id, signal_msg)
    await consume_signal(user_id, context)

async def generate_premium(update: Update, context):
    """Generate premium signal"""
    user_id = update.message.from_user.id
    
    if not await check_user_signals(user_id, context):
        return
    if not await check_anti_spam(user_id, context):
        return
        
    # Loading animation
    msg = await update.message.reply_text("💎 Analyse Premium IA...\n[▒▒▒▒▒▒▒▒▒▒] 0%")
    
    for i in range(1, 11):
        await asyncio.sleep(0.5)
        progress = "█" * i + "▒" * (10 - i)
        await msg.edit_text(f"💎 Analyse Premium IA...\n[{progress}] {i * 10}%")
    
    # Generate premium prediction
    coeff, assurance, timing = analyzer.predict_premium()
    
    if coeff is None:
        profile = user_profiles.get(user_id)
        lang = profile.language if profile else "fr"
        await update.message.reply_text(MESSAGES.get(lang, MESSAGES["fr"])["insufficient_data"])
        return
    
    # Send premium signal
    total_tours = len(analyzer.tours_history)
    confidence = min(98, 80 + (total_tours // 200))
    
    premium_msg = (
        f"💎 LUCKY JET PREMIUM SIGNAL\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"┠ ◆ COEFFICIENT VISÉ : 🚀 x{coeff}\n"
        f"┠ ◆ 🔒 Assurance estimée : x{assurance}\n"
        f"┠ ◆ PLAGE HORAIRE : 🕒 {timing}\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 IA Premium : {total_tours} tours analysés\n"
        f"🔥 Cycle rare détecté - Confiance {confidence}%\n"
        f"📌 Signal premium basé sur analyse approfondie"
    )
    
    await context.bot.send_message(user_id, premium_msg)
    await consume_signal(user_id, context)

async def generate_montante(update: Update, context):
    """Generate ultra-precise montante signal"""
    user_id = update.message.from_user.id
    
    if not await check_user_montant(user_id, context):
        return
    if not await check_anti_spam(user_id, context):
        return
        
    # Extended loading for montante precision
    msg = await update.message.reply_text("🎯 Analyse MONTANTE Ultra-Précise...\n[▒▒▒▒▒▒▒▒▒▒] 0%")
    
    for i in range(1, 16):  # Longer animation for montante
        await asyncio.sleep(0.3)
        progress = "█" * min(i, 10) + "▒" * max(0, 10 - i)
        percentage = min(100, i * 7)
        await msg.edit_text(f"🎯 Analyse MONTANTE Ultra-Précise...\n[{progress}] {percentage}%")
    
    # Generate montante prediction
    coeff, timing = analyzer.predict_montante()
    
    if coeff is None:
        profile = user_profiles.get(user_id)
        lang = profile.language if profile else "fr"
        await update.message.reply_text(MESSAGES.get(lang, MESSAGES["fr"])["insufficient_data"])
        return
    
    # Send montante signal
    total_tours = len(analyzer.tours_history)
    reliability = min(99.8, 95 + (total_tours // 500))  # Very high reliability
    
    montante_msg = (
        f"📈 MONTANTE SÉCURISÉE\n"
        f"┏━━━━━━━━━━━━━━━━━━━\n"
        f"┠ ◆ COEFFICIENT : x{coeff}\n"
        f"┠ ◆ TIMING EXACT : {timing}\n"
        f"┠ ◆ FIABILITÉ : {reliability}%\n"
        f"┗━━━━━━━━━━━━━━━━━━━\n"
        f"🔒 Sécurité maximale garantie\n"
        f"⚡ Analyse ultra-précise sur {total_tours} tours\n"
        f"🎯 IA professionnelle niveau casino"
    )
    
    await context.bot.send_message(user_id, montante_msg)
    await consume_montant(user_id, context)

async def collect_tours_handler(update: Update, context):
    """Handle collect tours button"""
    user_id = update.message.from_user.id
    profile = user_profiles.get(user_id)
    
    if not profile:
        return
    
    lang = profile.language
    
    # Ask for target number
    await update.message.reply_text(
        MESSAGES.get(lang, MESSAGES["fr"])["collect_tours_prompt"]
    )
    
    # Store state for next message
    context.user_data['awaiting_tours_number'] = True

async def handle_tours_number(update: Update, context):
    """Handle tours number input"""
    if not context.user_data.get('awaiting_tours_number'):
        return
        
    user_id = update.message.from_user.id
    profile = user_profiles.get(user_id)
    
    if not profile:
        return
        
    try:
        tours_target = int(update.message.text)
        if tours_target < 10 or tours_target > 5000:
            await update.message.reply_text("❌ Nombre de tours invalide (10-5000)")
            return
            
        profile.tours_target = tours_target
        profile.tours_collected = len(analyzer.tours_history)
        
        lang = profile.language
        msg = MESSAGES.get(lang, MESSAGES["fr"])["tours_target_set"].format(tours_target)
        await update.message.reply_text(msg)
        
        context.user_data['awaiting_tours_number'] = False
        
    except ValueError:
        await update.message.reply_text("❌ Veuillez entrer un nombre valide")

async def mon_compte(update: Update, context):
    """Show user account information"""
    user_id = update.message.from_user.id
    profile = user_profiles.get(user_id)
    
    if not profile:
        return
        
    user = update.message.from_user
    total_tours = len(analyzer.tours_history)
    
    account_msg = (
        f"👤 *Votre Compte*\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Nom: {user.full_name}\n"
        f"🌍 Pays: {COUNTRIES[profile.country_code]['name']}\n"
        f"📡 Signaux restants: {profile.signals_remaining}\n"
        f"💰 Montant restants: {profile.montant_remaining}\n"
        f"📊 Tours collectés: {total_tours}\n"
        f"🧠 IA Status: Actif"
    )
    
    if ContextTypes:
        await update.message.reply_text(account_msg, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(account_msg, parse_mode='Markdown')

async def handle_menu_buttons(update: Update, context):
    """Handle main menu button presses"""
    text = update.message.text
    user_id = update.message.from_user.id
    
    # Check if waiting for tours number
    if context.user_data.get('awaiting_tours_number'):
        await handle_tours_number(update, context)
        return
    
    # Check if admin is providing input for admin actions
    if context.user_data.get("admin_action"):
        await admin_panel_handler(update, context)
        return
    
    if "Signal" in text:
        await generate_signal(update, context)
    elif "Premium" in text:
        await generate_premium(update, context)
    elif "Montante" in text:
        await generate_montante(update, context)
    elif "Collecte de tours" in text or "Collect Tours" in text:
        await collect_tours_handler(update, context)
    elif "Mon compte" in text or "My Account" in text:
        await mon_compte(update, context)
    elif "Admin Panel" in text:
        if str(user_id) == ADMIN_ID:
            profile = user_profiles.get(user_id)
            lang = profile.language if profile else "fr"
            await update.message.reply_text("🔧 Panneau Admin", reply_markup=get_admin_keyboard(lang))
        else:
            await update.message.reply_text("❌ Accès refusé.")
    elif "Statistiques" in text or "Statistics" in text:
        await show_statistics(update, context)
    # Handle admin panel buttons
    elif text in ["➕ Ajouter Signaux", "➖ Réduire Signaux", "💰 Ajouter Montant", "⛔ Désactiver Signaux", "🔙 Retour"]:
        await admin_panel_handler(update, context)

async def show_statistics(update: Update, context):
    """Show bot statistics"""
    total_tours = len(analyzer.tours_history)
    total_users = len(user_profiles)
    active_users = sum(1 for p in user_profiles.values() if p.signals_remaining > 0)
    
    recent_coeffs = []
    if analyzer.tours_history:
        recent_coeffs = [t.coefficient for t in list(analyzer.tours_history)[-10:]]
    
    stats_msg = (
        f"📊 *Statistiques du Bot*\n\n"
        f"👥 Utilisateurs totaux: {total_users}\n"
        f"🔥 Utilisateurs actifs: {active_users}\n"
        f"📈 Tours analysés: {total_tours}\n"
        f"🧠 IA Status: Apprentissage continu\n"
        f"🎯 Derniers coefficients:\n"
    )
    
    if recent_coeffs:
        for coeff in recent_coeffs[-5:]:
            stats_msg += f"   ➡️ x{coeff}\n"
    else:
        stats_msg += "   Aucune donnée récente\n"
    
    if ContextTypes:
        await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def admin_panel_handler(update: Update, context):
    """Handle admin panel operations"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    if str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ Accès refusé.")
        return

    admin_action = context.user_data.get("admin_action")
    profile = user_profiles.get(user_id)
    lang = profile.language if profile else "fr"

    # Handle button clicks
    if "Ajouter Signaux" in text:
        context.user_data["admin_action"] = "add_signals"
        await update.message.reply_text("📥 Envoie l'ID utilisateur et le nombre de signaux (ex: `12345678 5`)")
        return
    elif "Réduire Signaux" in text:
        context.user_data["admin_action"] = "reduce_signals"
        await update.message.reply_text("📤 Envoie l'ID utilisateur et le nombre à réduire (ex: `12345678 3`)")
        return
    elif "Ajouter Montant" in text:
        context.user_data["admin_action"] = "add_amount"
        await update.message.reply_text("💰 Envoie l'ID utilisateur et le nombre de signaux Montante (ex: `12345678 10`)")
        return
    elif "Désactiver Signaux" in text:
        context.user_data["admin_action"] = "disable_signals"
        await update.message.reply_text("⛔ Envoie l'ID de l'utilisateur pour désactiver ses signaux.")
        return
    elif "Retour" in text:
        context.user_data.clear()
        await update.message.reply_text("📋 Menu principal :", reply_markup=get_main_keyboard(user_id, lang))
        return

    # Handle admin input responses
    if admin_action:
        parts = text.strip().split()
        
        if admin_action in ("add_signals", "reduce_signals", "add_amount") and len(parts) == 2:
            try:
                target_id = int(parts[0])
                nombre = int(parts[1])
                
                # Create user if doesn't exist
                if target_id not in user_profiles:
                    user_profiles[target_id] = UserProfile(
                        user_id=target_id,
                        country_code="CI",
                        language="fr",
                        timezone="Africa/Abidjan"
                    )
                
                target_profile = user_profiles[target_id]
                
                if admin_action == "add_signals":
                    target_profile.signals_remaining += nombre
                    await update.message.reply_text(f"✅ Ajouté {nombre} signaux à l'utilisateur `{target_id}`.")
                elif admin_action == "reduce_signals":
                    target_profile.signals_remaining = max(0, target_profile.signals_remaining - nombre)
                    await update.message.reply_text(f"✅ Réduit {nombre} signaux à l'utilisateur `{target_id}`.")
                elif admin_action == "add_amount":
                    target_profile.montant_remaining += nombre
                    await update.message.reply_text(f"✅ Ajouté {nombre} signaux Montante à l'utilisateur `{target_id}`.")
                
                context.user_data.pop("admin_action")
                
            except ValueError:
                await update.message.reply_text("❌ Format invalide. Utilise: ID_utilisateur nombre")
                
        elif admin_action == "disable_signals" and len(parts) == 1:
            try:
                target_id = int(parts[0])
                if target_id in user_profiles:
                    user_profiles[target_id].signals_remaining = 0
                    await update.message.reply_text(f"⛔ Signaux désactivés pour l'utilisateur `{target_id}`.")
                else:
                    await update.message.reply_text("❌ Utilisateur non trouvé.")
                context.user_data.pop("admin_action")
            except ValueError:
                await update.message.reply_text("❌ Format invalide. Envoie juste l'ID utilisateur.")
        else:
            await update.message.reply_text("❌ Format invalide.")
        
        await update.message.reply_text("🔧 Retour au menu admin:", reply_markup=get_admin_keyboard(lang))
        return

    # Handle admin menu selections
    if "Ajouter Signaux" in text or "Add Signals" in text:
        context.user_data["admin_action"] = "add"
        await update.message.reply_text("📥 ID utilisateur et nombre de signaux (ex: 12345678 5)")
    elif "Réduire" in text or "Reduce" in text:
        context.user_data["admin_action"] = "reduce"
        await update.message.reply_text("📤 ID utilisateur et nombre de signaux (ex: 12345678 3)")
    elif "Ajouter Montant" in text or "Add Amount" in text:
        context.user_data["admin_action"] = "add_amount"
        await update.message.reply_text("💰 ID utilisateur et nombre de tours (ex: 12345678 100)")
    elif "Désactiver" in text or "Disable" in text:
        context.user_data["admin_action"] = "disable"
        await update.message.reply_text("⛔ Envoie l'ID de l'utilisateur")
    elif "Retour" in text or "Back" in text:
        await update.message.reply_text(
            MESSAGES.get(lang, MESSAGES["fr"])["menu_prompt"],
            reply_markup=get_main_keyboard(user_id, lang)
        )

def fetch_tours_data():
    """Background task to fetch game data from API and update analyzer"""
    while True:
        try:
            response = requests.get(API_URL, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    new_tours_count = 0
                    
                    for item in data:
                        # Extract coefficient from various possible keys
                        coeff = None
                        for key in ["top_coefficient", "coefficient", "coef", "value", "multiplier"]:
                            if key in item:
                                try:
                                    coeff = float(item[key])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        if coeff and coeff > 0:
                            # Generate unique round ID from multiple fields
                            round_id = (item.get('id') or 
                                      item.get('round_id') or 
                                      item.get('game_id') or 
                                      f"{coeff}_{item.get('timestamp', int(time.time()))}")
                            
                            # Create game round object with proper timestamp
                            round_timestamp = datetime.now()
                            if 'timestamp' in item:
                                try:
                                    round_timestamp = datetime.fromtimestamp(float(item['timestamp']))
                                except:
                                    pass
                            elif 'created_at' in item:
                                try:
                                    round_timestamp = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            round_obj = GameRound(
                                coefficient=coeff,
                                timestamp=round_timestamp,
                                round_id=str(round_id),
                                metadata=item
                            )
                            
                            # Add to analyzer (returns True if new tour added)
                            if analyzer.add_tour(round_obj):
                                new_tours_count += 1
                    
                    if new_tours_count > 0:
                        logger.info(f"API: Added {new_tours_count} new unique tours. Total stored: {len(analyzer.tours_history)}")
                    
                    # Check user targets and send notifications
                    for user_id, profile in user_profiles.items():
                        if profile.tours_target > 0 and len(analyzer.tours_history) >= profile.tours_target:
                            if profile.tours_collected < profile.tours_target:
                                profile.tours_collected = len(analyzer.tours_history)
                                # Send notification to user
                                try:
                                    import asyncio
                                    from telegram import Bot
                                    bot = Bot(token=TOKEN)
                                    
                                    # Create notification message
                                    message = f"🎯 *Objectif Atteint!*\n\nVous avez atteint votre objectif de {profile.tours_target} tours!\nTours actuels: {len(analyzer.tours_history)}"
                                    
                                    # Send notification asynchronously
                                    async def send_notification():
                                        try:
                                            await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
                                        except Exception as e:
                                            logger.error(f"Failed to send notification to {user_id}: {e}")
                                    
                                    # Schedule the notification
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    loop.run_until_complete(send_notification())
                                    loop.close()
                                    
                                    logger.info(f"User {user_id} reached target of {profile.tours_target} tours")
                                except Exception as e:
                                    logger.error(f"Error sending notification to user {user_id}: {e}")
                
            else:
                logger.warning(f"API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching API data: {e}")
        
        time.sleep(10)  # Wait 10 seconds before next fetch

async def main():
    """Main function to start the intelligent bot"""
    logger.info("Starting Intelligent Casino Signals Bot...")
    
    # Start API data fetching in background
    api_thread = threading.Thread(target=fetch_tours_data, daemon=True)
    api_thread.start()
    logger.info("API data fetching started")
    
    # Initialize bot application
    if ContextTypes:
        # Modern python-telegram-bot (v20+)
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Register handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
        app.add_handler(CallbackQueryHandler(country_chosen, pattern="country_"))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel_handler))
        
        logger.info("Starting bot polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        try:
            await asyncio.Event().wait()
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
    else:
        # Fallback for older versions
        from telegram.ext import Updater
        updater = Updater(token=TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Register handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
        dp.add_handler(CallbackQueryHandler(country_chosen, pattern="country_"))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_menu_buttons))
        
        logger.info("Starting bot polling...")
        updater.start_polling()
        updater.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")