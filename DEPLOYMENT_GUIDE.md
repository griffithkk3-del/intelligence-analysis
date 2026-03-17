# 🚀 AI 情报中心 - 自动化数据获取系统部署指南

## 📋 系统概述

### 新系统特性

✅ **真实数据获取**：
- 通过 Serper API 搜索 SimilarWeb 数据
- 通过 GitHub API 获取 Stars/Forks
- 所有数据标注来源和获取时间
- 无数据时返回 None，不编造

✅ **完整错误处理**：
- 所有网络请求都有 try/except
- API 失败时优雅降级
- 详细的错误日志

✅ **数据验证**：
- 验证数据来源标注
- 检查数据合理性
- 检测过期数据
- 防止模拟数据

✅ **安全性**：
- API Key 从环境变量读取
- 不硬编码敏感信息
- Git 历史中无泄露

---

## 🔧 部署步骤

### 步骤 1：撤销泄露的 API Key（重要！）

**当前泄露的 Key**：`374959ea28cae888d8049ea2e34d8acc156c602b`

**立即行动**：

1. **登录 Serper.dev**：
   ```
   https://serper.dev/dashboard
   ```

2. **撤销旧 Key**：
   - 找到泄露的 Key
   - 点击"Revoke"或"Delete"

3. **生成新 Key**：
   - 点击"Create New API Key"
   - 复制新 Key（只显示一次）

4. **设置环境变量**：
   ```bash
   # 添加到 ~/.zshrc 或 ~/.bash_profile
   echo 'export SERPER_API_KEY="your_new_api_key_here"' >> ~/.zshrc
   source ~/.zshrc
   
   # 验证
   echo $SERPER_API_KEY
   ```

---

### 步骤 2：部署新脚本到项目

```bash
# 进入项目目录
cd ~/.openclaw/workspace/shared/artifacts/competitor-site

# 备份旧脚本
mv daily_update.py daily_update_old.py
mv validate_data.py validate_data_old.py

# 复制新脚本
cp daily_update_v2.py daily_update.py
cp validate_data_v2.py validate_data.py

# 添加执行权限
chmod +x daily_update.py validate_data.py daily_update.sh

# 创建日志目录
mkdir -p logs
```

---

### 步骤 3：测试新系统

#### 3.1 测试数据获取

```bash
cd ~/.openclaw/workspace/shared/artifacts/competitor-site

# 确保环境变量已设置
export SERPER_API_KEY="your_new_api_key_here"

# 测试单个网站数据获取
python3 << 'EOF'
from daily_update import get_real_traffic_data

# 测试获取数据
data = get_real_traffic_data("theresanaiforthat.com")
if data:
    print(f"✅ 成功获取数据:")
    print(f"   月访问: {data['monthlyVisits']:,}")
    print(f"   数据来源: {data['dataSource']}")
    print(f"   获取时间: {data['dataFetchedAt']}")
else:
    print("❌ 获取数据失败")
EOF
```

#### 3.2 测试完整更新流程

```bash
# 运行完整更新（只更新一个站点测试）
python3 daily_update.py

# 查看输出，确认：
# ✅ 搜索成功
# ✅ 数据解析成功
# ✅ 数据已保存
```

#### 3.3 测试数据验证

```bash
# 运行验证脚本
python3 validate_data.py

# 预期输出：
# ✅ data.json: 通过验证
# ✅ cn/data.json: 通过验证
# ...
```

---

### 步骤 4：设置定时任务

#### 方法 A：使用 OpenClaw 定时任务（推荐）

1. **编辑配置文件**：
   ```bash
   vim ~/.openclaw-nexus/.openclaw/openclaw.json
   ```

2. **添加定时任务**（在 `schedules` 部分）：
   ```json
   {
     "schedules": {
       "ai-intelligence-daily-update": {
         "cron": "0 9 * * *",
         "command": "bash ~/.openclaw/workspace/shared/artifacts/competitor-site/daily_update.sh",
         "enabled": true,
         "description": "AI 情报中心每日数据更新",
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

4. **验证任务已加载**：
   ```bash
   openclaw status | grep schedule
   ```

#### 方法 B：使用 cron（备选）

```bash
# 编辑 crontab
crontab -e

# 添加任务（每天 9:00）
0 9 * * * cd ~/.openclaw/workspace/shared/artifacts/competitor-site && bash daily_update.sh

# 保存并退出
# 验证
crontab -l
```

---

### 步骤 5：推送到 GitHub

```bash
cd ~/.openclaw/workspace/shared/artifacts/competitor-site

# 添加新文件
git add daily_update.py validate_data.py daily_update.sh
git add SCHEDULE_SETUP.md DEPLOYMENT_GUIDE.md

# 提交
git commit -m "feat: 实现真实数据自动获取系统

- 通过 Serper 搜索 SimilarWeb 数据
- 通过 GitHub API 获取仓库数据
- 所有数据标注来源和获取时间
- 完整的错误处理和数据验证
- 修复 API Key 泄露问题
- 添加定时任务支持"

# 推送
git push
```

---

## 📊 使用指南

### 手动更新数据

```bash
cd ~/.openclaw/workspace/shared/artifacts/competitor-site

