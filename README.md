# CLIP 语义图像搜索应用

基于 CLIP 模型的自然语言图像搜索应用，支持中英文查询。

## 🌐 快速开始

### 1. 准备图片
```bash
# 将图片放入images文件夹
mkdir -p images
# 复制你的图片到images文件夹
```

### 2. 生成Embeddings
```bash
python get_embeddings.py
```

### 3. 启动应用
```bash
streamlit run app.py
```

### 4. 访问地址
http://localhost:8501

## 📦 安装

```bash
pip install -r requirements.txt
```

## ✨ 主要功能

- 🔍 **自然语言搜索**: 使用中英文描述搜索图片
- 📝 **查询增强**: 自动优化查询文本提高检索效果
- 🌡️ **温度调节**: 可调节相似度分布
- 📊 **相似度可视化**: 颜色编码显示匹配度
- ⚡ **快速检索**: 使用预计算embeddings，搜索速度快
- 🌍 **离线运行**: 使用本地模型，无需网络

## 🚀 使用流程

### 第一步：准备图片

将你的图片放入 `./images` 文件夹：

```bash
images/
├── photo1.jpg
├── photo2.png
├── photo3.jpg
└── ...
```

支持的格式：JPG, JPEG, PNG, WEBP, BMP, GIF

### 第二步：生成Embeddings

运行脚本为所有图片生成向量：

```bash
python get_embeddings.py
```

这会：
- 扫描 `./images` 文件夹中的所有图片
- 使用CLIP模型生成512维向量
- 保存到 `image_embeddings.pkl` 文件

**注意**: 只需运行一次，或在添加新图片时重新运行

### 第三步：搜索图片

启动Web应用：

```bash
streamlit run app.py
```

然后：
1. 在浏览器中打开 http://localhost:8501
2. 输入自然语言查询
3. 查看按相似度排序的结果
4. 调整参数优化效果

## 💡 搜索技巧

### 好的查询示例

✅ **描述性查询**
- "a golden retriever dog running in a green park"
- "modern glass building with blue sky background"
- "delicious pizza with cheese on wooden table"
- "一个穿着红色衣服的女孩在海边微笑"

### 避免的查询

❌ **太简单**: "dog", "car"
❌ **太模糊**: "thing", "stuff"
❌ **太主观**: "nice", "beautiful"

### 提高效果的方法

1. **使用描述性语言**: 包含颜色、动作、场景等细节
2. **包含关键特征**: 描述主要视觉元素
3. **使用具体词汇**: 避免抽象或模糊的词
4. **组合多个概念**: 描述完整场景
5. **支持中英文**: 两种语言都能获得好效果

## 🔧 技术栈

- **模型**: CLIP ViT-B-32 (LAION训练)
- **训练数据**: 2B+ 图像对
- **前端**: Streamlit
- **后端**: PyTorch + OpenCLIP
- **Embedding**: 512维语义向量
- **相似度**: 余弦相似度

## 📊 性能

- **Embedding生成**: ~40 images/second (CPU)
- **搜索速度**: 近乎实时 (< 100ms for 1000 images)
- **GPU加速**: 自动检测并使用
- **Embedding维度**: 512
- **相似度范围**: 0-100%
- **推荐阈值**: >25% 为相关结果

## 🎯 参数说明

### Query Enhancement (查询增强)
- **作用**: 自动添加"a photo of"等前缀
- **效果**: 提高短查询的检索准确度
- **建议**: 保持开启

### Temperature (温度)
- **范围**: 0.1 - 2.0
- **默认**: 1.0
- **调整**:
  - < 1.0: 使高分更高，低分更低（更集中）
  - = 1.0: 保持原始分布
  - > 1.0: 使分数更平滑（更分散）

## 📁 项目结构

```
.
├── app.py                    # 主应用（预计算版本）
├── app_upload_version.py     # 备用：实时上传版本
├── get_embeddings.py         # Embedding生成脚本
├── requirements.txt          # 依赖列表
├── images/                   # 图片文件夹
│   ├── photo1.jpg
│   └── ...
├── models/                   # 模型文件夹
│   └── ViT-B-32-laion2B-s34B-b79K/
│       ├── open_clip_pytorch_model.bin
│       └── open_clip_config.json
├── image_embeddings.pkl      # 预计算的embeddings
├── README.md                 # 本文件
└── OPTIMIZATION.md           # 优化说明
```

## 🔄 更新图片

当你添加新图片时：

1. 将新图片放入 `./images` 文件夹
2. 重新运行: `python get_embeddings.py`
3. 刷新浏览器页面

## 🔄 模型信息

### 当前模型
- **名称**: CLIP-ViT-B-32-laion2B-s34B-b79K
- **来源**: LAION
- **大小**: 577.2 MB
- **训练数据**: 2B+ 图像对

### 模型特点
- 更大规模的训练数据
- 更强的泛化能力
- 对多样化场景理解更好
- 长尾分布查询表现优秀

## 🎓 示例查询

### 英文查询
- "a person smiling happily"
- "red sports car on street"
- "delicious food on white plate"
- "beautiful sunset over mountains"
- "modern office interior"
- "cute dog playing in park"

### 中文查询
- "一个开心微笑的人"
- "街道上的红色跑车"
- "白色盘子上的美食"
- "山上的美丽日落"
- "现代办公室内景"
- "公园里玩耍的可爱小狗"

## 🐛 故障排除

### 未找到embeddings文件
运行 `python get_embeddings.py` 生成embeddings

### 模型加载失败
确保模型文件存在于 `./models/ViT-B-32-laion2B-s34B-b79K/` 目录

### 检索效果不佳
1. 开启 Query Enhancement
2. 调整 Temperature 参数
3. 使用更描述性的查询
4. 参考搜索技巧部分

### Embedding生成速度慢
- 使用GPU加速（如果可用）
- 分批处理大量图片

## 💻 两种使用模式

### 模式1: 预计算Embeddings（推荐）
- **文件**: `app.py` + `get_embeddings.py`
- **优点**: 搜索速度快，适合大量图片
- **适用**: 图片库相对固定的场景

### 模式2: 实时上传
- **文件**: `app_upload_version.py`
- **优点**: 无需预处理，即传即搜
- **适用**: 临时搜索，图片经常变化

切换到实时上传模式：
```bash
streamlit run app_upload_version.py
```

## 📚 参考资源

- [CLIP论文](https://arxiv.org/abs/2103.00020)
- [OpenCLIP项目](https://github.com/mlfoundations/open_clip)
- [LAION官网](https://laion.ai/)
- [Streamlit文档](https://docs.streamlit.io)

## 📄 许可证

本项目使用的组件：
- OpenAI CLIP (MIT License)
- Streamlit (Apache 2.0)
- PyTorch (BSD License)

---

**开始使用自然语言搜索你的图片吧！** 🔍✨
