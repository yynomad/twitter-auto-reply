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
import requests
import time
import random

# 自动加载 .env 文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, '.env')

if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# ============== 配置 ==============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 阿里云百炼 AI 配置
AI_API_KEY = os.getenv("AI_API_KEY")  # 必须通过环境变量设置
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "qwen3.5-plus")

# 检查 AI 配置
if not AI_API_KEY:
    print("⚠️  警告：未设置 AI_API_KEY 环境变量，将使用模板回复")
    print("   请设置：export AI_API_KEY='your-api-key'")

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
            # 支持两种按钮类型：callback_data（回复）和 url（直接跳转）
            button_data = {"text": btn["text"]}
            if "url" in btn:
                button_data["url"] = btn["url"]
            elif "data" in btn:
                button_data["callback_data"] = btn["data"]
            keyboard.append([button_data])
    
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


def auto_comment(tweet_url, reply_text):
    """自动评论：打开浏览器，模拟人工操作"""
    import time
    import random
    
    print(f"\n🚀 开始自动评论...")
    print(f"   推文：{tweet_url}")
    print(f"   回复：{reply_text[:50]}...")
    
    # 步骤 1: 打开推文
    print("\n📍 步骤 1: 打开推文 (等待 3-5 秒)")
    subprocess.run(['open', tweet_url])
    time.sleep(random.uniform(3, 5))
    
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
    
    # 步骤 3: 等待加载
    print("   等待评论框加载 (2-3 秒)...")
    time.sleep(random.uniform(2, 3))
    
    # 步骤 4: 复制回复
    print("\n📍 步骤 3: 复制回复内容")
    copy_to_clipboard(reply_text)
    time.sleep(random.uniform(1, 2))
    
    # 步骤 5: 粘贴
    print("\n📍 步骤 4: 粘贴到评论框")
    script = '''
    tell application "System Events"
        keystroke "v" using command down
        delay 1
    end tell
    '''
    run_applescript(script)
    time.sleep(random.uniform(2, 3))
    
    # 步骤 6: 模拟思考
    print("\n📍 步骤 5: 模拟思考 (3-6 秒)...")
    time.sleep(random.uniform(3, 6))
    
    # 步骤 7: 点击发送
    print("\n📍 步骤 6: 点击发送按钮")
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
    
    # 步骤 8: 等待完成
    print("\n📍 步骤 7: 等待发送完成 (2-4 秒)...")
    time.sleep(random.uniform(2, 4))
    
    print("\n✅ 自动评论完成！")

def open_url(url):
    """在 Chrome 中打开 URL（复用第 1 个标签页）"""
    # 检查 Chrome 是否运行
    check_script = '''
    tell application "Google Chrome"
        if not (exists window 1) then
            return "no_window"
        end if
        return "ok"
    end tell
    '''
    
    status = run_applescript(check_script).strip()
    
    if status == "ok":
        # Chrome 运行中，使用第 1 个标签页
        script = f'''
        tell application "Google Chrome"
            activate
            tell window 1
                set active tab to tab 1
                tell active tab
                    set location to "{url}"
                    delay 5
                end tell
            end tell
        end tell
        '''
        run_applescript(script)
        print(f"   (复用第 1 个标签页)")
    else:
        # Chrome 未运行，打开新窗口
        subprocess.run(['open', '-a', 'Google Chrome', url])
        time.sleep(5)
        print(f"   (创建新窗口)")
    
    print(f"✅ 已打开：{url}")

# ============== 步骤 1: 抓取推文 ==============

