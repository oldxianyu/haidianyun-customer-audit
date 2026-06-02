# GitHub 上传技能流程

## 前置条件

1. GitHub 账号
2. Personal Access Token (PAT) — 需要 `repo` 权限
3. Git 已配置用户名和邮箱

## 步骤

### 1. 配置 Git

```bash
git config --global user.name "your_username"
git config --global user.email "your_email@example.com"
```

### 2. 创建 GitHub 仓库

```bash
curl -s -u "username:token" https://api.github.com/user/repos \
  -d '{"name":"repo-name","description":"Description","auto_init":true}'
```

### 3. 克隆仓库

```bash
git clone https://token@github.com/username/repo-name.git
cd repo-name
```

### 4. 复制技能文件

```bash
cp ~/.hermes/skills/business/skill-name/SKILL.md .
cp ~/.hermes/skills/business/skill-name/scripts/*.py scripts/
```

### 5. 创建 README.md

详细说明文档，包含：
- 功能特性
- 环境要求
- 安装方法
- 使用方法
- API 文档
- 常见问题

### 6. 提交并推送

```bash
git add .
git commit -m "feat: 初始版本"
git push origin main
```

### 7. 更新文件

如果需要更新已存在的文件：

```bash
git pull origin main
# 修改文件
git add .
git commit -m "docs: 更新说明文档"
git push origin main
```

## 注意事项

- **Token 安全**：不要在代码中硬编码 token，使用环境变量或 git credential
- **README 详细**：用户通过 README 了解技能，写得越详细越好
- **环境检查脚本**：提供 `check_environment.py` 帮助用户验证配置
- **去除敏感信息**：上传前确保去除硬编码的账号密码

## 本次上传的仓库

- 仓库地址：https://github.com/oldxianyu/haidianyun-customer-audit
- 包含文件：
  - SKILL.md (技能文档)
  - README.md (详细说明)
  - .gitignore
  - scripts/haidianyun_audit.py (审核脚本)
  - scripts/check_environment.py (环境检查脚本)