# 更新所有站点
python3 daily_update.py

# 只更新特定站点
python3 daily_update.py --site global
python3 daily_update.py --site cn
```

### 验证数据

```bash
# 验证所有数据
python3 validate_data.py

# 只验证特定文件
python3 validate_data.py data.json
```

### 查看日志

```bash
# 查看今天的日志
tail -f logs/daily_update_$(date +%Y%m%d).log

# 查看所有日志
ls -lh logs/

# 查看最近的错误
grep "❌" logs/daily_update_*.log | tail -20
```

---

## 🔍 数据来源说明

### 流量数据

**来源**：SimilarWeb（通过 Serper 搜索）

**获取方式**：
1. 搜索：`site:similarweb.com {domain} monthly visits traffic`
2. 解析搜索结果中的流量数据
3. 提取：月访问量、全球排名

**数据字段**：
```json
{
  "monthlyVisits": 4500000,
  "globalRank": 9351,
  "dataSource": "SimilarWeb",
  "dataSourceUrl": "https://www.similarweb.com/website/...",
  "dataFetchedAt": "2026-03-17T12:00:00+08:00",
  "dataVerified": true
}
```

### GitHub 数据

**来源**：GitHub API

**获取方式**：
1. 调用：`https://api.github.com/repos/{owner}/{repo}`
2. 提取：Stars、Forks、最后更新时间

**数据字段**：
```json
{
  "githubStars": 12500,
  "githubForks": 1200,
  "githubUpdatedAt": "2026-03-17T10:30:00Z",
  "dataSource": "GitHub API"
}
```

### 无数据情况

如果无法获取数据：
- ✅ 返回 `None`
- ✅ 字段设为 `null`
- ❌ 不编造数据
- ❌ 不使用默认值

---

## ⚠️ 注意事项

### 1. API 配额限制

**Serper API**：
- 免费版：2,500 次/月
- 付费版：根据套餐

**GitHub API**：
- 未认证：60 次/小时
- 认证后：5,000 次/小时

**建议**：
- 每天只更新一次
- 使用缓存策略（数据 7 天内不重复获取）
- 监控 API 使用量

### 2. 数据准确性

**SimilarWeb 数据**：
- 是估算值，不是精确值
- 小网站数据可能不准确
- 建议标注"估算"

**GitHub 数据**：
- 是实时准确的
- 可以完全信任

### 3. 错误处理

**网络错误**：
- 自动重试（最多 3 次）
- 失败后跳过该网站
- 记录错误日志

**数据解析错误**：
- 返回 None
- 不影响其他网站
- 记录警告日志

---

## 📈 监控和维护

### 每日检查清单

- [ ] 查看日志，确认更新成功
- [ ] 检查 GitHub 是否有新提交
- [ ] 验证数据是否有来源标注
- [ ] 检查是否有错误或警告

### 每周检查清单

- [ ] 检查 API 配额使用情况
- [ ] 验证数据准确性（抽查 5-10 个网站）
- [ ] 清理旧日志（保留 30 天）
- [ ] 检查 Git 仓库大小

### 每月检查清单

- [ ] 审查数据质量
- [ ] 更新数据源（如有新的数据源）
- [ ] 优化脚本性能
- [ ] 备份重要数据

---

## 🐛 故障排查

### 问题 1：API Key 错误

**症状**：
```
❌ Serper HTTP 错误: 401 - Unauthorized
```

**解决**：
```bash
# 检查环境变量
echo $SERPER_API_KEY

# 重新设置
export SERPER_API_KEY="your_api_key"

# 测试 API
curl -X POST https://google.serper.dev/search \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'
```

### 问题 2：无法获取数据

**症状**：
```
⚠️  未找到数据
```

**原因**：
- SimilarWeb 没有该网站数据
- 搜索结果格式变化
- 网站域名错误

**解决**：
1. 手动访问 SimilarWeb 确认是否有数据
2. 检查域名是否正确
3. 查看搜索结果原始数据

### 问题 3：Git 推送失败

**症状**：
```
❌ Git 操作失败
```

**解决**：
```bash
# 检查 Git 状态
git status

# 检查远程仓库
git remote -v

# 测试连接
ssh -T git@github.com

# 手动推送
git push
```

---

## 📚 相关文档

- [SCHEDULE_SETUP.md](./SCHEDULE_SETUP.md) - 定时任务配置详解
- [DATA_RULES.md](./DATA_RULES.md) - 数据规范
- [OPTIMIZATION_REPORT.md](./OPTIMIZATION_REPORT.md) - 网站优化报告

---

## 🎯 下一步优化

### 短期（1-2 周）

- [ ] 添加更多数据源（Ahrefs, SEMrush）
- [ ] 实现并行数据获取（提升速度）
- [ ] 添加数据可视化（趋势图）

### 中期（1-2 月）

- [ ] 实现智能缓存策略
- [ ] 添加异常检测（数据突变告警）
- [ ] 集成飞书通知（更新完成通知）

### 长期（3-6 月）

- [ ] 机器学习预测流量趋势
- [ ] 自动发现新竞品
- [ ] 构建完整的竞品分析平台

---

*创建时间：2026-03-17*
*作者：小满 AI 助手*
*版本：v2.0*
