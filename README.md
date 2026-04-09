# Twitter 全自动回复工具
纯CDP远程调试方案，零系统权限、无风控、全自动运行的Twitter自动回复工具，不需要X开发者账号/API权限。

---
## ✨ 核心特性
1. **零开发者权限**：不需要申请X/Twitter开发者账号，不需要API密钥，用你自己Chrome的登录态即可，和手动发评论完全一致，不会触发API风控
2. **零系统权限**：不需要开启macOS辅助功能权限，不会有弹窗报错，稳定性拉满
3. **全自动运行**：自动启动Chrome、自动搜索最新推文、自动AI生成回复、自动点击发送评论、自动记录已回复ID去重
4. **真人模拟**：内置随机延迟、随机操作间隔，完全模拟真人操作习惯，几乎不会被风控
5. **结果通知**：回复完成自动推送通知，包含推文链接+原文+回复内容，随时可校验
6. **后台运行**：Chrome最小化/后台/被遮挡都能正常运行，完全不影响你使用电脑

---
## 🚀 快速开始
### 1. 安装依赖
```bash
pip3 install requests pychrome python-dotenv
```
### 2. 配置环境变量
复制`.env.example`为`.env`，填入你的豆包API密钥：
```env
DOUBO_API_KEY=你的火山方舟豆包API密钥
```
### 3. 配置Chrome启动别名（只需要配置一次）
终端执行：
```bash
echo 'alias chrome="killall -9 \'Google Chrome\' 2>/dev/null; /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=\"\$HOME/Library/Application Support/Google/Chrome\" >/dev/null 2>&1 &"' >> ~/.zshrc && source ~/.zshrc
```
### 4. 运行
终端执行`chrome`启动带调试模式的Chrome（和你平时用的Chrome完全一样，所有登录态/书签/插件都保留），然后执行：
```bash
python3 twitter-auto-reply-cdp.py
```

---
## ⚙️ 自定义配置
修改`twitter-auto-reply-cdp.py`开头的配置项即可：
- `SEARCH_KEYWORD`：要搜索的领域关键词，比如`"独立开发 AI工具 SaaS 远程工作"`
- `REPLY_PROMPT`：自定义回复风格/语气/领域，比如想要英文回复、更专业/更活泼的风格都可以改这里
- `CDP_PORT`：Chrome调试端口，默认9222无需修改
- `PROCESSED_IDS_FILE`：已回复ID存储路径，默认`./replied-tweet-ids.txt`

---
## 📌 定时运行
使用OpenClaw cron定时任务每10分钟运行一次，实现全自动无人值守：
```
/cron add --name "Twitter全自动回复" --schedule '{"kind": "every", "everyMs": 600000}' --payload '{"kind": "systemEvent", "text": "cd /your/path/twitter-auto-reply && python3 twitter-auto-reply-cdp.py"}'
```

---
## ❓ 常见问题
### 提示Chrome连接失败？
确保你是用`chrome`命令启动的Chrome，而不是直接点击图标启动的。如果还是失败，完全关闭Chrome后重新执行`chrome`命令即可。
### 不想每次都手动启动Chrome？
可以把`chrome`命令加到macOS开机启动项，开机自动启动带调试模式的Chrome，无需手动操作。
### 会被Twitter封号吗？
默认配置的随机延迟和真人操作模拟已经把风控概率降到最低，只要不要设置过短的运行间隔（建议至少10分钟以上运行一次），正常使用不会有问题。
