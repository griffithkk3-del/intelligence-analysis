# AI 情报中心 - 数据规范

## 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 唯一标识，小写+连字符 | `anthropic-connectors` |
| `name` | 显示名称 | `Anthropic Connectors` |
| `domain` | **显示给用户的域名，必须与 url 路径一致** | `support.anthropic.com` |
| `url` | **实际跳转链接** | `https://support.anthropic.com/...` |
| `type` | 分类 | `MCP 官方` |

## 核心规则

### 规则 1：domain 和 url 必须一致

```
✅ 正确：
domain: "lobehub.com/skills"
url: "https://lobehub.com/skills"

❌ 错误：
domain: "claude.com/connectors"
url: "https://support.anthropic.com/..."  # 主域名不同！
```

### 规则 2：domain 格式

- 不带协议（无 `https://`）
- 不带 `www.`（除非必要）
- 可以带路径（如 `github.com/user/repo`）
- 末尾不带 `/`

### 规则 3：url 格式

- 必须带协议（`https://`）
- 必须是可访问的完整链接
- 末尾可带或不带 `/`

## 校验脚本

添加新数据后，运行校验：

```bash
cd ~/.openclaw/workspace/shared/artifacts/competitor-site
python3 validate_data.py
```

## 添加新网站流程

1. 先访问目标网站，复制实际 URL
2. 从 URL 提取 domain（去掉协议和 www.）
3. 填写 data.json
4. 运行校验脚本
5. git commit & push

---

*创建时间：2026-03-17*
