"""
生成图片向量并保存为pkl文件
用法: python get_embeddings.py
"""

import torch
import open_clip
from PIL import Image
import os
import pickle
from tqdm import tqdm
import numpy as np

# 配置
IMAGE_FOLDER = "./data/images"
OUTPUT_FILE = "image_embeddings.pkl"
MODEL_NAME = 'ViT-B-32'
PRETRAINED = './models/ViT-B-32-laion2B-s34B-b79K/open_clip_pytorch_model.bin'

def get_image_files(folder):
    """获取文件夹中所有图片文件"""
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
    image_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file.lower())[1] in extensions:
                image_files.append(os.path.join(root, file))

    return sorted(image_files)

def generate_embeddings():
    """为所有图片生成embeddings"""
    print(f"🔧 加载CLIP模型: {MODEL_NAME}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"📱 使用设备: {device}")

    # 加载模型
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED
    )
    model = model.to(device)
    model.eval()

    print(f"\n📂 扫描图片文件夹: {IMAGE_FOLDER}")
    image_files = get_image_files(IMAGE_FOLDER)

    if not image_files:
        print(f"❌ 在 {IMAGE_FOLDER} 中没有找到图片")
        print(f"请将图片放入该文件夹后重试")
        return

    print(f"✅ 找到 {len(image_files)} 张图片")

    # 生成embeddings
    embeddings = []
    valid_files = []

    print("\n🔄 生成embeddings...")
    with torch.no_grad():
        for img_path in tqdm(image_files, desc="处理进度"):
            try:
                # 加载并预处理图片
                image = Image.open(img_path).convert('RGB')
                image_input = preprocess(image).unsqueeze(0).to(device)

                # 生成embedding
                image_features = model.encode_image(image_input)
                # L2归一化
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

                embeddings.append(image_features.cpu().numpy())
                valid_files.append(img_path)

            except Exception as e:
                print(f"\n⚠️  处理 {img_path} 时出错: {e}")
                continue

    if not embeddings:
        print("❌ 没有成功生成任何embeddings")
        return

    # 合并embeddings
    embeddings = np.vstack(embeddings)

    # 保存到pickle文件
    data = {
        'embeddings': embeddings,
        'image_paths': valid_files,
        'model_name': MODEL_NAME,
        'pretrained': PRETRAINED
    }

    print(f"\n💾 保存embeddings到 {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(data, f)

    print(f"✅ 成功为 {len(valid_files)} 张图片生成embeddings")
    print(f"📦 Embedding维度: {embeddings.shape}")
    print(f"💾 已保存到: {OUTPUT_FILE}")
    print(f"\n🚀 现在可以运行 python build_faiss_index.py 来构建FAISS索引")

if __name__ == "__main__":
    generate_embeddings()
