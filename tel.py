import threading
import subprocess
import sys
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is Running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """تشغيل البوت"""
    os.system("python main.py")

if __name__ == "__main__":
    # تشغيل البوت في thread منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل Flask للاستماع على المنفذ
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
