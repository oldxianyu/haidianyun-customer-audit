---
name: haidianyun-customer-audit
description: 操作海典运营平台 op.haidianyun.com 客户审核系统（sjc-verify 页面），查询和通过客户信息草稿。注意：此系统只做审核通过操作，不存在审核不通过。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [business, audit, haidianyun, api]
    related_skills: []
---

# 海典运营平台客户审核系统

## 概述

通过 API 操作 `https://op.haidianyun.com` 的客户信息审核（sjc-verify）模块。

## API 基础信息

- Base URL: `https://op.haidianyun.com/gateway/operation`
- 登录接口: `/auth/operation/auth`
- 需要 SSL 证书跳过（自签名或特殊配置）

## 登录

使用环境变量配置账号密码：

```bash
# 在 ~/.hermes/.env 中添加
HAIDIANYUN_USER_ACCOUNT=your_account
HAIDIANYUN_PASSWORD=your_password
```

```python
import urllib.request, json, ssl, os
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = 'https://op.haidianyun.com/gateway/operation'
user_account = os.environ.get('HAIDIANYUN_USER_ACCOUNT')
password = os.environ.get('HAIDIANYUN_PASSWORD')

if not user_account or not password:
    raise ValueError("请配置环境变量 HAIDIANYUN_USER_ACCOUNT 和 HAIDIANYUN_PASSWORD")

req = urllib.request.Request(BASE + '/auth/operation/auth',
    data=json.dumps({'userAccount': user_account, 'password': password}).encode(),
    headers={'Content-Type':'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=5)
token = json.loads(resp.read())['data']['accessToken']
```

后续所有请求需带 header: `access-token: <token>`

## 核心接口

### 1. 查询列表

```
POST /orgmanager-v2/top/customerDraft/queryList
Body: {"currentPage":1, "pageSize":20, "verifyStatus":2}
```

verifyStatus: 2=待审核, 3=审核通过

可按 customerName 搜索：`{"currentPage":1, "pageSize":50, "customerName":"关键词"}`

### 2. 查看详情

```
POST /orgmanager-v2/top/customerDraft/draftDetail
Body: {"id": <record_id>}
```

返回完整字段：customerName, customerShortName, socialCreditCode, contacts, phone, address, areaCodes, companyName 等。

### 3. 审核操作

```
POST /orgmanager-v2/top/customerDraft/audit
```

通过（verifyStatus=3）：
```json
{
    "id": 21322,
    "verifyStatus": 3,
    "remark": "审核通过",
    "companyName": "xxx",       // 必填！从详情获取或用 customerName
    "customerName": "xxx",
    "customerShortName": "xxx",
    "socialCreditCode": "xxx",
    "contacts": "xxx",
    "phone": "xxx",
    "address": "xxx",
    "areaCodes": [省, 市, 区]
}
```

**注意：此系统只做审核通过，不存在审核不通过的操作。**

## 快速审核脚本

优化后的脚本路径: `scripts/haidianyun_audit.py`（相对于此技能目录）

系统路径: `/root/scripts/haidianyun_audit.py`

用法:
```bash
python3 /root/scripts/haidianyun_audit.py <record_id>
```

该脚本将 4 次 API 调用压缩为 3 次（登录→详情→审核），减少 WebSocket 断连风险。

## 操作流程

### 标准流程（用户给名称或 ID）

1. 登录获取 token
2. 按名称或 ID 查询记录
3. 调 draftDetail 获取完整信息（如需）
4. 审核通过时需补全 companyName（该字段可能为空，用 customerName 填充）
5. 提交审核结果

### 图片审核流程（用户发截图）

用户经常发送系统截图来说"审核这一条"。处理步骤：

1. 用 vision_analyze 分析图片，提取厂家名称、信用代码等关键信息
2. 登录 API，用 customerName 搜索匹配记录
3. 确认记录 ID 后直接审核通过（**不要问用户确认**）
4. 汇报结果

**注意：** 图片中的信息可能被遮挡（联系人、电话部分隐藏），以 API 查询结果为准。

## ⚠️ 铁律（必须遵守）—— 用户曾因此发火

**用户说"审核"时，意思就是"审核通过"。这个系统里不存在审核不通过的操作。**

**核心规则：**
1. "审核" = "审核通过"，永远不拒绝
2. **绝对不要问"通过还是拒绝"——直接执行审核通过**
3. 用户发图片说"审核这一条" → 分析图片 → 查找记录 → 直接审核通过，不要中途确认
4. 只操作用户明确提到的那一条记录，其他记录一律不动
5. 用户明确说"全部通过"才做批量通过
6. 不要自作主张处理其他记录
7. 违反此规则会严重损害用户信任

**错误示例（曾导致用户愤怒）：**
- 用户说"将21321通过" → 错误做法：通过21321 + 拒绝其他4条
- 正确做法：只通过21321，其他不动
- 用户说"审核这一条" → 错误做法：先问"通过还是拒绝？"
- 正确做法：直接查询记录并审核通过

## 常见错误

- `code=00003, msg=厂家名称不能为空` → 审核通过时 companyName 为空，需从详情获取并补全
- `code=00103, msg=修改成功` → 操作成功

## ⚠️ WeCom 响应超时问题

企业微信 WebSocket 每 ~90 秒断连重连。如果审核操作（查询+详情+提交）耗时过长，回复可能在发送时丢失。

**应对策略：**
- 尽量减少 API 调用次数（能一次查到的不要分两次）
- 如果需要查看详情再审核，可以在回复中先告知"正在处理"，然后快速完成操作
- 如果用户没收到回复，检查 `~/.hermes/logs/gateway.log` 确认是否发送失败
- 详见 `wecom-gateway-tuning` 技能

## 输出格式

审核完成后汇报：
- 处理了哪些 ID
- 每条的操作结果（通过）
- 如有失败，说明原因

## 参考文件

- `references/api-details.md` — API 详细文档、响应码、已知坑
- `references/wecom-message-loss.md` — 企业微信消息丢失问题与解决方案
- `references/ngrok-tunnel-setup.md` — Ngrok 隧道配置（备用方案，需管理后台权限）
