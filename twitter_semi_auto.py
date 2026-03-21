#!/usr/bin/env python3
"""
Twitter 半自动回复 - Telegram 版本

功能：
1. 抓取 Twitter Home 第一条推文
2. 提取：链接、原文、点赞、评论、转发、浏览
3. 生成 3 条回复建议
4. 通过 Telegram 发送，带复制按钮
5. 用户点击后打开推文链接
"""

import subprocess
import json
import os
import sys

# ============== 配置 ==============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ============== 工具函数 ==============

def run_applescript(script):
    """运行 AppleScript"""
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def run_js(js_code):
    """在 Chrome 中执行 JavaScript"""
    script = f'''
    tell application "Google Chrome"
        tell active tab of window 1
            set result to execute javascript "{js_code}"
            return result
        end tell
    end tell
    '''
    return run_applescript(script)

def send_telegram_message(text, buttons=None):
    """发送 Telegram 消息（带内联按钮）"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️  未配置 Telegram，直接输出：")
        print("=" * 60)
        print(text)
        if buttons:
            print("\n按钮:")
            for i, btn in enumerate(buttons, 1):
                print(f"  {i}. {btn['text']}")
        return
    
    # 构建内联键盘
    keyboard = []
    if buttons:
        for btn in buttons:
            keyboard.append([{
                "text": btn["text"],
                "callback_data": btn["data"]
            }])
    
    # 发送消息
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    
    response = requests.post(url, json=data)
    result = response.json()
    
    if result.get("ok"):
        print(f"\n✅ 消息已发送到 Telegram")
        return result["result"]["message_id"]
    else:
        print(f"\n❌ 发送失败：{result.get('description')}")
        return None

def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    subprocess.run(['pbcopy'], input=text.encode('utf-8'))
    print(f"✅ 已复制到剪贴板")

def open_url(url):
    """在 Chrome 中打开 URL"""
    script = f'''
    tell application "Google Chrome"
        activate
        tell active tab of window 1
            open location "{url}"
            return URL
        end tell
    end tell
    '''
    result = run_applescript(script)
    print(f"✅ 已打开：{result}")

# ============== 步骤 1: 抓取推文 ==============

def grab_tweet():
    """抓取 Home 页面第一条推文"""
    print("\n" + "=" * 60)
    print("📥 步骤 1: 抓取推文")
    print("=" * 60)
    
    script = '''
    tell application "Google Chrome"
        activate
        tell active tab of window 1
            open location "https://twitter.com/home"
            delay 5
            
            set result to execute javascript "
            (function() {
                var articles = document.querySelectorAll('article[data-testid=\\\"tweet\\\"]');
                if (articles.length === 0) {
                    window.scrollTo(0, document.body.scrollHeight);
                    var start = Date.now();
                    while (articles.length === 0 && Date.now() - start < 5000) {
                        articles = document.querySelectorAll('article[data-testid=\\\"tweet\\\"]');
                    }
                }
                
                if (articles.length === 0) return JSON.stringify({error: 'NO_TWEETS'});
                
                var article = articles[0];
                
                var data = {
                    text: article.querySelector('div[data-testid=\\\"tweetText\\\"]')?.innerText || 'N/A',
                    username: article.querySelector('a[href^=\\\"/\\\"][href*=\\\"/status\\\"]')?.href?.split('/')[3] || 'N/A',
                    name: article.querySelector('div[data-testid=\\\"User-Name\\\"] span span')?.innerText || 'N/A',
                    url: ''
                };
                
                var links = article.querySelectorAll('a[href*=\\\"/status/\\\"]');
                for (var link of links) {
                    if (link.href.includes('/status/')) {
                        data.url = link.href;
                        break;
                    }
                }
                
                // 获取互动数据
                var allSpans = article.querySelectorAll('span');
                var numbers = [];
                for (var span of allSpans) {
                    var text = span.innerText.trim();
                    if (text && /^[0-9.]+[KMBkmb]?$/i.test(text) && text.length < 10) {
                        numbers.push(text);
                    }
                }
                
                data.likes = numbers[numbers.length-2] || '0';
                data.replies = numbers[0] || '0';
                data.retweets = numbers[1] || '0';
                data.views = numbers[numbers.length-1] || 'N/A';
                
                return JSON.stringify(data);
            })();
            "
            return result
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    
    try:
        tweet = json.loads(result)
        if 'error' in tweet:
            print("❌ 未找到推文")
            return None
        
        print(f"\n👤 用户：{tweet.get('name', 'N/A')} (@{tweet.get('username', 'N/A')})")
        print(f"\n📝 内容:\n{tweet.get('text', 'N/A')}\n")
        print(f"📈 互动：👍{tweet.get('likes')} 💬{tweet.get('replies')} 🔄{tweet.get('retweets')} 👁️{tweet.get('views')}")
        
        return tweet
        
    except Exception as e:
        print(f"解析失败：{e}")
        print(f"原始结果：{result}")
        return None

# ============== 步骤 2: 生成回复 ==============

def generate_replies(tweet):
    """生成 3 条回复建议"""
    print("\n" + "=" * 60)
    print("💡 步骤 2: 生成回复建议")
    print("=" * 60)
    
    # 根据推文内容生成回复（这里用模板，可以接入 AI）
    text = tweet.get('text', '')
    
    # 简单的情绪分析
    if '?' in text or '？' in text:
        # 问题型推文
        replies = [
            "好问题！我也在想这个，蹲一个答案~ 🤔",
            "这个得看具体情况，不过一般来说...",
            "有人知道吗？同求解答！"
        ]
    elif '😂' in text or '哈哈' in text or '笑' in text:
        # 幽默型推文
        replies = [
            "哈哈哈哈笑死我了😂",
            "太真实了，无法反驳！",
            "这个我必须点赞，太逗了~"
        ]
    else:
        # 通用型
        replies = [
            "确实是这样，深有同感~ 👍",
            "第一次见到这种，长见识了！",
            "求更多细节！👀"
        ]
    
    print("\n📋 回复建议:")
    for i, reply in enumerate(replies, 1):
        print(f"   {i}. {reply}")
    
    return replies

# ============== 步骤 3: 发送到 Telegram ==============

def format_message(tweet, replies):
    """格式化 Telegram 消息"""
    
    # 截断过长的推文
    text = tweet.get('text', 'N/A')
    if len(text) > 200:
        text = text[:200] + "..."
    
    message = f"""🐦 <b>新推文发现</b>

