# Ngrok 隧道配置

## 用途

当需要配置企业微信回调模式但没有公网 IP 时，使用 ngrok 创建隧道。

## 安装

```bash
curl -sSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz -C /usr/local/bin/
```

## 配置

1. 注册 ngrok 账号：https://dashboard.ngrok.com/signup
2. 获取 authtoken：https://dashboard.ngrok.com/get-started/your-authtoken
3. 配置 token：
```bash
ngrok config add-authtoken <your_token>
```

## 使用

```bash
# 启动 HTTP 隧道
ngrok http 8645

# 查看隧道状态
curl -s http://127.0.0.1:4040/api/tunnels
```

公网 URL 格式：`https://xxx.ngrok-free.dev`

## 企业微信回调配置

回调地址：`https://xxx.ngrok-free.dev/wecom/callback`

需要在企业微信管理后台配置：
- URL: 回调地址
- Token: 验证 Token
- EncodingAESKey: 加密密钥

## 注意事项

- ngrok 免费版 URL 每次重启会变
- 需要保持 ngrok 进程运行
- 建议使用 systemd 服务管理 ngrok

## 环境要求

- 需要公网可访问的服务器或 ngrok 隧道
- 企业微信管理后台权限（配置回调 URL）
