#!/usr/bin/env python3
import time
import random
import os
import json
import requests
import pychrome
import subprocess
import socket

# 手动加载.env文件，不需要第三方依赖
DOUBO_API_KEY = ""
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                os.environ[key] = value
                if key == "DOUBO_API_KEY":
                    DOUBO_API_KEY = value

# 自动检测并启动带调试模式的Chrome
CDP_PORT = 9222
def is_chrome_running():
    """检测Chrome调试端口是否可用"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", CDP_PORT))
        s.close()
        return True
    except:
        return False

if not is_chrome_running():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到Chrome调试模式未启动，自动启动中...")
    # 自动获取当前用户的Chrome数据路径
    chrome_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    # 后台启动Chrome，不输出日志
    cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={chrome_data_dir}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    # 等待Chrome启动完成
    time.sleep(10)
    # 再次检测
    for i in range(5):
        if is_chrome_running():
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Chrome调试模式启动成功")
            break
        time.sleep(2)
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Chrome启动失败，请手动启动")
        exit(1)

# 配置项
PROCESSED_IDS_FILE = "./replied-tweet-ids.txt"
SEARCH_KEYWORD = "独立开发 远程工作 AI工具"
REPLY_PROMPT = "你是一个关注独立开发、远程工作、AI工具方向的Twitter用户，针对下面这条推文，生成一条自然、口语化的评论，不要太官方，不要用生硬的语气，长度控制在15-80字，可以适当加emoji，不要加话题标签，像真人发的评论一样。"
CDP_PORT = 9222

# 随机延迟0-300秒
sleep_sec = random.randint(0, 300)
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 随机等待 {sleep_sec} 秒...")
time.sleep(sleep_sec)

# 加载已回复ID
processed_ids = set()
if os.path.exists(PROCESSED_IDS_FILE):
    with open(PROCESSED_IDS_FILE, "r") as f:
        processed_ids = set([line.strip() for line in f.readlines()])

def generate_reply(tweet_text):
    """调用豆包AI生成回复"""
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBO_API_KEY}"
    }
    data = {
        "model": "doubao-seed-2.0-pro",
        "messages": [
            {"role": "system", "content": REPLY_PROMPT},
            {"role": "user", "content": tweet_text}
        ],
        "temperature": 0.8,
        "max_tokens": 100
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        return resp.json()["choices"][0]["message"]["content"].strip()[:270]
    except Exception as e:
        print(f"AI生成回复失败: {str(e)}")
        return None

try:
    # 连接Chrome调试端口
    browser = pychrome.Browser(url=f"http://127.0.0.1:{CDP_PORT}")
    tab = browser.new_tab()
    tab.start()

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 打开Twitter搜索页...")
    search_url = f"https://x.com/search?q={SEARCH_KEYWORD.replace(' ', '%20')}&f=live"
    tab.Page.navigate(url=search_url)
    # 等待页面加载
    time.sleep(10)

    # 提取第一条推文
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 提取第一条推文...")
    result = tab.Runtime.evaluate(expression="""
        () => {
            const tweets = document.querySelectorAll('article[data-testid="tweet"]');
            for (let tweet of tweets) {
                const link = tweet.querySelector('a[href*="/status/"]');
                if (!link) continue;
                const url = 'https://x.com' + link.getAttribute('href');
                const id = url.split('/').pop();
                const text = tweet.querySelector('div[data-testid="tweetText"]')?.innerText || '';
                return {id, url, text};
            }
            return null;
        }
    """)

    tweet_info = result.get('result', {}).get('value', None)
    if not tweet_info or not tweet_info.get('id'):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 未找到推文")
        browser.close_tab(tab)
        exit(0)

    tweet_id = tweet_info['id']
    tweet_url = tweet_info['url']
    tweet_text = tweet_info['text']

    # 检查是否已回复
    if tweet_id in processed_ids:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 推文已回复过，跳过")
        browser.close_tab(tab)
        exit(0)

    print(f"推文URL: {tweet_url}")
    print(f"推文ID: {tweet_id}")
    print(f"推文内容: {tweet_text}")

    # 生成回复
    reply_text = generate_reply(tweet_text)
    if not reply_text:
        browser.close_tab(tab)
        exit(1)
    print(f"生成回复: {reply_text}")

    # 打开推文详情页
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 打开推文详情页...")
    tab.Page.navigate(url=tweet_url)
    time.sleep(5)

    # 点击评论按钮
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 点击评论按钮...")
    tab.Runtime.evaluate(expression="""
        () => document.querySelector('button[data-testid="reply"]')?.click()
    """)
    time.sleep(2)

    # 输入回复内容
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 输入回复内容...")
    reply_text_escaped = reply_text.replace('"', '\\"').replace("'", "\\'")
    tab.Runtime.evaluate(expression=f"""
        () => {{
            const textarea = document.querySelector('div[data-testid="tweetTextarea_0"]');
            if (textarea) {{
                textarea.focus();
                document.execCommand('insertText', false, "{reply_text_escaped}");
                return true;
            }}
            return false;
        }}
    """)
    time.sleep(1)

    # 点击发送按钮
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 发送评论...")
    tab.Runtime.evaluate(expression="""
        () => document.querySelector('button[data-testid="tweetButton"]')?.click()
    """)
    time.sleep(3)

    # 记录已回复
    with open(PROCESSED_IDS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

    # 发送通知
    notify_msg = f"""✅ Twitter自动回复成功！
📌 推文链接: {tweet_url}
📝 推文内容: {tweet_text}
💬 回复内容: {reply_text}"""
    os.system(f'''openclaw message action=send message="{notify_msg.replace('"', '\\"')}"''')

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 回复完成！")

except Exception as e:
    print(f"执行出错: {str(e)}")
finally:
    try:
        browser.close_tab(tab)
    except:
        pass
    try:
        tab.stop()
    except:
        pass