👤 <b>{tweet.get('name', 'N/A')}</b> (@{tweet.get('username', 'N/A')})

📝 <b>内容:</b>
{text}

📈 <b>互动数据:</b>
👍 点赞：{tweet.get('likes', '0')}
💬 评论：{tweet.get('replies', '0')}
🔄 转发：{tweet.get('retweets', '0')}
👁️ 浏览：{tweet.get('views', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>回复建议:</b>

1️⃣ {replies[0]}

2️⃣ {replies[1]}

3️⃣ {replies[2]}

━━━━━━━━━━━━━━━━━━━━━━━

🔗 <a href="{tweet.get('url', '#')}">打开推文回复</a>"""
    
    return message

def create_buttons(tweet, replies):
    """创建内联按钮"""
    buttons = []
    
    # 3 个回复选项（复制功能通过 callback 处理）
    for i, reply in enumerate(replies, 1):
        buttons.append({
            "text": f"{i}. {reply[:30]}{'...' if len(reply) > 30 else ''}",
            "data": f"reply_{i}"
        })
    
    # 打开推文按钮
    buttons.append({
        "text": "🔗 打开推文",
        "data": f"open_{tweet.get('url', '')}"
    })
    
    return buttons

# ============== 主流程 ==============

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           🐦 Twitter 半自动回复（Telegram 版）              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 步骤 1: 抓取推文
    tweet = grab_tweet()
    if not tweet:
        print("\n❌ 流程终止")
        return
    
    # 步骤 2: 生成回复
    replies = generate_replies(tweet)
    
    # 步骤 3: 格式化消息
    message = format_message(tweet, replies)
    buttons = create_buttons(tweet, replies)
    
    # 步骤 4: 发送到 Telegram
    print("\n" + "=" * 60)
    print("📤 步骤 4: 发送到 Telegram")
    print("=" * 60)
    
    msg_id = send_telegram_message(message, buttons)
    
    if msg_id:
        print("\n✅ 完成！请在 Telegram 中:")
        print("   1. 点击回复建议 → 自动复制到剪贴板")
        print("   2. 点击「打开推文」→ 自动在 Chrome 中打开")
        print("   3. 粘贴回复并发送")
    else:
        print("\n✅ 完成！已输出到控制台")
        print("   请手动复制回复，打开推文链接发送")

if __name__ == "__main__":
    main()
