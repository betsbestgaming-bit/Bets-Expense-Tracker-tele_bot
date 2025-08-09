#!/usr/bin/env python3
"""
Simple bot test untuk verificasi koneksi
"""
import requests
import json
from config import Config

def send_test_message(chat_id, message):
    """Send a test message to specific chat"""
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=data)
    return response.json()

def get_updates():
    """Get latest updates from Telegram"""
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    return response.json()

def get_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    print("=== Bot Information ===")
    bot_info = get_bot_info()
    print(json.dumps(bot_info, indent=2))
    
    print("\n=== Latest Updates ===")
    updates = get_updates()
    print(json.dumps(updates, indent=2))
    
    # Try to extract chat_id from updates
    if updates.get('result'):
        for update in updates['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                print(f"\n=== Sending test message to chat {chat_id} ===")
                result = send_test_message(chat_id, "🤖 Bot test berhasil! Silakan coba kirim /start")
                print(json.dumps(result, indent=2))
                break