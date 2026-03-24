#!/bin/bash
# Twitter 自动回复 - 一键启动脚本

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载 .env 配置
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ 已加载 .env 配置"
else
    echo "⚠️  未找到 .env 文件，请检查配置"
    exit 1
fi

# 显示帮助
show_help() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           🐦 Twitter 自动回复                              ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "用法:"
    echo "  ./start.sh              # 默认搜索 AI"
    echo "  ./start.sh AI           # 搜索 AI"
    echo "  ./start.sh technology   # 搜索 technology"
    echo "  ./start.sh auto         # 自动评论模式（搜索 AI）"
    echo "  ./start.sh -h           # 显示帮助"
    echo ""
}

# 解析参数
MODE="semi"  # semi=半自动，auto=自动评论
SEARCH_QUERY="AI"

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
    exit 0
fi

if [ "$1" == "auto" ]; then
    MODE="auto"
elif [ -n "$1" ]; then
    SEARCH_QUERY="$1"
fi

# 执行脚本
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 启动 Twitter 自动回复"
echo "   模式：$([ "$MODE" == "auto" ] && echo "🤖 自动评论" || echo "📤 半自动")"
echo "   搜索：$SEARCH_QUERY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$MODE" == "auto" ]; then
    python3 twitter_semi_auto.py --search "$SEARCH_QUERY" --auto
else
    python3 twitter_semi_auto.py --search "$SEARCH_QUERY"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 执行完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
