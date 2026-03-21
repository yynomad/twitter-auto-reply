#!/bin/bash
# Twitter 自动回复 - 快速启动脚本

cd ~/twitter-auto-reply

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🐦 Twitter 自动回复工具                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "请选择模式:"
echo ""
echo "  [1] 终端快速版（推荐）"
echo "  [2] Telegram 版本"
echo "  [3] 查看 README"
echo ""
read -p "请输入选项 [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "启动终端快速版..."
        python3 twitter_quick_reply.py
        ;;
    2)
        echo ""
        if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
            echo "⚠️  未配置 Telegram 环境变量"
            echo ""
            echo "请先设置:"
            echo "  export TELEGRAM_BOT_TOKEN=your_token"
            echo "  export TELEGRAM_CHAT_ID=your_chat_id"
            echo ""
        else
            python3 twitter_semi_auto.py
        fi
        ;;
    3)
        cat README.md
        ;;
    *)
        echo "无效选项"
        ;;
esac
