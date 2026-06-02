# 技能打包发布到 GitHub

## 流程

1. **创建发布目录** — 从原技能目录复制，排除敏感文件
2. **脱敏处理** — 硬编码密码改为环境变量
3. **添加 setup.env** — 让安装时自动提示填写配置
4. **打包** — tar.gz 或直接 git init

## 关键改动

### SKILL.md frontmatter 添加 setup.env

```yaml
setup:
  env:
    - name: ENV_VAR_NAME
      prompt: "提示用户输入的内容"
      required: true
    - name: SECRET_VAR
      prompt: "请输入密码"
      required: true
      secret: true  # 掩码输入
```

效果：用户安装技能后首次使用时，Hermes 自动提示输入，保存到 `~/.hermes/.env`。

### 脚本脱敏

```python
# 之前
password = 'hardcoded_password'

# 之后
password = os.environ.get('ENV_VAR_NAME', '')
if not password:
    print("错误: 请设置环境变量 ENV_VAR_NAME")
    sys.exit(1)
```

## 发布结构

```
skill-name/
├── SKILL.md          # 技能主文件（含 setup.env 配置）
├── README.md         # 使用说明
├── references/       # 参考文档
│   └── api-details.md
└── scripts/          # 脚本
    └── main.py
```

## 用户安装方式

```bash
# 方式一：hermes CLI
hermes skill install github.com/user/repo

# 方式二：手动
git clone https://github.com/user/repo.git ~/.hermes/skills/category/skill-name
```
