# 安装和快速开始指南

## 前置条件

- Python 3.8+ (已测试：3.13.2)
- pip 包管理器
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

## 分步安装指南

### 1. 创建虚拟环境

```bash
cd /Users/zch/work/agent-webapp
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装 Python 依赖

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**关键依赖版本**:
- Flask 3.1.2 (Web 框架)
- PyTorch 2.10.0 (深度学习)
- OpenCLIP 3.2.0 (CLIP 模型)
- FAISS 1.13.2 (向量搜索)
- NumPy 2.4.1 (数值计算)
- Pillow 12.1.0 (图像处理)

### 3. 准备图片数据集

```bash
# 图片应该已在 images/ 目录中
ls images/  # 验证图片存在
```

### 4. 生成 FAISS 索引（重要！）

这一步是必需的，用于生成向量索引。

```bash
source venv/bin/activate
python get_embeddings.py
```

这将:
- 扫描 `images/` 文件夹中的所有图片
- 生成 512 维 CLIP 嵌入向量
- 保存到 `image_embeddings.pkl`

预期输出:
```
🔧 加载CLIP模型: ViT-B-32
📱 使用设备: mps
📂 扫描图片文件夹: ./images
✅ 找到 9 张图片
...
✅ 成功为 9 张图片生成embeddings
```

### 5. 构建 FAISS 索引

```bash
python build_faiss_index.py
```

这将:
- 从 embeddings 构建 FAISS 索引
- 创建向量索引文件 (`data/faiss_index/index.faiss`)
- 保存元数据 (`data/faiss_index/metadata.json`)

预期输出:
```
✅ FAISS索引创建成功！
📊 索引统计:
  status: initialized
  total_vectors: 9
  dimension: 512
  ...
```

### 6. 启动 Flask Web 应用

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

> **重要**: 必须设置 `KMP_DUPLICATE_LIB_OK=TRUE` 环境变量，以避免 PyTorch 的 OpenMP 库冲突导致应用崩溃。

预期输出:
```
2026-01-29 14:44:54 - __main__ - INFO - ML components initialized successfully
2026-01-29 14:44:54 - __main__ - INFO - Starting Flask app on http://localhost:5001
 * Running on http://127.0.0.1:5001
```

### 7. 在浏览器中打开

访问以下任一地址:
```
http://localhost:5001          # 本地访问
http://127.0.0.1:5001        # 本地回环
http://192.168.0.108:5001    # 局域网访问
```

## 验证清单

- [ ] 虚拟环境已创建和激活
- [ ] 所有依赖安装成功（pip list 检查）
- [ ] images/ 目录包含图片
- [ ] get_embeddings.py 成功运行
- [ ] build_faiss_index.py 成功运行
- [ ] Flask 应用成功启动
- [ ] 浏览器加载搜索页面
- [ ] 文本搜索返回结果
- [ ] 图片上传功能正常
- [ ] 反馈按钮有效

## 快速测试

应用启动后，尝试这些功能:

1. **文本搜索**: 输入 "a dog" 或 "一只狗"
2. **图片搜索**: 上传 `images/` 中的任何图片
3. **多模态搜索**: 输入文本 + 上传图片
4. **多图片搜索**: 上传 2-3 张图片
5. **语音搜索**: 点击麦克风按钮并说话

## 故障排除

### 问题：FAISS 索引未找到
```
FileNotFoundError: Index file not found
```
**解决方案**: 运行 `python build_faiss_index.py`

### 问题：模型加载失败
```
Error: Cannot load model
```
**解决方案**: 确保 `models/ViT-B-32-laion2B-s34B-b79K/` 目录存在

### 问题：CLIP 模型下载超时
```
SSL timeout / Connection reset
```
**解决方案**: 应用已配置使用本地模型文件，无需网络

### 问题：OpenMP 库冲突错误
```
OMP: Error #15: Initializing libomp.dylib, but found libomp.dylib already initialized.
```
**解决方案**: 设置环境变量
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
```
或者使用启动脚本（已包含此设置）:
```bash
./start.sh
```

### 问题：端口 5001 被占用
```
Address already in use
```
**解决方案**:
```bash
# 杀死现有进程
pkill -f "python app_web.py"

# 或使用其他端口（在 app_web.py 中修改）
```

### 问题：MPS 设备不可用
```
Device: cpu
```
**正常情况**: 应用将回退到 CPU（较慢但可用）
- Apple Silicon: 自动使用 MPS（已优化）
- NVIDIA GPU: 自动使用 CUDA
- 否则: 使用 CPU

### 问题：虚拟环境激活问题
```bash
# 如果 source 命令不工作，尝试：
. venv/bin/activate     # 简写
bash venv/bin/activate  # 显式使用 bash
```

## 系统要求

### 磁盘空间
- CLIP 模型: ~600 MB
- 虚拟环境: ~2 GB
- FAISS 索引（9 张图片）: ~20 KB
- **最小总需求**: ~3 GB

### 内存
- 最小: 4 GB RAM
- 推荐: 8 GB RAM
- 模型加载: ~1-2 GB

### 处理器
- MacBook M1/M2+ (MPS 加速): 最佳
- Intel CPU with CUDA: 很好
- 纯 CPU: 可行（较慢）

## 开发模式

运行带调试日志的应用:

```bash
export DEBUG=True
python app_web.py
```

这将启用:
- 自动代码重加载
- 详细错误消息
- Flask 调试工具栏

## 生产部署

对于生产环境，建议:

1. 使用 WSGI 服务器（gunicorn, uWSGI）
2. 设置 `DEBUG=False`
3. 配置反向代理（nginx）
4. 使用 HTTPS
5. 设置环境变量安全密钥

示例 gunicorn 启动:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app_web:app
```

## 文件位置

设置完成后，你应该拥有:

```
agent-webapp/
├── venv/                          # Python 虚拟环境
├── data/
│   ├── faiss_index/
│   │   ├── index.faiss           # FAISS 索引
│   │   └── metadata.json         # 元数据
│   ├── feedback.db               # SQLite 反馈数据库
│   └── images/                   # 原始图片
├── models/
│   └── ViT-B-32-laion2B-s34B-b79K/  # CLIP 模型
├── image_embeddings.pkl          # 图片嵌入向量
└── app_web.py                    # Flask 应用（主程序）
```

## 支持

如有问题:
1. 检查故障排除部分
2. 验证所有依赖已安装 (`pip list`)
3. 查看应用日志获取错误信息
4. 参考 README_WEB.md 详细文档

---

**准备好了吗?** 运行 `python app_web.py` 并访问 http://localhost:5001 🚀
