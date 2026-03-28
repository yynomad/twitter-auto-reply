#!/usr/bin/env python3
"""
Twitter 自动评论 - 简化版
手动选择推文，自动执行评论
"""

import subprocess
import time
import random
import json
import requests
import os

# 配置
AI_API_KEY = os.getenv("AI_API_KEY", "sk-sp-74bad0d59c8741b5a18610cbeafd0eb9")
AI_BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
AI_MODEL = "qwen3.5-plus"

def run_applescript(script):
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def copy_to_clipboard(text):
    subprocess.run(['pbcopy'], input=text.encode('utf-8'))

def generate_ai_reply(tweet_text, tweet_author):
    """使用 AI 生成回复"""
    prompt = f"""你是 Twitter 用户，回复这条推文：

@{tweet_author}: {tweet_text[:200]}

要求：
- 简短自然，像真人说话
- 不超过 50 字
- 可以使用 emoji
- 只要回复内容，不要其他解释

回复："""

    try:
        response = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "你是 Twitter 用户，擅长生成简短有趣的回复。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 100
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        return None
    except:
        return None

def auto_comment(tweet_url, reply_text):
    """自动评论"""
    print("\n🚀 开始自动评论...")
    print(f"   推文：{tweet_url}")
    print(f"   回复：{reply_text[:50]}...")
    
    # 步骤 1: 打开推文
    print("\n📍 步骤 1: 打开推文 (等待 3-5 秒)")
    subprocess.run(['open', tweet_url])
    time.sleep(random.uniform(3, 5))
    print("   ✅ 已打开")
    
    # 步骤 2: 点击回复按钮
    print("\n📍 步骤 2: 点击回复按钮")
    script = '''
    tell application "System Events"
        tell process "Google Chrome"
            try
                click (first button whose description contains "Reply")
            end try
        end tell
    end tell
    '''
    run_applescript(script)
    time.sleep(random.uniform(2, 3))
    print("   ✅ 已点击")
    
    # 步骤 3: 等待评论框加载
    print("\n📍 步骤 3: 等待评论框加载 (2-3 秒)")
    time.sleep(random.uniform(2, 3))
    
    # 步骤 4: 复制回复
    print("\n📍 步骤 4: 复制回复内容")
    copy_to_clipboard(reply_text)
    time.sleep(random.uniform(1, 2))
    print("   ✅ 已复制")
    
    # 步骤 5: 粘贴
    print("\n📍 步骤 5: 粘贴到评论框")
    script = '''
    tell application "System Events"
        keystroke "v" using command down
        delay 1
    end tell
    '''
    run_applescript(script)
    time.sleep(random.uniform(2, 3))
    print("   ✅ 已粘贴")
    
    # 步骤 6: 模拟思考
    print("\n📍 步骤 6: 模拟思考 (3-6 秒)...")
    time.sleep(random.uniform(3, 6))
    
    # 步骤 7: 点击发送
    print("\n📍 步骤 7: 点击发送按钮")
    script = '''
    tell application "System Events"
        tell process "Google Chrome"
            try
                click (first button whose description contains "Post")
            end try
        end tell
    end tell
    '''
    run_applescript(script)
    time.sleep(random.uniform(2, 3))
    print("   ✅ 已点击发送")
    
    # 步骤 8: 等待完成
    print("\n📍 步骤 8: 等待发送完成 (2-4 秒)...")
    time.sleep(random.uniform(2, 4))
    
    print("\n✅ 自动评论完成！")

def main():
    print("=" * 70)
    print("🐦 Twitter 自动评论")
    print("=" * 70)
    
    # 让用户输入推文 URL
    print("\n请在 Chrome 中打开要回复的推文")
    time.sleep(2)
    
    # 获取当前 Chrome 标签页的 URL
    script = '''
    tell application "Google Chrome"
        tell active tab of window 1
            return URL
        end tell
    end tell
    '''
    tweet_url = run_applescript(script)
    
    if not tweet_url or 'error' in tweet_url.lower():
        print("\n❌ 无法获取当前推文 URL，请手动输入:")
        tweet_url = input("推文 URL: ").strip()
    
    print(f"\n📍 当前推文：{tweet_url}")
    
    # 获取推文内容（简化版，让用户输入）
    print("\n请输入推文内容（用于 AI 生成回复）:")
    tweet_text = input("> ").strip()
    
    if not tweet_text:
        tweet_text = "推文内容"
    
    # 提取作者
    tweet_author = tweet_url.split('/')[-2] if '/status/' in tweet_url else "user"
    
    # 生成 AI 回复
    print("\n🤖 正在生成 AI 回复...")
    reply = generate_ai_reply(tweet_text, tweet_author)
    
    if not reply:
        reply = "写得真好！👍"
    
    print(f"   ✅ 生成回复：{reply}")
    
    # 确认
    print("\n" + "=" * 70)
    print(f"推文：@{tweet_author} - {tweet_text[:50]}...")
    print(f"回复：{reply}")
    print("=" * 70)
    
    try:
        confirm = input("\n是否执行自动评论？[y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("\n❌ 已取消")
            return
        
        # 执行自动评论
        auto_comment(tweet_url, reply)
        
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
    except EOFError:
        print("\n❌ 已取消")

if __name__ == "__main__":
    main()
