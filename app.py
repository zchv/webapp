"""
CLIP 语义图像搜索 - 预计算Embeddings版本
使用预先生成的图片向量进行快速搜索
"""

import streamlit as st
import torch
import open_clip
from PIL import Image
import pickle
import os
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CLIP 语义图像搜索",
    page_icon="🔍",
    layout="wide"
)

# 配置
EMBEDDINGS_FILE = "image_embeddings.pkl"
MODEL_NAME = 'ViT-B-32'
PRETRAINED = './models/ViT-B-32-laion2B-s34B-b79K/open_clip_pytorch_model.bin'

@st.cache_resource
def load_clip_model():
    """加载CLIP模型"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED
    )
    model = model.to(device)
    model.eval()
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    return model, tokenizer, device

@st.cache_data
def load_embeddings():
    """加载预计算的图片embeddings"""
    if not os.path.exists(EMBEDDINGS_FILE):
        return None

    with open(EMBEDDINGS_FILE, 'rb') as f:
        data = pickle.load(f)

    return data

def enhance_query(query):
    """增强查询文本"""
    query = query.strip()

    # 如果查询很短，添加上下文
    if len(query.split()) <= 2:
        if not query.lower().startswith(('a ', 'an ', 'the ', '一个', '一张')):
            query = f"a photo of {query}"

    return query

def search_images(query, embeddings_data, model, tokenizer, device, top_k=20,
                 use_query_enhancement=True, temperature=1.0):
    """使用自然语言搜索图片"""
    # 查询增强
    if use_query_enhancement:
        enhanced_query = enhance_query(query)
    else:
        enhanced_query = query

    # 编码文本
    text = tokenizer([enhanced_query]).to(device)

    with torch.no_grad():
        # 提取文本特征
        text_features = model.encode_text(text)
        # L2归一化
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    # 转换为numpy
    text_features_np = text_features.cpu().numpy()

    # 计算相似度
    embeddings = embeddings_data['embeddings']
    similarities = (embeddings @ text_features_np.T).squeeze()

    # 应用温度缩放
    if temperature != 1.0:
        similarities = similarities / temperature

    # 转换为百分比
    similarities_percent = similarities * 100.0

    # 获取top k结果
    top_indices = np.argsort(similarities_percent)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            'path': embeddings_data['image_paths'][idx],
            'score': float(similarities_percent[idx])
        })

    return results, enhanced_query

# Main app
st.title("🔍 CLIP 语义图像搜索")
st.markdown("使用自然语言搜索你的图片库！")

# 加载模型
with st.spinner("加载CLIP模型..."):
    model, tokenizer, device = load_clip_model()
st.success(f"✅ 模型已加载 ({device})")

# 加载embeddings
embeddings_data = load_embeddings()

if embeddings_data is None:
    st.error("❌ 未找到图片embeddings文件！")
    st.markdown("""
    ### 📝 使用步骤

    1. **添加图片** 到 `./images` 文件夹
    2. **生成embeddings** 运行:
       ```bash
       python get_embeddings.py
       ```
    3. **刷新** 此页面

    💡 Embeddings只需生成一次，或在添加新图片时重新生成。
    """)
    st.stop()

# 显示统计信息
num_images = len(embeddings_data['image_paths'])
st.info(f"📊 已加载 {num_images} 张图片的embeddings")

# 侧边栏设置
with st.sidebar:
    st.header("⚙️ 搜索设置")

    use_enhancement = st.checkbox("查询增强", value=True,
                                  help="自动优化查询文本以提高检索效果")

    temperature = st.slider("温度", min_value=0.1, max_value=2.0, value=1.0, step=0.1,
                           help="调整相似度分布。<1: 更集中，>1: 更分散")

    st.markdown("---")
    st.markdown("### ℹ️ 信息")
    st.markdown(f"""
    **模型**: {MODEL_NAME} (LAION)
    **设备**: {device}
    **图片数量**: {num_images}
    **Embedding维度**: 512
    """)

    st.markdown("---")
    st.markdown("### 🔄 更新图片")
    st.markdown("""
    添加新图片后:
    1. 将图片放入 `./images` 文件夹
    2. 运行: `python get_embeddings.py`
    3. 刷新此页面
    """)

# 主内容区域
st.markdown("---")

# 搜索界面
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "🔎 输入搜索查询",
        placeholder="例如: 一个微笑的人, red car, sunset, 美食..."
    )
with col2:
    top_k = st.number_input("显示结果数", min_value=5, max_value=100, value=20, step=5)

# 搜索提示
with st.expander("💡 搜索技巧"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ 好的查询**")
        st.markdown("""
        - "a golden retriever dog running in park"
        - "modern glass building with blue sky"
        - "delicious pizza on wooden table"
        - "一个穿红衣服的女孩在海边"
        """)

    with col2:
        st.markdown("**❌ 避免的查询**")
        st.markdown("""
        - "dog" (太简单)
        - "thing" (太模糊)
        - "nice" (太主观)
        - "it" (无意义)
        """)

    st.markdown("---")
    st.markdown("**🎯 提高效果的方法:**")
    st.markdown("""
    1. 使用描述性语言，包含颜色、动作、场景等细节
    2. 包含关键特征，描述主要视觉元素
    3. 使用具体词汇，避免抽象或模糊的词
    4. 组合多个概念，描述完整场景
    5. 支持中英文，两种语言都能获得好效果
    """)

if query:
    with st.spinner("搜索中..."):
        results, enhanced_query = search_images(
            query,
            embeddings_data,
            model,
            tokenizer,
            device,
            int(top_k),
            use_query_enhancement=use_enhancement,
            temperature=temperature
        )

    # 显示增强后的查询
    if use_enhancement and enhanced_query != query:
        st.info(f"🔄 增强查询: `{enhanced_query}`")

    st.markdown(f"### 搜索结果: *'{query}'*")

    # 显示相似度统计
    scores = [r['score'] for r in results]
    if scores:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("最高分", f"{max(scores):.1f}%")
        with col2:
            st.metric("平均分", f"{np.mean(scores):.1f}%")
        with col3:
            st.metric("最低分", f"{min(scores):.1f}%")

    # 显示结果网格
    cols_per_row = 4
    for i in range(0, len(results), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(results):
                result = results[i + j]
                with col:
                    try:
                        img = Image.open(result['path'])
                        st.image(img, use_container_width=True)

                        # 颜色编码相似度
                        score = result['score']
                        if score >= 30:
                            color = "🟢"
                        elif score >= 20:
                            color = "🟡"
                        else:
                            color = "🔴"

                        st.caption(f"{color} **{score:.1f}%**")
                        st.caption(f"{os.path.basename(result['path'])}")
                    except Exception as e:
                        st.error(f"加载图片出错: {e}")

else:
    # 显示示例查询
    st.markdown("### 💡 示例查询")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**英文查询:**")
        st.markdown("""
        - "a person smiling happily"
        - "red sports car on street"
        - "delicious food on white plate"
        - "beautiful sunset over mountains"
        - "modern office interior"
        - "cute dog playing in park"
        """)

    with col2:
        st.markdown("**中文查询:**")
        st.markdown("""
        - "一个开心微笑的人"
        - "街道上的红色跑车"
        - "白色盘子上的美食"
        - "山上的美丽日落"
        - "现代办公室内景"
        - "公园里玩耍的可爱小狗"
        """)

    # 显示部分样例图片
    with st.expander("📸 查看部分图片样例", expanded=False):
        sample_size = min(12, num_images)
        sample_indices = np.random.choice(num_images, sample_size, replace=False)

        cols = st.columns(4)
        for idx, img_idx in enumerate(sample_indices):
            with cols[idx % 4]:
                try:
                    img_path = embeddings_data['image_paths'][img_idx]
                    img = Image.open(img_path)
                    st.image(img, caption=os.path.basename(img_path), use_container_width=True)
                except Exception as e:
                    st.error(f"加载出错: {e}")
