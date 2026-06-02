# WeCom WebSocket 稳定性问题

## 现象

企业微信 WebSocket 长连接每 ~90 秒断连重连一次。日志表现：
```
[Wecom] Reconnected
[Wecom] WebSocket error: WeCom websocket closed
```

## 影响

当消息处理时间超过 90 秒时，回复可能在发送时丢失：
1. 用户发送消息
2. Agent 开始处理（LLM + API 调用，耗时 30-40 秒）
3. WebSocket 断连
4. Agent 完成处理，尝试发送回复
5. 发送失败：`WeCom connection interrupted`
6. WebSocket 重连，但回复已丢失

## 解决方案

### 1. 优化处理速度（推荐）

将审核操作压缩到 2-3 秒内完成：
- 减少 API 调用次数（登录→详情→审核，共 3 次）
- 使用优化后的脚本 `scripts/haidianyun_audit.py`

### 2. 切换到回调模式（需要管理后台权限）

回调模式使用 HTTP webhook，不依赖持久连接：
- 需要在企业微信管理后台创建自建应用
- 需要公网可访问的 URL（或 ngrok 隧道）
- 需要配置 Corp ID、Corp Secret、Agent ID、Token、EncodingAESKey

### 3. 使用 ngrok 隧道（如果需要回调模式）

```bash
# 安装 ngrok
curl -sSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz -C /usr/local/bin/

# 配置 auth token
ngrok config add-authtoken <your_token>

# 启动隧道
ngrok http 8645
```

公网 URL 格式：`https://xxx.ngrok-free.dev`
回调地址：`https://xxx.ngrok-free.dev/wecom/callback`

## 网络环境注意

当前机器在内网（192.168.0.100 / 192.168.1.200），公网 IP 122.4.19.46 是路由器的。端口需要路由器转发才能从外部访问。

## 日志检查

检查 WebSocket 状态：
```bash
tail -50 ~/.hermes/logs/gateway.log | grep -i "wecom\|websocket\|reconnect"
```

检查回复是否发送成功：
```bash
grep "Send failed\|response ready" ~/.hermes/logs/gateway.log | tail -10
```
