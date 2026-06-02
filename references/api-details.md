# 海淀云客户审核 API 详细文档

## 基础信息

- Base URL: `https://op.haidianyun.com/gateway/operation`
- SSL: 需跳过证书验证（自签名或特殊配置）
- 认证: Header `access-token: <token>`

## 登录

```
POST /auth/operation/auth
Body: {"userAccount":"3593","password":"DAPVWKPf"}
Response: {"data":{"accessToken":"..."}}
```

Token 有效期未知，建议每次操作重新获取。

## 查询列表

```
POST /orgmanager-v2/top/customerDraft/queryList
Body: {"currentPage":1, "pageSize":20, "verifyStatus":2}
```

verifyStatus 枚举:
- 1 = 审核不通过
- 2 = 待审核
- 3 = 审核通过
- 4 = 已撤回

支持按名称搜索: `{"customerName":"关键词"}`

## 查看详情

```
POST /orgmanager-v2/top/customerDraft/draftDetail
Body: {"id": <record_id>}
```

返回完整字段，关键字段:
- customerName, customerShortName
- socialCreditCode (统一社会信用代码)
- contacts, phone, address
- areaCodes: [省, 市, 区] 三级行政区划代码
- companyName (可能为空!)
- verifyStatus

## 审核操作

```
POST /orgmanager-v2/top/customerDraft/audit
```

### 通过 (verifyStatus=3)

**必须填充 companyName**，否则返回 `code=00003, msg=厂家名称不能为空`。

```json
{
    "id": 21322,
    "verifyStatus": 3,
    "remark": "审核通过",
    "companyName": "从详情获取或用customerName",
    "customerName": "xxx",
    "customerShortName": "xxx",
    "socialCreditCode": "xxx",
    "contacts": "xxx",
    "phone": "xxx",
    "address": "xxx",
    "areaCodes": [省, 市, 区]
}
```

### 拒绝 (verifyStatus=1)

```json
{"id": <id>, "verifyStatus": 1, "remark": "审核不通过"}
```

## 响应码

- `code=00103, msg=修改成功` → 操作成功
- `code=00003, msg=厂家名称不能为空` → companyName 缺失

## 性能优化

原流程 4 次 API 调用: 登录→查询→详情→审核
优化后 3 次: 登录→详情→审核（跳过查询，直接用 ID）

快速脚本: `/root/scripts/haidianyun_audit.py <record_id>`

## 已知坑

1. companyName 可能为空，审核通过时必须补全
2. 用 customerName 填充 companyName 即可
3. areaCodes 必须是数组格式 [省, 市, 区]
