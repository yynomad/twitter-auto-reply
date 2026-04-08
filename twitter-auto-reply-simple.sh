#!/bin/bash
set -e

# 加载环境变量
source .env

# 配置项
PROCESSED_IDS_FILE="./processed-tweet-ids.txt"
# 要搜索的关键词
SEARCH_KEYWORD="独立开发 远程工作"
# 豆包API密钥（从.env加载）
DOUBO_API_KEY=$DOUBO_API_KEY
# AI回复提示词
REPLY_PROMPT="你是一个喜欢分享独立开发经验的Twitter用户，针对下面这条推文，生成一条自然的、像真人写的评论，不要太官方，口语化一点，长度在20-100字之间，可以适当用emoji："

# 随机延迟0-300秒，实现5-10分钟随机运行
SLEEP_SEC=$((RANDOM % 300))
echo "[$(date)] 随机延迟 $SLEEP_SEC 秒..."
sleep $SLEEP_SEC

# 初始化已处理文件
touch $PROCESSED_IDS_FILE

# 1. 打开搜索页面提取最新推文
echo "[$(date)] 打开搜索页面提取推文..."
SEARCH_URL="https://x.com/search?q=$(echo $SEARCH_KEYWORD | sed 's/ /%20/g')&f=live"
open -a "Google Chrome" "$SEARCH_URL"
sleep 8

# 提取第一条推文URL
osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' > /tmp/current_twitter_url.txt
TWEET_URL=$(cat /tmp/current_twitter_url.txt)
if [[ ! $TWEET_URL == *"/status/"* ]]; then
  # 点击第一条推文进入详情页
  osascript -e 'tell application "System Events" to keystroke tab'
  osascript -e 'tell application "System Events" to keystroke return'
  sleep 5
  osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' > /tmp/current_twitter_url.txt
  TWEET_URL=$(cat /tmp/current_twitter_url.txt)
fi

TWEET_ID=$(echo $TWEET_URL | awk -F'/' '{print $NF}')
# 跳过已处理的
if grep -q "^$TWEET_ID$" $PROCESSED_IDS_FILE; then
  echo "[$(date)] 推文已处理过，关闭页面退出"
  osascript -e 'tell application "System Events" to keystroke "w" using command down'
  exit 0
fi

# 提取推文内容
osascript -e 'tell application "System Events" to keystroke "a" using command down'
osascript -e 'tell application "System Events" to keystroke "c" using command down'
pbpaste > /tmp/tweet_content.txt
TWEET_TEXT=$(grep -A 20 "·.*[0-9]h\|·.*[0-9]m" /tmp/tweet_content.txt | head -20 | tr '\n' ' ' | sed 's/  */ /g')

if [ -z "$TWEET_ID" ] || [ -z "$TWEET_TEXT" ]; then
  echo "[$(date)] 无新推文，关闭页面退出"
  osascript -e 'tell application "System Events" to keystroke "w" using command down'
  exit 0
fi

echo "选中推文：$TWEET_URL"
echo "推文内容：$TWEET_TEXT"

# 3. 生成回复
echo "生成回复..."
REPLY_TEXT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DOUBO_API_KEY" \
  -d "{
    \"model\": \"doubao-seed-2.0-pro\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"$REPLY_PROMPT\"},
      {\"role\": \"user\", \"content\": \"$TWEET_TEXT\"}
    ],
    \"temperature\": 0.8
  }" | jq -r '.choices[0].message.content' | head -c 270)

echo "回复内容：$REPLY_TEXT"

# 4. 模拟人工操作发评论（已经在推文详情页，直接操作）
echo "[$(date)] 开始操作发评论..."

# 模拟按Tab键定位到评论框
echo "定位评论框..."
osascript -e 'tell application "System Events" to keystroke tab'
osascript -e 'tell application "System Events" to keystroke tab'
sleep 1

# 复制回复内容到剪贴板
echo "复制回复内容..."
echo "$REPLY_TEXT" | pbcopy
sleep 1

# 粘贴内容
echo "粘贴回复..."
osascript -e 'tell application "System Events" to keystroke "v" using command down'
sleep 1

# 按Command+回车发送
echo "发送评论..."
osascript -e 'tell application "System Events" to keystroke return using command down'
sleep 3

# 关闭当前标签页
osascript -e 'tell application "System Events" to keystroke "w" using command down'

# 5. 记录已处理
echo $TWEET_ID >> $PROCESSED_IDS_FILE

# 6. 发送通知
openclaw message action=send message="✅ Twitter自动回复成功！
📌 推文链接: $TWEET_URL
📝 推文内容: $TWEET_TEXT
💬 回复内容: $REPLY_TEXT"

echo "[$(date)] 全部完成！"
