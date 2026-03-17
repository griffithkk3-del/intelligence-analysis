#!/bin/bash
# AI 情报中心 - 每日自动更新任务
# 使用 OpenClaw 定时任务系统

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/logs/daily_update_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

echo "========================================" | tee -a "$LOG_FILE"
echo "AI 情报中心 - 每日自动更新" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 检查环境变量
if [ -z "$SERPER_API_KEY" ]; then
    echo "❌ 错误: SERPER_API_KEY 环境变量未设置" | tee -a "$LOG_FILE"
    exit 1
fi

# 切换到项目目录
cd "$SCRIPT_DIR"

# 拉取最新代码
echo "" | tee -a "$LOG_FILE"
echo "📥 拉取最新代码..." | tee -a "$LOG_FILE"
git pull 2>&1 | tee -a "$LOG_FILE"

# 运行数据更新脚本
echo "" | tee -a "$LOG_FILE"
echo "🔄 开始更新数据..." | tee -a "$LOG_FILE"
python3 daily_update_v2.py 2>&1 | tee -a "$LOG_FILE"

# 验证数据
echo "" | tee -a "$LOG_FILE"
echo "✅ 验证数据..." | tee -a "$LOG_FILE"
python3 validate_data_v2.py 2>&1 | tee -a "$LOG_FILE"

VALIDATION_EXIT_CODE=$?

if [ $VALIDATION_EXIT_CODE -ne 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "❌ 数据验证失败，不推送到 GitHub" | tee -a "$LOG_FILE"
    exit 1
fi

# 推送到 GitHub
echo "" | tee -a "$LOG_FILE"
echo "🚀 推送到 GitHub..." | tee -a "$LOG_FILE"

if git diff --quiet && git diff --cached --quiet; then
    echo "📝 无变更，跳过提交" | tee -a "$LOG_FILE"
else
    git add . 2>&1 | tee -a "$LOG_FILE"
    git commit -m "data: 每日自动更新 $(date '+%Y-%m-%d')" 2>&1 | tee -a "$LOG_FILE"
    git push 2>&1 | tee -a "$LOG_FILE"
    echo "✅ 推送成功" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "✅ 每日更新完成" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 清理旧日志（保留最近 30 天）
find "$SCRIPT_DIR/logs" -name "daily_update_*.log" -mtime +30 -delete

exit 0
