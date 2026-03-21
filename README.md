# 🐦 Twitter 自动回复工具

基于 AppleScript + Python 的 Twitter 半自动回复工具，使用真实浏览器模拟真人操作。

---

## ✨ 功能特点

- ✅ 使用真实 Chrome 浏览器（非 headless）
- ✅ 直接利用已登录的 Twitter 账号
- ✅ 自动抓取 Home 页面第一条推文
- ✅ 提取完整信息（链接、原文、点赞、评论、转发、浏览）
- ✅ 自动生成 3 条回复建议
- ✅ 一键复制 + 打开推文
- ✅ 模拟真人操作，避免风控

---

## 📦 项目结构

```
~/twitter-auto-reply/
├── README.md                    # 本文档
├── twitter_quick_reply.py       # ⭐ 终端快速版（推荐）
├── twitter_semi_auto.py         # Telegram 版本
├── twitter_bot.py               # Telegram Bot 处理器
├── grab_all_data.applescript    # AppleScript 抓取脚本
└── manual_input.applescript     # AppleScript 手动输入脚本
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# Python 3（Mac 自带）
python3 --version

# 无需额外依赖，直接使用
```

### 2. 运行（推荐）

```bash
cd ~/twitter-auto-reply
python3 twitter_quick_reply.py
```

### 3. 操作流程

```
1. 脚本自动打开 Twitter Home
2. 抓取第一条推文（显示链接、原文、互动数据）
3. 生成 3 条回复建议
4. 输入数字选择回复（1/2/3）
5. 自动复制到剪贴板 + 打开推文
6. 手动粘贴发送
```

---

## 📝 使用说明

### 终端快速版

```bash
python3 twitter_quick_reply.py
```

**输出示例：**

```
╔═══════════════════════════════════════════════════════════╗
║           🐦 Twitter 快速回复                              ║
╚═══════════════════════════════════════════════════════════╝

👤 用户名 (@username)

📝 推文内容...

📈 👍 1.2K  💬 6  🔄 6  👁️ 1.2K

🔗 链接：https://x.com/username/status/123456789

============================================================
💡 回复建议（输入数字选择，或按 Enter 跳过）:
============================================================

  [1] 确实是这样，深有同感~ 👍
  [2] 第一次见到这种，长见识了！
  [3] 求更多细节！👀

============================================================

请选择 [1-3]: 
```

### Telegram 版本

需要配置环境变量：

```bash
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id

python3 twitter_semi_auto.py
```

---

## 🔧 高级用法

### 修改回复模板

编辑 `twitter_quick_reply.py` 中的 `generate_replies()` 函数：

```python
def generate_replies(tweet):
    text = tweet.get('text', '')
    
    # 自定义回复逻辑
    if '?' in text:
        return ["问题型回复 1", "问题型回复 2", "问题型回复 3"]
    elif '😂' in text:
        return ["幽默型回复 1", "幽默型回复 2", "幽默型回复 3"]
    else:
        return ["通用回复 1", "通用回复 2", "通用回复 3"]
```

### 接入 AI 生成回复

可以接入火山方舟、OpenAI 等：

```python
import openai

def generate_replies_ai(tweet):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "生成 3 条 Twitter 回复"},
            {"role": "user", "content": tweet.get('text')}
        ]
    )
    return response.choices[0].message.content.split('\n')
```

---

## ⚠️ 注意事项

### 避免风控

1. **控制频率** - 每天不超过 10-20 条回复
2. **随机延迟** - 每条间隔 2-4 小时
3. **真实内容** - 不要回复完全相同的内容
4. **真人审核** - 半自动模式最安全

### 浏览器要求

- ✅ Google Chrome（推荐）
- ✅ 需要已登录 Twitter
- ✅ 保持至少一个 Chrome 窗口打开

---

## 🛠️ 故障排除

### 问题 1: 找不到推文

**原因**: Twitter 页面未加载完成

**解决**: 
```bash
# 手动打开 Twitter 并登录
open https://twitter.com/home

# 确保登录后再运行脚本
```

### 问题 2: AppleScript 权限

**原因**: macOS 需要授权

**解决**: 
```
系统偏好设置 → 安全性与隐私 → 隐私 → 自动化
→ 勾选 Google Chrome
```

### 问题 3: 复制失败

**原因**: pbcopy 命令问题

**解决**:
```bash
# 测试剪贴板
echo "test" | pbcopy
pbpaste  # 应该输出 test
```

---

## 📚 技术原理

```
┌─────────────┐
│  Python 脚本 │
└──────┬──────┘
       │ 生成 AppleScript
       ▼
┌─────────────┐
│ AppleScript │
└──────┬──────┘
       │ 控制 Chrome
       ▼
┌─────────────┐
│   Chrome    │
└──────┬──────┘
       │ 执行 JavaScript
       ▼
┌─────────────┐
│   Twitter   │
│  页面交互    │
└─────────────┘
```

**核心技术**:
- `document.execCommand('insertText')` - 模拟真实输入
- AppleScript - 系统级浏览器控制
- 随机延迟 - 模拟真人行为

---

## 🎯 下一步优化

- [ ] 接入 AI 生成更智能回复
- [ ] 添加推文筛选条件
- [ ] 支持多账号切换
- [ ] 添加回复历史记录
- [ ] 定时自动运行

---

## 📄 License

MIT License

---

## 🙏 致谢

- 使用真实浏览器避免风控
- AppleScript + JavaScript 模拟真人操作
- 半自动模式保证账号安全

---

**Happy Tweeting! 🐦**
