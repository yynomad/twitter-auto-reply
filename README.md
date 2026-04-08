# Twitter 全自动回复工具集
零配置、多方案、无风控的Twitter自动回复工具，完全模拟真人操作，不需要X开发者账号/API权限。

---
## 📦 包含的版本
| 文件名 | 方案 | 依赖 | 系统权限要求 | 特点 |
| --- | --- | --- | --- | --- |
| `twitter-auto-reply-cdp.py` | **Chrome CDP远程调试方案（推荐）** | Python3 + requests + pychrome | ❌ 无任何系统权限要求 | ✅ 稳定性最高、后台运行不影响使用、操作精准、长期可用 |
| `twitter-auto-reply-final.sh` | AppleScript模拟键盘操作方案 | bash + curl + jq | ⚠️ 需要开启辅助功能权限 | ✅ 不需要改Chrome启动方式，适合临时使用 |
| `twitter-auto-reply-simple.sh` | 极简浏览器模拟方案 | bash + curl + jq | ⚠️ 需要开启辅助功能权限 | ✅ 零依赖，逻辑简单易修改 |
| `twitter-auto-reply.py` | Playwright自动化方案 | Python3 + playwright + requests | ❌ 无系统权限要求 | ✅ 跨平台支持，适合Windows/Linux用户 |
| `twitter-full-browser-reply.sh` | 全浏览器操作方案 | bash + curl + jq | ⚠️ 需要开启辅助功能权限 | ✅ 完全模拟手动操作流程 |
| `twitter-human-like-reply.sh` | 模拟真人随机操作方案 | bash + curl + jq | ⚠️ 需要开启辅助功能权限 | ✅ 随机延迟+随机操作间隔，风控概率最低 |

---
## ✨ 核心特性
1. **零开发者权限**：不需要申请X/Twitter开发者账号，不需要API密钥，用你自己Chrome的登录态即可
2. **自动去重**：已回复的推文ID自动记录，永远不会重复回复同一条
3. **AI智能回复**：默认对接火山方舟豆包大模型，可自定义回复风格/领域
4. **真人模拟**：内置随机延迟、随机操作间隔，完全模拟真人操作习惯，几乎不会被风控
5. **结果通知**：回复完成自动推送通知，包含推文链接+原文+回复内容，随时可校验

---
## 🚀 推荐方案快速开始（CDP版）
### 1. 安装依赖
```bash
pip3 install requests pychrome
```
### 2. 配置.env
在当前目录创建`.env`文件，填入你的豆包API密钥：
```env
DOUBO_API_KEY=你的豆包API密钥
```
### 3. 运行脚本
```bash
python3 twitter-auto-reply-cdp.py
```
脚本会自动启动带调试模式的Chrome，全程无需手动操作。

---
## ⚙️ 自定义配置
修改脚本开头的配置项即可：
- `SEARCH_KEYWORD`：要搜索的领域关键词，比如`"独立开发 AI工具 SaaS"`
- `REPLY_PROMPT`：自定义回复风格/语气/语言
- `PROCESSED_IDS_FILE`：已回复ID存储路径

---
## 📌 定时运行
使用OpenClaw cron定时任务每10分钟运行一次：
```
/cron add --name "Twitter自动回复" --schedule '{"kind": "every", "everyMs": 600000}' --payload '{"kind": "systemEvent", "text": "cd /your/path/twitter-auto-reply && python3 twitter-auto-reply-cdp.py"}'
```
