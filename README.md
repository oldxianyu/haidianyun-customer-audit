# 海典运营平台客户审核系统

[Hermes Agent](https://github.com/NousResearch/hermes-agent) 技能：自动审核海典运营平台 (op.haidianyun.com) 的客户信息草稿。

## 📋 功能特性

- ✅ 查询待审核客户列表
- ✅ 自动审核通过指定客户（按 ID 或名称）
- ✅ 支持图片识别审核（截图 → 自动匹配 → 审核）
- ✅ 极速模式：2秒内完成审核操作
- ✅ 批量审核（用户明确说"全部通过"时）

## 🔧 环境要求

### 必需条件

| 要求 | 说明 | 检查命令 |
|------|------|----------|
| Python 3.6+ | 脚本运行环境 | `python3 --version` |
| 网络访问 | 能访问 op.haidianyun.com | `curl -sk https://op.haidianyun.com` |
| Hermes Agent | 技能加载框架 | `hermes --version` |

### 依赖说明

**无额外依赖** — 脚本仅使用 Python 标准库，无需安装任何第三方包。

**不需要浏览器** — 纯 API 调用，无需 Selenium、Puppeteer 或 Chromium。

### 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `HAIDIANYUN_USER_ACCOUNT` | 海典运营平台账号 | ✅ |
| `HAIDIANYUN_PASSWORD` | 海典运营平台密码 | ✅ |

## 🚀 快速开始

### 方式一：通过 Hermes Agent 安装（推荐）

```bash
hermes skills install haidianyun-customer-audit
```

### 方式二：手动安装

```bash
# 克隆到 Hermes 技能目录
git clone https://github.com/oldxianyu/haidianyun-customer-audit.git \
  ~/.hermes/skills/business/haidianyun-customer-audit

# 重启 Hermes Agent 使技能生效
hermes gateway restart
```

### 环境检查

安装后运行环境检查脚本：

```bash
python3 ~/.hermes/skills/business/haidianyun-customer-audit/scripts/check_environment.py
```

## ⚙️ 配置

### 1. 设置环境变量

在 `~/.hermes/.env` 文件中添加：

```bash
# 海典运营平台账号密码
HAIDIANYUN_USER_ACCOUNT=your_account
HAIDIANYUN_PASSWORD=your_p...## 2. 重启 Hermes Agent

```bash
hermes gateway restart
```

### 3. 验证配置

```bash
# 检查技能是否加载
hermes skills list | grep haidianyun

# 测试脚本
python3 ~/.hermes/skills/business/haidianyun-customer-audit/scripts/haidianyun_audit.py
```

## 📖 使用方法

### 在企业微信中使用

直接发送消息给 Hermes Agent：

| 消息示例 | 说明 |
|----------|------|
| `审核 21322` | 审核通过 ID 为 21322 的记录 |
| `审核 河北君临药业` | 审核通过名称包含"河北君临药业"的记录 |
| `审核这一条` + 截图 | 识别截图中的客户并审核通过 |
| `全部通过` | 批量审核所有待审核记录 |

### 命令行使用

```bash
# 审核指定 ID 的记录
python3 ~/.hermes/skills/business/haidianyun-customer-audit/scripts/haidianyun_audit.py 21322
```

## 🔌 API 接口文档

### 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://op.haidianyun.com/gateway/operation` |
| 协议 | HTTPS（需跳过证书验证） |
| 认证方式 | 登录获取 `accessToken`，放入请求 header |

### 接口列表

#### 1. 登录认证

```http
POST /auth/operation/auth
Content-Type: application/json

{
    "userAccount": "your_account",
    "password": "your_password"
}
```

**响应示例：**
```json
{
    "code": "00000",
    "data": {
        "accessToken": "xxx..."
    }
}
```

#### 2. 查询客户列表

```http
POST /orgmanager-v2/top/customerDraft/queryList
Content-Type: application/json
access-token: <token>

{
    "currentPage": 1,
    "pageSize": 20,
    "verifyStatus": 2,      // 2=待审核, 3=审核通过
    "customerName": "关键词"  // 可选，按名称搜索
}
```

#### 3. 查看客户详情

```http
POST /orgmanager-v2/top/customerDraft/draftDetail
Content-Type: application/json
access-token: <token>

{
    "id": 21322
}
```

**响应字段：**
- `customerName` - 客户名称
- `customerShortName` - 客户简称
- `socialCreditCode` - 社会信用代码
- `contacts` - 联系人
- `phone` - 电话
- `address` - 地址
- `areaCodes` - 地区编码 [省, 市, 区]
- `companyName` - 厂家名称（可能为空）
- `verifyStatus` - 审核状态

#### 4. 审核操作

```http
POST /orgmanager-v2/top/customerDraft/audit
Content-Type: application/json
access-token: <token>

{
    "id": 21322,
    "verifyStatus": 3,           // 3=审核通过
    "remark": "审核通过",
    "companyName": "xxx",        // 必填！从详情获取
    "customerName": "xxx",
    "customerShortName": "xxx",
    "socialCreditCode": "xxx",
    "contacts": "xxx",
    "phone": "xxx",
    "address": "xxx",
    "areaCodes": [省, 市, 区]
}
```

**响应码：**
- `00103` - 修改成功（操作成功）
- `00003` - 厂家名称不能为空（需补全 companyName）

## 📁 项目结构

```
haidianyun-customer-audit/
├── SKILL.md                    # Hermes Agent 技能文档
├── README.md                   # 本说明文档
├── .gitignore                  # Git 忽略规则
├── scripts/
│   ├── haidianyun_audit.py     # 快速审核脚本
│   └── check_environment.py    # 环境检查脚本
└── references/                 # 参考文档
    ├── api-details.md          # API 详细文档
    ├── wecom-websocket-stability.md  # WebSocket 稳定性说明
    └── ngrok-tunnel-setup.md   # Ngrok 隧道配置
```

## ⚠️ 重要规则

### 审核规则

1. **"审核" = "审核通过"** - 此系统不存在审核不通过的操作
2. **只操作指定记录** - 用户提到哪条就处理哪条，其他不动
3. **不要询问确认** - 用户说"审核这一条"就直接执行
4. **批量需明确** - 只有用户说"全部通过"才做批量操作

### 错误示例（避免）

❌ 用户说"将21321通过" → 通过21321 + 拒绝其他4条
✅ 正确做法：只通过21321，其他不动

❌ 用户说"审核这一条" → 先问"通过还是拒绝？"
✅ 正确做法：直接查询记录并审核通过

## 🔧 常见问题

### Q: 审核失败，提示"厂家名称不能为空"

**原因：** `companyName` 字段为空

**解决：** 脚本会自动从详情获取 `customerName` 填充，如果仍失败，检查记录是否完整。

### Q: 企业微信收不到回复

**原因：** WebSocket 在处理过程中断连

**解决：** 
1. 使用优化后的脚本（2秒内完成）
2. 简化消息格式（如"审核 21322"）
3. 检查日志：`tail -f ~/.hermes/logs/gateway.log`

### Q: 如何查看待审核列表？

**解决：** 发送消息"查看待审核列表"或"有哪些待审核"

## 🛠️ 开发调试

### 查看日志

```bash
# 实时查看 gateway 日志
tail -f ~/.hermes/logs/gateway.log

# 搜索审核相关日志
grep -i "审核\|audit" ~/.hermes/logs/gateway.log
```

### 测试 API 连通性

```bash
curl -sk https://op.haidianyun.com/gateway/operation/auth/operation/auth \
  -H "Content-Type: application/json" \
  -d '{"userAccount":"test","password":"test"}'
```

### 手动执行脚本

```bash
cd ~/.hermes/skills/business/haidianyun-customer-audit
python3 scripts/haidianyun_audit.py 21322
```

## 📄 更新日志

### v1.0.0 (2026-05-29)
- 初始版本
- 支持客户审核通过操作
- 支持按 ID 和名称审核
- 支持图片识别审核
- 极速模式优化（2秒内完成）
- 环境检查脚本

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [海典运营平台](https://op.haidianyun.com)
- [Hermes Agent 文档](https://hermes-agent.nousresearch.com/docs/)
