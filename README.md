# 海典运营平台客户审核系统

Hermes Agent 技能：自动审核海典运营平台 (op.haidianyun.com) 的客户信息草稿。

## 功能

- 查询待审核客户列表
- 自动审核通过指定客户
- 支持按 ID 或名称审核
- 极速模式：2秒内完成审核

## 安装

### 方式一：通过 Hermes Agent 安装

```bash
hermes skills install haidianyun-customer-audit
```

### 方式二：手动安装

1. 克隆此仓库到 `~/.hermes/skills/business/` 目录：

```bash
git clone https://github.com/oldxianyu/haidianyun-customer-audit.git ~/.hermes/skills/business/haidianyun-customer-audit
```

2. 配置环境变量：

```bash
# 在 ~/.hermes/.env 中添加
HAIDIANYUN_USER_ACCOUNT=your_account
HAIDIANYUN_PASSWORD=your_password
```

3. 重启 Hermes Agent

## 使用方法

### 在企业微信中使用

直接发送消息：
- `审核 21322` — 审核通过 ID 为 21322 的记录
- `审核 河北君临药业` — 审核通过名称包含"河北君临药业"的记录

### 命令行使用

```bash
python3 ~/.hermes/skills/business/haidianyun-customer-audit/scripts/haidianyun_audit.py <record_id>
```

## 注意事项

⚠️ **重要规则**：
- "审核" = "审核通过"，此系统不存在审核不通过的操作
- 只操作用户明确提到的记录，其他记录不动
- 批量操作需要用户明确说"全部通过"

## API 接口

| 接口 | 路径 | 说明 |
|------|------|------|
| 登录 | `/auth/operation/auth` | 获取 accessToken |
| 查询列表 | `/orgmanager-v2/top/customerDraft/queryList` | 查询客户草稿列表 |
| 查看详情 | `/orgmanager-v2/top/customerDraft/draftDetail` | 获取客户详情 |
| 审核操作 | `/orgmanager-v2/top/customerDraft/audit` | 提交审核结果 |

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `HAIDIANYUN_USER_ACCOUNT` | 海典运营平台账号 | ✅ |
| `HAIDIANYUN_PASSWORD` | 海典运营平台密码 | ✅ |

## License

MIT
