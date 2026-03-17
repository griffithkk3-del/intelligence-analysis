# AI 情报中心 - 定时任务配置指南

## 📅 定时任务设置

### 方法 1：使用 OpenClaw 定时任务（推荐）

OpenClaw 内置定时任务系统，可以在 `openclaw.json` 中配置。

#### 配置步骤：

1. **编辑配置文件**：
   ```bash
   vim ~/.openclaw-nexus/.openclaw/openclaw.json
   ```

2. **添加定时任务**：
   ```json
   {
     "schedules": {
       "ai-intelligence-daily-update": {
         "cron": "0 9 * * *",
         "command": "bash ~/.openclaw/workspace/shared/artifacts/competitor-site/daily_update.sh",
         "enabled": true,
         "description": "AI 情报中心每日数据更新（每天 9:00）",
         "env": {
           "SERPER_API_KEY": "${SERPER_API_KEY}"
         }
       }
     }
   }
   ```

3. **重启 Gateway**：
   ```bash
   launchctl stop ai.openclaw.gateway-nexus
   launchctl start ai.openclaw.gateway-nexus
   ```

#### Cron 表达式说明：

| 表达式 | 说明 |
|--------|------|
| `0 9 * * *` | 每天 9:00 |
| `0 */6 * * *` | 每 6 小时 |
| `0 0 * * 0` | 每周日 0:00 |
| `0 0 1 * *` | 每月 1 号 0:00 |

---

### 方法 2：使用 macOS launchd（备选）

如果不想用 OpenClaw 定时任务，可以使用 macOS 原生的 launchd。

#### 创建 plist 文件：

```bash
cat > ~/Library/LaunchAgents/com.intelligence-analysis.daily-update.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.intelligence-analysis.daily-update</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/tkzz/.openclaw/workspace/shared/artifacts/competitor-site/daily_update.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/Users/tkzz/.openclaw/workspace/shared/artifacts/competitor-site/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/tkzz/.openclaw/workspace/shared/artifacts/competitor-site/logs/launchd.error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>SERPER_API_KEY</key>
        <string>YOUR_API_KEY_HERE</string>
    </dict>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
```

#### 加载任务：

```bash
launchctl load ~/Library/LaunchAgents/com.intelligence-analysis.daily-update.plist
launchctl start com.intelligence-analysis.daily-update
```

#### 管理命令：

```bash
# 查看状态
launchctl list | grep intelligence-analysis

# 停止任务
launchctl stop com.intelligence-analysis.daily-update

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.intelligence-analysis.daily-update.plist
```

---

### 方法 3：使用 cron（最简单）

#### 编辑 crontab：

```bash
crontab -e
```

#### 添加任务：

```cron
# AI 情报中心每日更新（每天 9:00）
0 9 * * * cd ~/.openclaw/workspace/shared/artifacts/competitor-site && bash daily_update.sh
```

#### 查看任务：

```bash
crontab -l
```

---

## 🔧 手动测试

在设置定时任务前，先手动测试一次：

```bash
cd ~/.openclaw/workspace/shared/artifacts/competitor-site

# 设置环境变量
export SERPER_API_KEY="your_api_key_here"

# 运行更新脚本
bash daily_update.sh
```

---

## 📊 监控和日志

### 查看日志：

```bash
# 查看最新日志
tail -f ~/.openclaw/workspace/shared/artifacts/competitor-site/logs/daily_update_$(date +%Y%m%d).log

# 查看所有日志
ls -lh ~/.openclaw/workspace/shared/artifacts/competitor-site/logs/
```

### 日志保留策略：

- 自动保留最近 30 天的日志
- 旧日志自动删除

---

## ⚠️ 注意事项

### 1. API Key 安全

**❌ 错误做法**：
```bash
export SERPER_API_KEY="374959ea28cae888d8049ea2e34d8acc156c602b"  # 硬编码
```

**✅ 正确做法**：
```bash
# 在 ~/.zshrc 或 ~/.bash_profile 中设置
echo 'export SERPER_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Git 配置

确保 Git 已配置好 SSH key 或 HTTPS 认证：

```bash
# 测试 Git 推送
cd ~/.openclaw/workspace/shared/artifacts/competitor-site
git push
```

### 3. 网络连接

定时任务运行时，确保：
- 网络连接正常
- 可以访问 GitHub
- 可以访问 Serper API

---

## 🧪 测试清单

在启用定时任务前，完成以下测试：

- [ ] 手动运行 `daily_update_v2.py` 成功
- [ ] 手动运行 `validate_data_v2.py` 通过
- [ ] 手动运行 `daily_update.sh` 成功
- [ ] Git 推送成功
- [ ] 日志文件正常生成
- [ ] 环境变量正确设置

---

## 📞 故障排查

### 问题 1：脚本没有执行

**检查**：
```bash
# 检查定时任务是否加载
launchctl list | grep intelligence-analysis

# 查看日志
cat ~/.openclaw/workspace/shared/artifacts/competitor-site/logs/launchd.error.log
```

### 问题 2：API Key 错误

**检查**：
```bash
# 验证环境变量
echo $SERPER_API_KEY

# 测试 API
curl -X POST https://google.serper.dev/search \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'
```

### 问题 3：Git 推送失败

**检查**：
```bash
# 测试 SSH
ssh -T git@github.com

# 或测试 HTTPS
git remote -v
```

---

## 📈 性能优化

### 1. 并行处理

如果网站数量很多，可以并行获取数据：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(get_real_traffic_data, site) for site in sites]
    results = [f.result() for f in futures]
```

### 2. 缓存策略

避免频繁请求同一个网站：

```python
# 如果数据不到 7 天，跳过更新
if is_data_fresh(competitor, max_age_days=7):
    print(f"  ⏭️  数据仍然新鲜，跳过")
    continue
```

### 3. 速率限制

避免触发 API 限流：

```python
import time

for site in sites:
    get_real_traffic_data(site)
    time.sleep(2)  # 每次请求间隔 2 秒
```

---

## 🎯 推荐配置

**生产环境推荐**：
- 使用 OpenClaw 定时任务（方法 1）
- 每天 9:00 更新一次
- 保留 30 天日志
- 启用数据验证

**开发环境推荐**：
- 手动运行测试
- 每次修改后验证
- 查看详细日志

---

*创建时间：2026-03-17*
*更新时间：2026-03-17*
