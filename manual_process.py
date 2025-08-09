#!/usr/bin/env python3
"""
Manual process untuk memproses update yang tertunda
"""
import json
import asyncio
from telegram import Update
from telegram.ext import Application
from bot_handlers import BotHandlers
from config import Config

async def process_pending_updates():
    """Process all pending updates"""
    # Initialize bot handlers
    bot_handlers = BotHandlers()
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    from telegram.ext import CommandHandler, MessageHandler, filters
    application.add_handler(CommandHandler("start", bot_handlers.start_command))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CommandHandler("pengeluaran", bot_handlers.expense_command))
    application.add_handler(CommandHandler("pemasukan", bot_handlers.income_command))
    application.add_handler(CommandHandler("hari_ini", bot_handlers.daily_summary_command))
    application.add_handler(CommandHandler("bulan_ini", bot_handlers.monthly_summary_command))
    application.add_handler(CommandHandler("tahun_ini", bot_handlers.yearly_summary_command))
    application.add_handler(MessageHandler(filters.PHOTO, bot_handlers.handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, bot_handlers.handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_text))
    
    # Initialize the application
    await application.initialize()
    
    # Get pending updates
    updates = await application.bot.get_updates()
    
    print(f"Processing {len(updates)} pending updates...")
    
    for update_data in updates:
        try:
            print(f"Processing update {update_data.update_id}")
            # Process each update
            await application.process_update(update_data)
            print(f"Processed update {update_data.update_id} successfully")
        except Exception as e:
            print(f"Error processing update {update_data.update_id}: {e}")
    
    # Clear processed updates
    if updates:
        last_update_id = updates[-1].update_id
        await application.bot.get_updates(offset=last_update_id + 1)
        print(f"Cleared updates up to {last_update_id}")
    
    await application.shutdown()
    print("Processing completed!")

if __name__ == "__main__":
    asyncio.run(process_pending_updates())