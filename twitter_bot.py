#!/usr/bin/env python3
"""
Twitter 半自动回复 - Telegram Bot

处理内联按钮点击：
- 点击回复 → 复制到剪贴板 + 打开推文
- 点击打开推文 → 在 Chrome 中打开
"""

import os
import json
import subprocess
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 存储当前的推文和回复
current_tweet = {}
current_replies = []

def run_applescript(script):
    """运行 AppleScript"""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    subprocess.run(['pbcopy'], input=text.encode('utf-8'))

def open_tweet(url):
    """在 Chrome 中打开推文"""
    script = f'''
    tell application "Google Chrome"
        activate
        tell active tab of window 1
            open location "{url}"
            delay 2
            return URL
        end tell
    end tell
    '''
    return run_applescript(script)

def send_message(text, reply_to_message_id=None):
    """发送 Telegram 消息"""
    import requests
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id
    
    response = requests.post(url, json=data)
    return response.json()

def answer_callback(callback_query_id, text, show_alert=False):
    """回复 callback 查询"""
    import requests
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    data = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    }
    
    response = requests.post(url, json=data)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理 Telegram webhook"""
    update = request.get_json()
    
    # 处理回调查询（按钮点击）
    if 'callback_query' in update:
        callback = update['callback_query']
        data = callback.get('data', '')
        query_id = callback.get('id', '')
        
        if data.startswith('reply_'):
            # 点击回复建议
            reply_index = int(data.split('_')[1]) - 1
            if 0 <= reply_index < len(current_replies):
                reply_text = current_replies[reply_index]
                
                # 复制到剪贴板
                copy_to_clipboard(reply_text)
                
                # 打开推文
                if current_tweet.get('url'):
                    open_tweet(current_tweet['url'])
                
                # 回复用户
                answer_callback(
                    query_id,
                    f"✅ 已复制：{reply_text[:50]}...\n\n请粘贴到 Twitter 评论框",
                    show_alert=True
                )
        
        elif data.startswith('open_'):
            # 点击打开推文
            url = data.split('_', 1)[1]
            open_tweet(url)
            
            answer_callback(
                query_id,
                "✅ 已在 Chrome 中打开推文",
                show_alert=True
            )
        
        return 'OK'
    
    # 处理普通消息
    if 'message' in update:
        message = update['message']
        text = message.get('text', '')
        
        # 如果是 /start 命令
        if text == '/start':
            send_message(
                "👋 欢迎使用 Twitter 半自动回复！\n\n"
                "发送 /grab 抓取下一条推文",
                reply_to_message_id=message.get('message_id')
            )
        
        # 如果是 /grab 命令
        elif text == '/grab':
            send_message(
                "🔄 正在抓取推文...",
                reply_to_message_id=message.get('message_id')
            )
            
            # 这里可以调用抓取逻辑
            # 为简化，直接返回提示
            send_message(
                "请运行：python3 twitter_semi_auto.py",
                reply_to_message_id=message.get('message_id')
            )
        
        return 'OK'
    
    return 'OK'

if __name__ == '__main__':
    # 启动 webhook 服务器
    app.run(host='0.0.0.0', port=5000)