def grab_tweet():
    """抓取 Home 页面第一条推文"""
    print("\n" + "=" * 60)
    print("📥 步骤 1: 抓取推文")
    print("=" * 60)
    
    # 检查 Chrome 状态
    check_script = '''
    tell application "Google Chrome"
        if not (exists window 1) then
            return "no_window"
        end if
        return "ok"
    end tell
    '''
    
    status = run_applescript(check_script).strip()
    
    if status == "ok":
        # Chrome 运行中，使用第 1 个标签页
        script = '''
        tell application "Google Chrome"
            activate
            tell window 1
                set active tab to tab 1
                tell active tab
                    set location to "https://twitter.com/home"
                    delay 5
                end tell
            end tell
        end tell
        '''
        run_applescript(script)
        print(f"   (复用第 1 个标签页)")
    else:
        # Chrome 未运行，打开新窗口
        subprocess.run(['open', '-a', 'Google Chrome', 'https://twitter.com/home'])
        time.sleep(5)
        print(f"   (创建新窗口)")
    
    # 执行 JS 抓取推文
    js_code = '''
    (function() {
        var articles = document.querySelectorAll('article[data-testid="tweet"]');
        if (articles.length === 0) {
            window.scrollTo(0, document.body.scrollHeight);
            var start = Date.now();
            while (articles.length === 0 && Date.now() - start < 5000) {
                articles = document.querySelectorAll('article[data-testid="tweet"]');
            }
        }
        
        if (articles.length === 0) return JSON.stringify({error: 'NO_TWEETS'});
        
        var article = articles[0];
        
        var data = {
            text: article.querySelector('div[data-testid="tweetText"]')?.innerText || 'N/A',
            username: article.querySelector('a[href^="/"][href*="/status"]')?.href?.split('/')[3] || 'N/A',
            name: article.querySelector('div[data-testid="User-Name"] span span')?.innerText || 'N/A',
            url: ''
        };
        
        var links = article.querySelectorAll('a[href*="/status/"]');
        for (var link of links) {
            if (link.href.includes('/status/')) {
                data.url = link.href;
                break;
            }
        }
        
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
    })()
    '''
    
    # 通过 AppleScript 执行 JS
    script = f'''
    tell application "Google Chrome"
        tell active tab of window 1
            set result to execute javascript "{js_code}"
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

def generate_replies_ai(tweet_text, tweet_author, num_replies=3):
    """使用 AI 生成回复建议"""
    if not AI_API_KEY:
        return None
    
    prompt = f"""你是一个 Twitter 用户，需要回复一条推文。请生成 {num_replies} 条简短、自然、有趣的回复。

推文作者：@{tweet_author}
推文内容：
{tweet_text}

要求：
- 每条回复不超过 50 个字
- 语气自然，像真人说话
- 可以适当使用 emoji
- 回复风格多样化（赞同、提问、补充、幽默等）

请按以下 JSON 格式返回：
{{
  "replies": [
    {{"style": "赞同", "content": "回复内容 1"}},
    {{"style": "提问", "content": "回复内容 2"}},
    {{"style": "补充", "content": "回复内容 3"}}
  ]
}}"""

    try:
        response = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一个 Twitter 用户，擅长生成简短有趣的回复。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 500
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 尝试解析 JSON
            import json as json_lib
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    data = json_lib.loads(content[start:end])
                    replies = []
                    for r in data.get("replies", []):
                        replies.append(f"[{r.get('style', '回复')}] {r.get('content', '')}")
                    return replies
            except:
                pass
            
            return [content]
        else:
            print(f"   ⚠️  AI 请求失败：{response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ⚠️  AI 请求异常：{e}")
        return None


def generate_replies(tweet):
    """生成 3 条回复建议"""
    print("\n" + "=" * 60)
    print("💡 步骤 2: 生成回复建议")
    print("=" * 60)
    
    text = tweet.get('text', '')
    author = tweet.get('username', 'user')
    
    # 尝试使用 AI 生成
    if AI_API_KEY:
        print("   🤖 正在使用 AI 生成回复...")
        ai_replies = generate_replies_ai(text, author)
        
        if ai_replies:
            replies = ai_replies
            print("\n📋 AI 生成的回复建议:")
        else:
            print("\n   ⚠️  AI 生成失败，使用模板回复")
            replies = None
    else:
        replies = None
    
    # AI 失败或未配置时使用模板
    if not replies:
        if '?' in text or '？' in text:
            replies = [
                "[提问] 好问题！我也在想这个，蹲一个答案~ 🤔",
                "[分析] 这个得看具体情况，不过一般来说...",
                "[求助] 有人知道吗？同求解答！"
            ]
        elif '😂' in text or '哈哈' in text or '笑' in text:
            replies = [
                "[幽默] 哈哈哈哈笑死我了😂",
                "[共鸣] 太真实了，无法反驳！",
                "[点赞] 这个我必须点赞，太逗了~"
            ]
        else:
            replies = [
                "[赞同] 确实是这样，深有同感~ 👍",
                "[学习] 第一次见到这种，长见识了！",
                "[好奇] 求更多细节！👀"
            ]
        
        if not AI_API_KEY:
            print("\n📋 回复建议:")
        else:
            print("\n📋 模板回复:")
    
    for i, reply in enumerate(replies, 1):
        print(f"   {i}. {reply}")
    
    return replies

# ============== 步骤 3: 发送到 Telegram ==============

def format_message(tweet, replies):
    """格式化 Telegram 消息"""
    
    # 截断过长的推文（Telegram 限制 4096 字符，这里限制 2048 留余量）
    text = tweet.get('text', 'N/A')
    if len(text) > 2048:
        text = text[:2048] + "..."
    
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
    
    # 打开推文按钮 - 使用 url 类型，直接跳转
    buttons.append({
        "text": "🔗 打开推文",
        "url": tweet.get('url', '')
    })
    
    return buttons

# ============== 主流程 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter 半自动回复")
    parser.add_argument("--search", type=str, help="搜索关键词（如 AI, technology）")
    parser.add_argument("--auto", action="store_true", help="启用自动评论模式")
    args = parser.parse_args()
    
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           🐦 Twitter 半自动回复（Telegram 版）              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    tweet = None
    tweet_url = None
    
    # 步骤 1: 获取推文
    print("\n📍 步骤 1: 获取推文")
    print("=" * 60)
    
    if args.search:
        print(f"🔍 搜索模式：{args.search}")
        # 打开搜索页面
        import urllib.parse
        encoded = urllib.parse.quote(f"{args.search} -filter:replies -filter:retweets")
        url = f"https://twitter.com/search?q={encoded}&f=live"
        open_url(url)
        print("\n💡 请在浏览器中选择一条推文，然后按回车继续...")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ 已取消")
            return
        
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
            print("\n❌ 无法获取推文 URL")
            return
        
        print(f"📍 推文 URL: {tweet_url}")
        
        # 让用户输入推文内容（用于 AI 生成）
        print("\n请输入推文内容（前 100 字）:")
        tweet_text = input("> ").strip()[:200]
        
        # 提取作者
        tweet_author = tweet_url.split('/')[-2] if '/status/' in tweet_url else "user"
        
        tweet = {
            'url': tweet_url,
            'text': tweet_text,
            'username': tweet_author,
            'name': tweet_author,
            'likes': '0',
            'replies': '0',
            'retweets': '0',
            'views': '0'
        }
    else:
        print("🏠 Home 模式")
        # 打开 Home 页面
        open_url("https://twitter.com/home")
        print("\n💡 请在浏览器中选择一条推文，然后按回车继续...")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ 已取消")
            return
        
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
            print("\n❌ 无法获取推文 URL")
            return
        
        print(f"📍 推文 URL: {tweet_url}")
        
        # 让用户输入推文内容
        print("\n请输入推文内容（前 100 字）:")
        tweet_text = input("> ").strip()[:200]
        
        tweet_author = tweet_url.split('/')[-2] if '/status/' in tweet_url else "user"
        
        tweet = {
            'url': tweet_url,
            'text': tweet_text,
            'username': tweet_author,
            'name': tweet_author,
            'likes': '0',
            'replies': '0',
            'retweets': '0',
            'views': '0'
        }
    
    if not tweet:
        print("\n❌ 流程终止")
        return
    
    # 步骤 2: 生成回复
    print("\n\n📍 步骤 2: 生成回复建议")
    print("=" * 60)
    replies = generate_replies(tweet)
    
    # 步骤 3: 发送到 Telegram
    print("\n\n📍 步骤 3: 发送到 Telegram")
    print("=" * 60)
    
    message = format_message(tweet, replies)
    buttons = create_buttons(tweet, replies)
    
    msg_id = send_telegram_message(message, buttons)
    
    if msg_id:
        print("\n✅ 消息已发送到 Telegram")
    else:
        print("\n✅ 已输出到控制台")
    
    # 步骤 4: 自动评论选项
    if args.auto:
        print("\n" + "=" * 60)
        print("🤖 自动评论模式")
        print("=" * 60)
        
        print("\n请选择回复编号 [1-3]，或按 Enter 跳过:")
        for i, reply in enumerate(replies, 1):
            print(f"   [{i}] {reply}")
        
        try:
            choice = input("\n选择：").strip()
            
            if choice in ['1', '2', '3']:
                index = int(choice) - 1
                selected_reply = replies[index]
                
                print(f"\n✅ 已选择：{selected_reply}")
                
                # 确认
                confirm = input("是否执行自动评论？[y/N]: ").strip().lower()
                if confirm in ['y', 'yes']:
                    # 执行自动评论
                    print("\n🚀 开始自动评论...")
                    auto_comment(tweet.get('url', ''), selected_reply)
                else:
                    print("\n✅ 已取消自动评论")
            else:
                print("\n✅ 已跳过")
        except KeyboardInterrupt:
            print("\n\n✅ 已取消")
        except EOFError:
            print("\n✅ 已跳过")
    
    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
