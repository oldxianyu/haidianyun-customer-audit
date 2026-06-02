# 企业微信消息丢失问题与解决方案

## 问题现象

审核操作通过 API 完成，但用户在企业微信收不到回复。

日志显示:
```
[Wecom] Send failed: WeCom connection interrupted
[Wecom] Send failed: WeCom websocket is not connected
```

## 根因

企业微信 WebSocket 服务端 ~90 秒强制断连。如果审核操作耗时超过 90 秒（登录→查询→详情→审核），WebSocket 在发送回复时已断开。

## 解决方案

### 方案 1: 优化操作速度（已实施）

使用快速脚本 `/root/scripts/haidianyun_audit.py <record_id>`，将 4 次 API 调用压缩为 3 次。

### 方案 2: 切换到回调模式（推荐）

用 HTTP webhook 代替 WebSocket，不依赖持久连接。

配置详见: `wecom-gateway-tuning` 技能的 `references/wecom-callback-setup.md`

前置条件:
- 公网可访问的 URL（路由器端口转发或 ngrok 隧道）
- 企业微信自建应用

### 方案 3: 重发机制（临时）

如果消息丢失，可以手动触发重发:
```bash
hermes gateway restart
```
重启后 gateway 会重新连接 WebSocket，但已丢失的消息不会自动重发。

## 监控

检查消息发送状态:
```bash
tail -50 ~/.hermes/logs/gateway.log | grep -i "send failed\|connection interrupted"
```
