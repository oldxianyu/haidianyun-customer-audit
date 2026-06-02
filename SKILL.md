---
name: haidianyun-customer-audit
description: 操作海典运营平台 op.haidianyun.com 客户审核系统（sjc-verify 页面），查询并审核通过厂家/客户信息草稿。用户说“审核厂家”“审核这一条”、发截图要求审核、给厂家名或记录 ID 时使用。
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [business, audit, haidianyun, api, wecom, low-token]
setup:
  env:
    - name: HAIDIANYUN_ACCOUNT
      prompt: "请输入海典云账号"
      required: true
    - name: HAIDIANYUN_PASSWORD
      prompt: "请输入海典云密码"
      required: true
      secret: true
---

# 海典云厂家审核（低 token 快路径）

目标：审核任务尽量 1 次模型决策 + 1 次脚本执行完成，避免反复加载长上下文。

## 必须遵守

- “审核”=“审核通过”。不要问“通过还是拒绝”。
- 只处理用户明确提到的那一条/那些记录；不要顺手处理其他记录。
- 用户明确说“全部通过”时才批量通过。
- 系统名称是“海典云”，域名 `op.haidianyun.com`。
- 企业微信场景要短回复：只报 ID、名称、成功/失败。

## 优先执行路径

### 文字或 ID 审核

不要手写 API 流程，直接调用脚本：

```bash
python3 /root/scripts/haidianyun_audit.py <记录ID或厂家名称> --json
```

多个明确目标：

```bash
python3 /root/scripts/haidianyun_audit.py <目标1> <目标2> --json
```

只有用户明确“全部通过”时才允许：

```bash
python3 /root/scripts/haidianyun_audit.py <厂家名> --all --json
```

列出待审核（仅排查时）：

```bash
python3 /root/scripts/haidianyun_audit.py --list
```

- 脚本能力：登录 → 名称搜索/ID 定位 → 详情补全 → 审核通过。环境变量兼容 `HAIDIANYUN_ACCOUNT`、`HAIDIANYUNUSERACCOUNT`、`HAIDIANYUN_USER_ACCOUNT` 和 `HAIDIANYUN_PASSWORD`。
- 注意：列表里的“提交商户编码/客户编码”（如截图中的 548838）不是草稿记录 ID，不能直接拿去 `draftDetail`。真正草稿 ID 是列表接口返回字段 `id`（例如 21446）。如果截图只显示提交商户编码，必须先按客户名称查列表拿 `id` 再审核。

### 图片审核

1. 如果收到图片/截图，先用视觉只提取厂家名或记录 ID。不要把整套 API 文档带进推理。
2. 图片只有一条记录：直接执行脚本审核，不确认。
3. 图片多条记录：除非用户说“全部通过”，否则让用户指定；不要批量自作主张。
4. WeCom 附件可能是 `.bin`，可先 `file <path>` 判断，真实 PNG/JPEG 可直接给视觉识别。

当前推荐命令仍是识别出名称/ID 后调用：

```bash
python3 /root/scripts/haidianyun_audit.py '<识别出的厂家名或ID>' --json
```

## 账号密码

必须放在 `~/.hermes/.env`，避免审核时反复询问：

```bash
HAIDIANYUN_ACCOUNT=3593
HAIDIANYUN_USER_ACCOUNT=3593
HAIDIANYUN_PASSWORD=你的密码
```

不要把密码写入 skill 或 memory。

## API 速查（仅脚本维护时用）

- Base: `https://op.haidianyun.com/gateway/operation`
- 登录: `POST /auth/operation/auth`，返回 `data.accessToken`
- 列表: `POST /orgmanager-v2/top/customerDraft/queryList`，`verifyStatus=2` 表示待审核
- 详情: `POST /orgmanager-v2/top/customerDraft/draftDetail`，body `{"id": 记录ID}`
- 审核: `POST /orgmanager-v2/top/customerDraft/audit`，`verifyStatus=3`、`remark=审核通过`
- 审核 payload 必须带详情里的 `companyName/customerName/socialCreditCode/contacts/phone/address/areaCodes`；`companyName` 为空时用 `customerName`。
- SSL 需跳过证书校验；脚本已处理。

## 常见错误

- `厂家名称不能为空`：审核 payload 缺 `companyName`，用详情的 `customerName` 补。
- `修改成功` 或 code `00103`：成功。
- 名称匹配多条：让用户指定 ID；只有“全部通过”才用 `--all`。
- 企业微信 90 秒重连属正常；减少模型轮次，不要长解释。

## 低成本/低延迟要求

- 审核时优先脚本，不重复展开 API 细节。
- 不需要加载浏览器/GitHub/设计/社交等工具。
- 企业微信长会话里审核成本高时，建议用户 `/reset` 后再发审核请求。
- 普通文字审核应控制为：加载 skill → 执行脚本 → 简短回复。

## 输出格式

成功：

```text
已通过：ID=21322，厂家名
```

失败：

```text
未通过：ID/厂家名，原因：xxx
```

## 文件

- 系统脚本：`/root/scripts/haidianyun_audit.py`
- skill 内置脚本：`scripts/haidianyun_audit.py`
- API 细节参考：`references/api-details.md`
- WeCom 稳定性：`references/wecom-websocket-stability.md`
- 企业微信低 token 审核工作流：`references/low-token-wecom-audit.md`
