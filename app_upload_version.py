"""
CLIP Image Search - Enhanced Version with Better Semantic Search
优化的语义检索版本
"""

import streamlit as st
import torch
import open_clip
from PIL import Image
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CLIP Image Search - Enhanced",
    page_icon="🔍",
    layout="wide"
)

MODEL_NAME = 'ViT-B-32'
PRETRAINED = './models/ViT-B-32-laion2B-s34B-b79K/open_clip_pytorch_model.bin'

@st.cache_resource
def load_clip_model():
    """Load CLIP model"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED
    )
    model = model.to(device)
    model.eval()
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    return model, preprocess, tokenizer, device

# Initialize session state
if 'images' not in st.session_state:
    st.session_state.images = []
if 'image_features' not in st.session_state:
    st.session_state.image_features = None

def enhance_query(query):
    """增强查询文本，提高语义检索效果"""
    query = query.strip()

    # 如果查询很短，添加上下文
    if len(query.split()) <= 2:
        # 添加"a photo of"前缀，这是CLIP训练时常用的模式
        if not query.lower().startswith(('a ', 'an ', 'the ')):
            query = f"a photo of {query}"

    return query

def process_images(uploaded_files, model, preprocess, device):
    """Process uploaded images and extract features with better preprocessing"""
    images = []
    image_features_list = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")

        try:
            # 加载图像
            image = Image.open(uploaded_file).convert("RGB")

            # 保存原始图像用于显示
            images.append((uploaded_file.name, image))

            # 预处理并提取特征
            image_input = preprocess(image).unsqueeze(0).to(device)

            with torch.no_grad():
                # 提取图像特征
                image_feature = model.encode_image(image_input)
                # L2归一化 - 这对余弦相似度很重要
                image_feature = image_feature / image_feature.norm(dim=-1, keepdim=True)

            image_features_list.append(image_feature)

        except Exception as e:
            st.warning(f"Error processing {uploaded_file.name}: {e}")
            continue

        progress_bar.progress((idx + 1) / len(uploaded_files))

    progress_bar.empty()
    status_text.empty()

    if image_features_list:
        image_features = torch.cat(image_features_list, dim=0)
        return images, image_features
    return [], None

def search_images(query, images, image_features, model, tokenizer, device, top_k=20,
                 use_query_enhancement=True, temperature=1.0):
    """
    Enhanced semantic search with multiple improvements

    Args:
        query: 搜索查询
        images: 图像列表
        image_features: 图像特征
        model: CLIP模型
        tokenizer: 文本tokenizer
        device: 计算设备
        top_k: 返回top k结果
        use_query_enhancement: 是否使用查询增强
        temperature: 温度参数，用于调整相似度分布
    """
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

    # 计算余弦相似度
    # image_features 和 text_features 都已归一化，所以点积就是余弦相似度
    similarity = (image_features @ text_features.T).squeeze()

    # 应用温度缩放（可选）
    if temperature != 1.0:
        similarity = similarity / temperature

    # 转换为百分比 (0-100)
    similarity_percent = similarity * 100.0

    # 排序并返回top k结果
    if len(images) > 1:
        values, indices = similarity_percent.sort(descending=True)
        indices = indices[:top_k]
        results = [(images[idx], values[idx].item()) for idx in indices]
    else:
        results = [(images[0], similarity_percent.item())]

    return results, enhanced_query

# Main app
st.title("🔍 CLIP 语义图像搜索 - 增强版")
st.markdown("上传图片，使用自然语言进行语义搜索！")

# Load model
with st.spinner("Loading CLIP model..."):
    model, preprocess, tokenizer, device = load_clip_model()
st.success(f"✅ Model loaded on {device}")

# Sidebar for image upload and settings
with st.sidebar:
    st.header("📁 Upload Images")
    uploaded_files = st.file_uploader(
        "Choose images",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if uploaded_files:
        if st.button("Process Images", type="primary"):
            with st.spinner("Processing images..."):
                images, features = process_images(uploaded_files, model, preprocess, device)
                if images:
                    st.session_state.images = images
                    st.session_state.image_features = features
                    st.success(f"✅ Processed {len(images)} images!")
                else:
                    st.error("No images were processed successfully")

    if st.session_state.images:
        st.markdown("---")
        st.metric("Images Loaded", len(st.session_state.images))

        if st.button("Clear All"):
            st.session_state.images = []
            st.session_state.image_features = None
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Search Settings")

    use_enhancement = st.checkbox("Query Enhancement", value=True,
                                  help="自动优化查询文本以提高检索效果")

    temperature = st.slider("Temperature", min_value=0.1, max_value=2.0, value=1.0, step=0.1,
                           help="调整相似度分布。<1: 更集中，>1: 更分散")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(f"""
    **Model**: {MODEL_NAME} (LAION)
    **Device**: {device}
    **Features**:
    - Query enhancement
    - Temperature scaling
    - L2 normalized embeddings
    """)

# Main content
if st.session_state.images:
    st.subheader(f"📊 {len(st.session_state.images)} images loaded")

    # Search interface
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "🔎 Enter your search query",
            placeholder="例如: 一个微笑的人, red car, sunset, 食物..."
        )
    with col2:
        top_k = st.number_input("Results", min_value=1, max_value=50,
                               value=min(20, len(st.session_state.images)))

    # 搜索提示
    with st.expander("💡 搜索技巧"):
        st.markdown("""
        **提高检索效果的技巧:**

        1. **使用描述性语言**:
           - ✅ "a person wearing red shirt smiling"
           - ❌ "person"

        2. **包含关键特征**:
           - ✅ "sunset over ocean with orange sky"
           - ❌ "sunset"

        3. **使用具体词汇**:
           - ✅ "golden retriever dog playing"
           - ❌ "animal"

        4. **支持中英文**:
           - "一只可爱的猫咪"
           - "a cute cat"

        5. **组合多个概念**:
           - "modern building with glass windows at night"
        """)

    if query:
        with st.spinner("Searching..."):
            results, enhanced_query = search_images(
                query,
                st.session_state.images,
                st.session_state.image_features,
                model,
                tokenizer,
                device,
                int(top_k),
                use_query_enhancement=use_enhancement,
                temperature=temperature
            )

        # 显示增强后的查询
        if use_enhancement and enhanced_query != query:
            st.info(f"🔄 Enhanced query: `{enhanced_query}`")

        st.markdown(f"### Results for: *'{query}'*")

        # 显示相似度统计
        scores = [score for _, score in results]
        if scores:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Highest Score", f"{max(scores):.1f}%")
            with col2:
                st.metric("Average Score", f"{np.mean(scores):.1f}%")
            with col3:
                st.metric("Lowest Score", f"{min(scores):.1f}%")

        # Display results in grid
        cols_per_row = 4
        for i in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(results):
                    (name, image), score = results[i + j]
                    with col:
                        st.image(image, use_container_width=True)

                        # 颜色编码相似度
                        if score >= 30:
                            color = "🟢"
                        elif score >= 20:
                            color = "🟡"
                        else:
                            color = "🔴"

                        st.caption(f"{color} **{score:.1f}%** - {name}")

    # Show all images
    with st.expander("📸 View all uploaded images"):
        cols = st.columns(5)
        for idx, (name, image) in enumerate(st.session_state.images):
            with cols[idx % 5]:
                st.image(image, caption=name, use_container_width=True)

else:
    st.info("👈 Please upload images using the sidebar to get started!")

    # Example queries
    st.markdown("### 💡 Example Queries")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**English:**")
        st.markdown("""
        - "a person smiling happily"
        - "red sports car on street"
        - "delicious food on white plate"
        - "beautiful sunset over mountains"
        - "modern office interior"
        - "cute dog playing in park"
        """)

    with col2:
        st.markdown("**中文:**")
        st.markdown("""
        - "一个开心微笑的人"
        - "街道上的红色跑车"
        - "白色盘子上的美食"
        - "山上的美丽日落"
        - "现代办公室内景"
        - "公园里玩耍的可爱小狗"
        """)

    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. Click **"Browse files"** in the sidebar
    2. Select multiple images from your computer
    3. Click **"Process Images"**
    4. Enter a natural language query to search
    5. Adjust settings for better results
    """)

    st.markdown("### 🎯 优化建议")
    st.markdown("""
    - **Query Enhancement**: 自动添加"a photo of"等前缀，提高检索准确度
    - **Temperature**: 调整相似度分布，找到最适合你数据的设置
    - **描述性查询**: 使用更详细的描述词获得更好的结果
    """)
