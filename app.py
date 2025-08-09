import os
import logging
from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
from bot_handlers import BotHandlers
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize bot application
bot_application = None
bot_handlers = None

def create_bot_application():
    """Create and configure the Telegram bot application"""
    global bot_application, bot_handlers
    
    # Initialize bot handlers
    bot_handlers = BotHandlers()
    
    # Create application
    bot_application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    bot_application.add_handler(CommandHandler("start", bot_handlers.start_command))
    bot_application.add_handler(CommandHandler("help", bot_handlers.help_command))
    bot_application.add_handler(CommandHandler("pengeluaran", bot_handlers.expense_command))
    bot_application.add_handler(CommandHandler("pemasukan", bot_handlers.income_command))
    bot_application.add_handler(CommandHandler("rekapharian", bot_handlers.daily_summary_command))
    bot_application.add_handler(CommandHandler("rekapcustom", bot_handlers.custom_summary_command))
    bot_application.add_handler(CommandHandler("rekapbulanan", bot_handlers.monthly_summary_command))
    bot_application.add_handler(CommandHandler("rekaptahunan", bot_handlers.yearly_summary_command))
    
    # Add message handlers
    bot_application.add_handler(MessageHandler(filters.PHOTO, bot_handlers.handle_photo))
    bot_application.add_handler(MessageHandler(filters.VOICE, bot_handlers.handle_voice))
    bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_text))
    
    return bot_application

@app.route('/')
def index():
    """Simple status page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        global bot_application
        if bot_application is None:
            bot_application = create_bot_application()
            
        # Get the update from Telegram
        update_data = request.get_json()
        logger.info(f"Received webhook update: {update_data}")
        
        if update_data and bot_application:
            update = Update.de_json(update_data, bot_application.bot)
            
            # Process the update in a new thread to avoid blocking
            import threading
            def process_update():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(bot_application.process_update(update))
                    loop.close()
                except Exception as e:
                    logger.error(f"Error in background processing: {e}")
            
            thread = threading.Thread(target=process_update)
            thread.daemon = True
            thread.start()
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set the webhook URL for the Telegram bot"""
    try:
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            return jsonify({'error': 'webhook_url is required'}), 400
            
        # This would be called externally to set up the webhook
        return jsonify({
            'message': 'Use Telegram Bot API to set webhook',
            'url': f'https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/setWebhook',
            'webhook_url': webhook_url
        })
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize bot application
    create_bot_application()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
