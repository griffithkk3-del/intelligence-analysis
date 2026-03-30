#!/bin/bash
# AI 情报中心 - 每日自动更新任务
# 当前主链路：daily_update.py + validate_data.py

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/daily_update_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"
cd "$SCRIPT_DIR"

# 读取本地 .env（如存在）
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

log() {
  echo "$1" | tee -a "$LOG_FILE"
}

log "========================================"
log "AI 情报中心 - 每日自动更新"
log "时间: $(date '+%Y-%m-%d %H:%M:%S')"
log "目录: $SCRIPT_DIR"
log "========================================"

log ""
log "🔐 环境检查..."
for key in TAVILY_API_KEY EXA_API_KEY SERPER_API_KEY; do
  if [ -n "${!key:-}" ]; then
    log "  - $key: 已设置"
  else
    log "  - $key: 未设置"
  fi
done

log ""
log "📥 拉取最新代码..."
git pull 2>&1 | tee -a "$LOG_FILE"

log ""
log "🔄 开始更新数据（daily_update.py）..."
python3 daily_update.py 2>&1 | tee -a "$LOG_FILE"

log ""
log "✅ 验证数据（validate_data.py）..."
python3 validate_data.py 2>&1 | tee -a "$LOG_FILE"

log ""
log "🚀 推送到 GitHub..."
if git diff --quiet && git diff --cached --quiet; then
  log "📝 无变更，跳过提交"
else
  git add . 2>&1 | tee -a "$LOG_FILE"
  git commit -m "data: 每日自动更新 $(date '+%Y-%m-%d')" 2>&1 | tee -a "$LOG_FILE"
  git push 2>&1 | tee -a "$LOG_FILE"
  log "✅ 推送成功"
fi

log ""
log "========================================"
log "✅ 每日更新完成"
log "========================================"

find "$LOG_DIR" -name "daily_update_*.log" -mtime +30 -delete || true

exit 0
