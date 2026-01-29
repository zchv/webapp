# CLIP 语义图像搜索应用

## 🎯 当前版本：Flask Web 应用

本项目是一个基于 **Flask** 的现代 Web 应用，用于语义图像搜索。支持文本、图像、语音、多模态等多种搜索方式。

> **原 Streamlit 版本已弃用** - 请使用 Flask Web 版本以获得更好的功能和性能。

## 🚀 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 生成索引

```bash
python get_embeddings.py
python build_faiss_index.py
```

### 4. 启动应用

**推荐方式（使用启动脚本）:**
```bash
./start.sh
```

**手动启动:**
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
source venv/bin/activate
python app_web.py
```

> **注意**: 必须设置 `KMP_DUPLICATE_LIB_OK=TRUE` 环境变量，以避免 PyTorch 的 OpenMP 库冲突问题。

### 5. 访问应用

打开浏览器访问: http://localhost:5001

## 📖 详细文档

- **[安装指南](INSTALLATION.md)** - 完整的安装步骤
- **[Flask Web 文档](README_WEB.md)** - 功能和 API 说明
- **[优化指南](OPTIMIZATION_GUIDE.md)** - 性能优化建议

## ✨ 主要功能

### 🔍 5 种搜索模式
- **文本搜索** - 自然语言查询
- **语音搜索** - Web Speech API
- **图像搜索** - 以图搜图
- **多模态搜索** - 文本 + 图像融合
- **多图片搜索** - 多张图片向量融合

### 🎨 现代 Web UI
- 响应式设计（桌面/平板/手机）
- 实时搜索结果
- 拖拽上传支持
- 分页/无限滚动

### 👥 用户反馈系统
- 点赞、收藏、标记功能
- SQLite 数据库持久化
- 反馈基础重排序
- 统计分析

## 📊 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| Web 框架 | Flask | 3.1.2 |
| 深度学习 | PyTorch | 2.10.0 |
| CLIP 模型 | OpenCLIP | 3.2.0 |
| 向量搜索 | FAISS | 1.13.2 |
| 图像处理 | Pillow | 12.1.0 |
| 前端 | Vanilla JS (ES6+) | - |
| 样式 | CSS3 (Grid/Flexbox) | - |

## 📁 项目结构

```
agent-webapp/
├── venv/                    # Python 虚拟环境
├── app_web.py              # Flask 应用（主程序）
├── config.py               # 配置文件
├── requirements.txt        # 依赖列表
│
├── api/                    # API 层
│   ├── search.py          # 搜索端点
│   └── utils.py           # 工具函数
│
├── core/                   # ML 核心
│   ├── clip_model.py      # CLIP 模型包装
│   ├── faiss_index.py     # FAISS 索引管理
│   └── feedback.py        # 反馈数据库
│
├── utils/                  # 工具模块
│   ├── image_processor.py # 图像处理
│   └── query_enhancer.py  # 查询增强
│
├── templates/             # HTML 模板
│   ├── base.html
│   ├── index.html
│   ├── settings.html
│   └── stats.html
│
├── static/                # 前端资源
│   ├── css/              # 7 个样式表
│   ├── js/               # 10 个脚本文件
│   └── uploads/          # 用户上传
│
├── data/                  # 数据文件
│   ├── faiss_index/      # FAISS 索引
│   ├── feedback.db       # SQLite 反馈数据
│   └── images/           # 原始图片
│
├── models/               # CLIP 模型
│   └── ViT-B-32-laion2B-s34B-b79K/
│
└── docs/                 # 文档
    ├── INSTALLATION.md
    ├── README_WEB.md
    └── OPTIMIZATION_GUIDE.md
```

## 🔧 API 端点

### 搜索接口
- `POST /api/search/text` - 文本搜索
- `POST /api/search/image` - 图像搜索
- `POST /api/search/voice` - 语音搜索
- `POST /api/search/multimodal` - 多模态搜索
- `POST /api/search/multi-image` - 多图片搜索
- `GET /api/search/stats` - 搜索统计

### 反馈接口
- `POST /api/search/feedback/record` - 记录反馈
- `GET /api/search/feedback/stats/<id>` - 获取反馈统计
- `GET /api/search/feedback/top-rated` - 高评分图片

### 工具接口
- `GET /api/health` - 健康检查
- `GET /api/examples` - 示例查询

## 🎯 系统要求

### 最小配置
- **CPU**: 双核 2GHz
- **内存**: 4 GB
- **磁盘**: 3 GB (包括模型)

### 推荐配置
- **CPU**: Apple Silicon (M1+) 或 Intel i7+
- **内存**: 8 GB+
- **磁盘**: 5 GB+
- **GPU**: NVIDIA CUDA 或 Apple MPS

## 📝 常见问题

### Q: 如何添加更多图片？
A: 将图片放入 `images/` 目录，然后运行：
```bash
python get_embeddings.py
python build_faiss_index.py
```

### Q: 支持哪些图片格式？
A: PNG, JPG, JPEG, GIF, BMP, WEBP

### Q: 语音搜索在 Firefox 中不工作？
A: Firefox 不支持 Web Speech API，请使用 Chrome/Edge/Safari

### Q: 如何在生产环境部署？
A: 参考 [INSTALLATION.md](INSTALLATION.md) 中的生产部署章节

### Q: 可以离线使用吗？
A: 是的，所有模型都本地存储，可以完全离线使用

## 🔒 安全说明

- 所有处理在本地进行，无数据上传到云服务
- 反馈数据存储在本地 SQLite 数据库
- 建议生产环境使用 HTTPS

## 📄 许可证

- OpenAI CLIP - MIT License
- Flask - BSD License
- PyTorch - BSD License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

遇到问题？
1. 查看 [INSTALLATION.md](INSTALLATION.md) 的故障排除部分
2. 检查 [README_WEB.md](README_WEB.md) 的详细文档
3. 查看应用日志获取错误信息

---

**准备好了吗？** 参考 [快速开始](#-快速开始) 立即开始使用！🚀

**上次更新**: 2026-01-29
**Python 版本**: 3.13.2
**Flask 版本**: 3.1.2
