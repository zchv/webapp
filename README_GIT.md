# Git 使用说明

## 📦 仓库信息

**项目名称**: CLIP Semantic Image Search
**分支**: main
**初始提交**: ✅ 已完成

## 🚀 快速开始

### 克隆仓库
```bash
git clone <repository-url>
cd agent-webapp
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 下载模型
模型文件较大（577MB），不包含在Git仓库中。

**方法1: 从HuggingFace镜像下载**
```bash
# 创建模型目录
mkdir -p models/ViT-B-32-laion2B-s34B-b79K

# 下载模型文件
wget https://hf-mirror.com/laion/CLIP-ViT-B-32-laion2B-s34B-b79K/resolve/main/open_clip_pytorch_model.bin \
  -O models/ViT-B-32-laion2B-s34B-b79K/open_clip_pytorch_model.bin

wget https://hf-mirror.com/laion/CLIP-ViT-B-32-laion2B-s34B-b79K/resolve/main/open_clip_config.json \
  -O models/ViT-B-32-laion2B-s34B-b79K/open_clip_config.json
```

**方法2: 使用Python脚本下载**
```python
# 创建 download_model.py
import requests
import os

MODEL_DIR = "./models/ViT-B-32-laion2B-s34B-b79K"
os.makedirs(MODEL_DIR, exist_ok=True)

# 下载模型文件
# ... (参考项目中的下载脚本)
```

## 📁 .gitignore 说明

以下文件/文件夹已被忽略：

### 大文件
- `models/` - 模型文件（577MB+）
- `*.bin`, `*.safetensors` - 模型权重文件
- `*.pkl` - Embeddings缓存文件

### 数据文件
- `image_embeddings.pkl` - 预计算的图片向量
- `images/` - 图片文件夹（可选）

### 开发环境
- `venv/`, `env/` - 虚拟环境
- `__pycache__/` - Python缓存
- `.vscode/`, `.idea/` - IDE配置

## 🔄 常用Git命令

### 查看状态
```bash
git status
```

### 添加文件
```bash
# 添加所有修改
git add .

# 添加特定文件
git add app.py
```

### 提交更改
```bash
git commit -m "描述你的更改"
```

### 推送到远程
```bash
# 首次推送
git push -u origin main

# 后续推送
git push
```

### 拉取更新
```bash
git pull
```

### 查看提交历史
```bash
git log --oneline
```

### 创建分支
```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 切换回主分支
git checkout main
```

## 📝 提交规范

建议使用以下提交信息格式：

```
<type>: <subject>

<body>

<footer>
```

**Type类型：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```bash
git commit -m "feat: add multi-query ensemble search

- Implement query ensemble for better accuracy
- Add configuration option in sidebar
- Update documentation

Closes #123"
```

## 🌿 分支策略

### 主分支
- `main` - 稳定版本，可直接部署

### 开发分支
- `develop` - 开发分支
- `feature/*` - 功能分支
- `fix/*` - 修复分支
- `docs/*` - 文档分支

### 工作流程
```bash
# 1. 从main创建功能分支
git checkout -b feature/new-search-algorithm

# 2. 开发并提交
git add .
git commit -m "feat: implement new search algorithm"

# 3. 推送到远程
git push -u origin feature/new-search-algorithm

# 4. 创建Pull Request
# 在GitHub/GitLab上创建PR

# 5. 合并后删除分支
git checkout main
git pull
git branch -d feature/new-search-algorithm
```

## 🔐 敏感信息处理

### 不要提交的内容
- ❌ API密钥
- ❌ 密码
- ❌ 私钥
- ❌ 个人数据
- ❌ 大型模型文件

### 使用环境变量
```bash
# 创建 .env 文件（已在.gitignore中）
echo "API_KEY=your_key_here" > .env

# 在代码中使用
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
```

## 📦 发布版本

### 创建标签
```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0

# 推送所有标签
git push --tags
```

### 版本号规范（Semantic Versioning）
```
v主版本.次版本.修订号

例如：
v1.0.0 - 初始发布
v1.1.0 - 添加新功能
v1.1.1 - 修复bug
v2.0.0 - 重大更新（不兼容旧版本）
```

## 🔧 Git配置

### 设置用户信息
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 设置默认编辑器
```bash
git config --global core.editor "vim"
```

### 设置别名
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"
```

## 🚨 常见问题

### 问题1：误提交了大文件
```bash
# 从Git历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch models/large_model.bin" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

### 问题2：撤销最后一次提交
```bash
# 保留更改
git reset --soft HEAD~1

# 丢弃更改
git reset --hard HEAD~1
```

### 问题3：合并冲突
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add <resolved-file>
git commit -m "resolve merge conflict"
```

## 📚 参考资源

- [Git官方文档](https://git-scm.com/doc)
- [GitHub指南](https://guides.github.com/)
- [Git教程](https://www.atlassian.com/git/tutorials)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目使用的组件：
- OpenAI CLIP (MIT License)
- Streamlit (Apache 2.0)
- PyTorch (BSD License)

---

**Happy Coding!** 🚀
