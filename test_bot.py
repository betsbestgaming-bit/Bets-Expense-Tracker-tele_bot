#!/usr/bin/env python3
"""
Test script untuk bot Telegram menggunakan long polling
"""
import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot_handlers import BotHandlers
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Run the bot with long polling for testing"""
    # Initialize bot handlers
    bot_handlers = BotHandlers()
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot_handlers.start_command))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CommandHandler("pengeluaran", bot_handlers.expense_command))
    application.add_handler(CommandHandler("pemasukan", bot_handlers.income_command))
    application.add_handler(CommandHandler("hari_ini", bot_handlers.daily_summary_command))
    application.add_handler(CommandHandler("bulan_ini", bot_handlers.monthly_summary_command))
    application.add_handler(CommandHandler("tahun_ini", bot_handlers.yearly_summary_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.PHOTO, bot_handlers.handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, bot_handlers.handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_text))
    
    # Delete webhook and run with long polling
    await application.bot.delete_webhook()
    logger.info("Bot started with long polling...")
    
    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())