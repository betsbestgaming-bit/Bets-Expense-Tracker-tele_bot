# Overview

This is an Indonesian Telegram expense tracking bot that helps users manage their personal finances through multiple input methods. The bot can process receipt photos using OCR, voice messages, and text commands to automatically categorize and record expenses/income. It uses free Gemini AI for processing instead of OpenAI, and has been configured to work with Google Sheets integration. The system provides comprehensive reporting features including daily, monthly, and yearly summaries with custom date range support.

## Recent Changes (2025-08-09)
- ✓ Replaced OpenAI with free Gemini AI integration for receipt OCR and text processing
- ✓ Implemented simplified Google Sheets service with logging fallback
- ✓ Fixed all telegram package conflicts and import errors  
- ✓ Configured automatic header creation in Google Sheets: Tanggal, Tipe, Jumlah, Kategori, Keterangan, Timestamp
- ✓ System now runs successfully with logging mode when Google Sheets auth is not available
- ✓ Integrated user's Google Sheets Public URL: 

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Flask Web Application**: Simple web interface with Bootstrap styling for bot status and information display
- **Telegram Bot Interface**: Primary user interaction through Telegram messaging platform
- **Multi-modal Input Processing**: Supports text commands, photo uploads (receipt OCR), and voice messages

## Backend Architecture
- **Flask Application Server**: Lightweight web server handling webhook endpoints and web interface
- **Event-driven Bot Handlers**: Asynchronous message processing using python-telegram-bot library
- **Modular Service Architecture**: Separated concerns with dedicated services for OpenAI, Google Sheets, and date utilities

## Core Services
- **GeminiService**: Receipt OCR using Gemini vision model for expense extraction from photos (replaces OpenAI)
- **SheetsService**: Google Sheets integration with logging fallback for data persistence
- **DateUtils**: Indonesian date parsing and formatting utilities with localized month names
- **BotHandlers**: Central command and message routing with comprehensive expense tracking commands

## Data Storage
- **Google Sheets**: Primary data persistence layer storing transactions with columns for date, type, amount, category, description, and timestamp
- **JSON Configuration**: Environment-based configuration management for API keys and service credentials

## Authentication & Security
- **Telegram Bot Token**: Secure bot authentication with Telegram's API (TELEGRAM_BOT_TOKEN)
- **Gemini API Key**: Free Google AI API authentication for vision processing (GEMINI_API_KEY)
- **Google Sheets**: Public editable link integration for simplified data storage

## Processing Pipeline
- **Receipt Processing**: Image upload → OpenAI Vision API → JSON extraction → Google Sheets storage
- **Voice Processing**: Voice message → transcription → expense parsing → data storage
- **Text Processing**: Command parsing → validation → direct data storage
- **Reporting Engine**: Date range queries → data aggregation → formatted summary generation

# External Dependencies

## APIs and Services
- **Telegram Bot API**: Core messaging platform and webhook integration
- **OpenAI GPT-4o Vision API**: Receipt OCR and expense data extraction from images
- **Google Sheets API**: Data persistence and spreadsheet management
- **Google Drive API**: Spreadsheet creation and access management

## Python Libraries
- **python-telegram-bot**: Telegram bot framework with async support
- **openai**: Official OpenAI API client
- **gspread**: Google Sheets Python integration
- **google-oauth2**: Service account authentication
- **flask**: Web application framework
- **python-dotenv**: Environment variable management
- **python-dateutil**: Enhanced date parsing capabilities

## Development Dependencies
- **Bootstrap 5.1.3**: Frontend UI framework via CDN
- **Feather Icons**: Icon library for web interface
- **logging**: Python standard library for application monitoring
