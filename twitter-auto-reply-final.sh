#!/bin/bash
set +e

# 加载环境变量（从你配置好的.env里读豆包API密钥）
source .env

# 配置项
PROCESSED_IDS_FILE="./replied-tweet-ids.txt"
# 要搜索的关键词，可自定义
SEARCH_KEYWORD="独立开发 远程工作 AI工具"
# AI回复提示词，可自定义回复风格
REPLY_PROMPT="你是一个关注独立开发、远程工作、AI工具方向的Twitter用户，针对下面这条推文，生成一条自然、口语化的评论，不要太官方，不要用生硬的语气，长度控制在15-80字，可以适当加emoji，不要加话题标签，像真人发的评论一样。"
# 最大重试次数
MAX_RETRY=3

# 随机延迟0-300秒，模拟真人随机刷推的时间，避免被风控
SLEEP_SEC=$((RANDOM % 300))
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 随机等待 $SLEEP_SEC 秒模拟真人行为..."
sleep $SLEEP_SEC

# 初始化已回复ID文件
touch $PROCESSED_IDS_FILE

# 通用重试函数
retry() {
    local n=1
    local max=$MAX_RETRY
    local delay=2
    while true; do
        "$@" && break || {
            if [[ $n -lt $max ]]; then
                ((n++))
                echo "操作失败，$delay 秒后重试第 $n 次..."
                sleep $delay;
            else
                echo "操作失败超过 $max 次，放弃"
                return 1
            fi
        }
    done
}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动Chrome浏览器打开Twitter搜索页..."
# 打开Chrome，用你已有的登录态，不需要重复登录
retry open -a "Google Chrome" "https://x.com/search?q=$(echo $SEARCH_KEYWORD | sed 's/ /%20/g')&f=live"
sleep 10 # 等待页面完全加载

# 等待推文加载完成
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 等待推文加载..."
sleep 5

# 提取第一条推文的URL和ID
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 提取第一条推文..."
osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' > /tmp/current_twitter_url.txt
TWEET_URL=$(cat /tmp/current_twitter_url.txt)

# 如果当前页面不是推文详情页，点击第一条推文进入
if [[ ! $TWEET_URL == *"/status/"* ]]; then
    echo "点击第一条推文进入详情页..."
    retry osascript -e 'tell application "System Events" to keystroke tab'
    retry osascript -e 'tell application "System Events" to keystroke return'
    sleep 8
    osascript -e 'tell application "Google Chrome" to get URL of active tab of front window' > /tmp/current_twitter_url.txt
    TWEET_URL=$(cat /tmp/current_twitter_url.txt)
fi

TWEET_ID=$(echo $TWEET_URL | awk -F'/' '{print $NF}')
# 检查是否已经回复过这条推文
if grep -q "^$TWEET_ID$" $PROCESSED_IDS_FILE; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推文ID $TWEET_ID 已经回复过，跳过"
    osascript -e 'tell application "System Events" to keystroke "w" using command down'
    exit 0
fi

# 提取推文内容
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 提取推文内容..."
sleep 2
# 选中页面内容复制
retry osascript -e 'tell application "System Events" to keystroke "a" using command down'
retry osascript -e 'tell application "System Events" to keystroke "c" using command down'
sleep 1
pbpaste > /tmp/tweet_full_content.txt
# 提取推文正文部分
TWEET_TEXT=$(grep -A 15 "·.*[0-9]h\|·.*[0-9]m\|·.*[0-9]s" /tmp/tweet_full_content.txt | head -15 | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//g' | sed 's/ *$//g')

if [ -z "$TWEET_TEXT" ] || [ ${#TWEET_TEXT} -lt 5 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 提取推文内容失败，跳过本次运行"
    osascript -e 'tell application "System Events" to keystroke "w" using command down'
    exit 1
fi

echo "推文URL: $TWEET_URL"
echo "推文ID: $TWEET_ID"
echo "推文内容: $TWEET_TEXT"

# 调用豆包AI生成回复
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 调用AI生成回复内容..."
REPLY_TEXT=$(curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DOUBO_API_KEY" \
  -d "{
    \"model\": \"doubao-seed-2.0-pro\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"$REPLY_PROMPT\"},
      {\"role\": \"user\", \"content\": \"$TWEET_TEXT\"}
    ],
    \"temperature\": 0.8,
    \"max_tokens\": 100
  }" | jq -r '.choices[0].message.content' | head -c 270 | sed 's/"/\\"/g')

if [ -z "$REPLY_TEXT" ] || [ "$REPLY_TEXT" == "null" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI生成回复失败，跳过本次运行"
    osascript -e 'tell application "System Events" to keystroke "w" using command down'
    exit 1
fi

echo "生成的回复: $REPLY_TEXT"

# 点击评论按钮
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 点击评论按钮..."
sleep 2
retry osascript -e 'tell application "System Events" to keystroke "r" using command down'
sleep 3

# 粘贴回复内容
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 粘贴回复内容..."
echo "$REPLY_TEXT" | pbcopy
sleep 1
retry osascript -e 'tell application "System Events" to keystroke "v" using command down'
sleep 2

# 发送评论（Command+回车）
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发送评论..."
retry osascript -e 'tell application "System Events" to keystroke return using command down'
sleep 5

# 记录已回复的ID
echo $TWEET_ID >> $PROCESSED_IDS_FILE

# 关闭当前标签页
osascript -e 'tell application "System Events" to keystroke "w" using command down'

# 给你发通知
NOTIFY_MSG="✅ Twitter自动回复成功！
📌 推文链接: $TWEET_URL
📝 推文内容: $TWEET_TEXT
💬 回复内容: $REPLY_TEXT"
openclaw message action=send message="$NOTIFY_MSG"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 全部操作完成！本次回复已记录。"
exit 0
