# Telegram Casino Signals Bot

## Overview

This is a Telegram bot application that provides gambling signals for casino games, specifically targeting crash/aviator-style games. The bot operates with a freemium model, offering both standard and premium signals to users based on their subscription status. It includes user management, country-specific localization, and an admin panel for signal management.

## System Architecture

### Core Architecture Components

1. **Telegram Bot Layer**: Built using `python-telegram-bot` library for handling user interactions
2. **Web Dashboard**: Flask-based monitoring interface for bot statistics and status
3. **Data Layer**: In-memory storage using Python dictionaries (no persistent database)
4. **External API Integration**: Fetches real-time game data from crash game gateway
5. **Multi-threading**: Concurrent execution of bot and web server components

### Technology Stack

- **Backend**: Python 3.11
- **Bot Framework**: python-telegram-bot (v22.1+)
- **Web Framework**: Flask (v3.1.1+)
- **HTTP Client**: requests library
- **Timezone Management**: pytz
- **Deployment**: Replit with Nix environment

## Key Components

### Bot Module (`bot.py`)
- **Purpose**: Main bot logic and user interaction handling
- **Features**: 
  - User registration and country selection
  - Channel membership verification
  - Signal generation and distribution
  - Premium user management
  - Admin controls

### Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment variable handling
  - Signal timing and coefficient parameters
  - Multi-country support settings
  - API endpoints and timeouts

### Web Server (`web_server.py`)
- **Purpose**: Monitoring dashboard for bot operations
- **Features**:
  - Real-time statistics display
  - Bot status monitoring
  - User analytics
  - REST API endpoints

### Main Entry Point (`main.py`)
- **Purpose**: Application orchestration
- **Features**:
  - Concurrent bot and web server execution
  - Graceful error handling
  - Logging configuration

## Data Flow

### User Registration Flow
1. User starts bot interaction
2. Country selection from supported regions (Côte d'Ivoire, France)
3. Channel membership verification
4. User data storage in memory
5. Access to main menu functionality

### Signal Generation Flow
1. External API polling for game data
2. Coefficient analysis and filtering
3. Signal timing calculation based on user type
4. Message formatting with localization
5. Distribution to eligible users

### Premium Feature Flow
1. Premium status verification
2. Enhanced signal parameters
3. Priority access to high-value signals
4. Extended signal history access

## External Dependencies

### Required Services
- **Telegram Bot API**: Core messaging functionality
- **Crash Game Gateway API**: Real-time game data source
- **Channel Verification**: Telegram channel membership checking

### Third-party Libraries
- `python-telegram-bot`: Telegram bot framework
- `flask`: Web server framework
- `requests`: HTTP client for API calls
- `pytz`: Timezone management
- `telegram`: Additional Telegram utilities

## Deployment Strategy

### Environment Configuration
- **Runtime**: Python 3.11 on Nix stable-24_05
- **Port**: Web server on port 5000
- **Process Management**: Parallel execution using workflows

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Bot authentication token
- `CHANNEL_USERNAME`: Required channel for membership
- `ADMIN_ID`: Administrative user identifier
- `API_URL`: Game data source endpoint
- `FLASK_SECRET_KEY`: Web session security

### Security Considerations
- Sensitive tokens stored as environment variables
- Admin access restricted by user ID verification
- Channel membership requirement for bot access
- No persistent data storage (memory-only)

## Architectural Decisions

### Data Storage Choice
- **Decision**: In-memory storage using Python dictionaries
- **Rationale**: Simple deployment, no database setup required
- **Trade-offs**: Data loss on restart, limited scalability
- **Alternative**: Could be upgraded to PostgreSQL with Drizzle ORM

### Multi-language Support
- **Decision**: Dictionary-based localization system
- **Rationale**: Simple implementation for limited language support
- **Current Support**: French language with country-specific timezones

### Signal Algorithm
- **Decision**: Coefficient-based filtering with timing delays
- **Rationale**: Creates perceived value through delayed premium signals
- **Parameters**: Configurable ranges for standard vs premium signals

### Web Dashboard Integration
- **Decision**: Separate Flask application with shared data access
- **Rationale**: Independent monitoring without affecting bot performance
- **Implementation**: Thread-based concurrent execution

## Changelog
- June 27, 2025. Initial setup
- June 27, 2025. Major upgrade to intelligent AI system with fixes:
  - Fixed tour deduplication system to prevent accumulation of duplicate rounds
  - Enhanced admin panel with "Ajouter Montant" functionality for tour targets
  - Improved API data fetching with proper unique ID handling
  - Updated web dashboard to show accurate statistics from intelligent bot
  - Implemented three-tier signal system: Standard, Premium, and ultra-precise Montante
  - Added 30 countries with automatic timezone and language detection
  - Built advanced machine learning algorithms for adaptive signal generation

## User Preferences

Preferred communication style: Simple, everyday language.
System Requirements: Ultra-intelligent bot with focus on Montante precision, real-time learning, and professional-level reliability.