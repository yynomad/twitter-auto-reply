#!/usr/bin/env python3
"""
Twitter 快速回复 - 终端版

功能：
1. 抓取推文（链接、原文、互动数据）
2. 生成 3 条回复
3. 按数字选择，自动复制 + 打开
"""

import subprocess
import json
import os

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

def copy_to_clipboard(text):
    """复制到剪贴板"""
    subprocess.run(['pbcopy'], input=text.encode('utf-8'))

def open_url(url):
    """打开 URL"""
    subprocess.run(['open', url])

def grab_tweet():
    """抓取推文"""
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
            return None
        return tweet
    except:
        return None

def generate_replies(tweet):
    """生成 3 条回复"""
    text = tweet.get('text', '')
    
    if '?' in text or '？' in text:
        return [
            "好问题！我也在想这个，蹲一个答案~ 🤔",
            "这个得看具体情况，不过一般来说...",
            "有人知道吗？同求解答！"
        ]
    elif '😂' in text or '哈哈' in text:
        return [
            "哈哈哈哈笑死我了😂",
            "太真实了，无法反驳！",
            "这个我必须点赞，太逗了~"
        ]
    else:
        return [
            "确实是这样，深有同感~ 👍",
            "第一次见到这种，长见识了！",
            "求更多细节！👀"
        ]

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           🐦 Twitter 快速回复                              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 抓取推文
    tweet = grab_tweet()
    if not tweet:
        print("\n❌ 未找到推文")
        return
    
    # 显示推文信息
    text = tweet.get('text', 'N/A')
    if len(text) > 150:
        text = text[:150] + "..."
    
    print(f"\n👤 {tweet.get('name', 'N/A')} (@{tweet.get('username', 'N/A')})")
    print(f"\n📝 {text}\n")
    print(f"📈 👍 {tweet.get('likes')}  💬 {tweet.get('replies')}  🔄 {tweet.get('retweets')}  👁️ {tweet.get('views')}")
    print(f"\n🔗 链接：{tweet.get('url', 'N/A')}")
    
    # 生成回复
    replies = generate_replies(tweet)
    
    print("\n" + "=" * 60)
    print("💡 回复建议（输入数字选择，或按 Enter 跳过）:")
    print("=" * 60)
    
    for i, reply in enumerate(replies, 1):
        print(f"\n  [{i}] {reply}")
    
    print("\n" + "=" * 60)
    
    # 用户选择
    try:
        choice = input("\n请选择 [1-3]: ").strip()
        
        if choice in ['1', '2', '3']:
            index = int(choice) - 1
            selected = replies[index]
            
            # 复制到剪贴板
            copy_to_clipboard(selected)
            print(f"\n✅ 已复制：{selected}")
            
            # 打开推文
            url = tweet.get('url', '')
            if url:
                open_url(url)
                print(f"✅ 已打开：{url}")
            
            print("\n💡 下一步:")
            print("   1. 在打开的页面中找到评论框")
            print("   2. 粘贴回复 (Cmd+V)")
            print("   3. 点击发送\n")
        else:
            print("\n✅ 已跳过")
            print(f"🔗 推文链接：{tweet.get('url', '')}")
    
    except KeyboardInterrupt:
        print("\n\n✅ 已取消")
    except EOFError:
        print("\n✅ 已跳过")

if __name__ == "__main__":
    main()
