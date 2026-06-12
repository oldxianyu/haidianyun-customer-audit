---
name: oms-order-exp
description: 登录海典中台运营平台，全量导出商户套餐订购数据到 PostgreSQL 数据库。每月1号自动同步。用于查询套餐到期、服务状态、订购历史。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [business, hydee, postgresql, cron, export]
setup:
  env:
    - name: HYDE_MIDDLE_ACCOUNT
      prompt: "海典中台账号"
      required: true
    - name: HYDE_MIDDLE_PASSWORD
      prompt: "海典中台密码"
      required: true
      secret: true
    - name: PG_SOP_HOST
      prompt: "PostgreSQL主机地址"
      required: true
      default: localhost
    - name: PG_SOP_PORT
      prompt: "PostgreSQL端口"
      required: true
      default: "5432"
    - name: PG_SOP_DB
      prompt: "PostgreSQL数据库名"
      required: true
      default: sop_4chan
    - name: PG_SOP_USER
      prompt: "PostgreSQL用户名"
      required: true
    - name: PG_SOP_PASSWORD
      prompt: "PostgreSQL密码"
      required: true
      secret: true
---

# OMS 订单套餐数据导出

从海典中台运营平台 (middle.hydee.cn) 全量导出商户套餐订购数据到本地 PostgreSQL 数据库。

## 数据源

- **平台**: 海典中台运营平台 `https://middle.hydee.cn/operation/`
- **API**: `merchant/queryMerchantServiceList`
- **认证**: MD5 哈希密码登录，获取 token

## 目标数据库

- **数据库**: PostgreSQL (`sop_4chan`)
- **表名**: `hydee_orders`
- **同步策略**: 每月1号凌晨3:00 全量覆盖（TRUNCATE + INSERT）

## 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| 插入时间 | TIMESTAMP | 同步批次时间 |
| 商户名称 | VARCHAR(255) | 连锁名称 |
| 商户编码 | VARCHAR(64) | 商户唯一编码 |
| 所属事业部 | VARCHAR(64) | 华东/中南/北方/西南/西北/GM/KA |
| 订购套餐 | VARCHAR(255) | 套餐名称 |
| 订购时长 | INTEGER | 月数（API几乎全0） |
| 订购状态 | VARCHAR(32) | 开通/暂停/未知/已取消 |
| 过期时间 | VARCHAR(64) | 套餐到期时间 |
| 订购时间 | VARCHAR(64) | 订购开始时间 |
| 订购人 | VARCHAR(64) | （API几乎全空） |

## 查询示例

```sql
-- 华东事业部 30天内到期套餐
SELECT 商户名称, 商户编码, 订购套餐, 过期时间
FROM hydee_orders
WHERE 所属事业部 = '华东事业部'
  AND 订购状态 = '开通'
  AND 过期时间 <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY 过期时间;

-- 按事业部统计开通数
SELECT 所属事业部, COUNT(*) AS 开通数
FROM hydee_orders
WHERE 订购状态 = '开通'
GROUP BY 所属事业部
ORDER BY 开通数 DESC;

-- 某商户全部套餐
SELECT 订购套餐, 订购状态, 过期时间
FROM hydee_orders
WHERE 商户名称 LIKE '%关键字%'
ORDER BY 过期时间;
```

## 脚本

- **同步脚本**: `/root/scripts/sync_hydee_orders.py`
- **Cron Job**: ID `3a172f43756e`, 每月1号 03:00

## 手动同步

```bash
python3 /root/scripts/sync_hydee_orders.py
```

约耗时 50-60 秒，拉取 ~23,550 条记录。

## 注意事项

- API 的 `monthsNum`（订购时长）和 `createName`（订购人）字段几乎全为空/0，仅测试数据有值
- bedept 过滤在 API 中不稳定，脚本拉取全量数据，库里用中文事业部名称可精确过滤
- 同步脚本以 `TRUNCATE + INSERT` 方式全量覆盖，不保留历史版本
