"""
从embeddings生成FAISS索引
用法: python build_faiss_index.py
"""

import pickle
import numpy as np
from pathlib import Path
from core.faiss_index import FAISSIndexManager

def build_faiss_index():
    """从image_embeddings.pkl构建FAISS索引"""

    # 加载embeddings
    embeddings_file = "image_embeddings.pkl"

    if not Path(embeddings_file).exists():
        print(f"❌ 未找到 {embeddings_file}")
        print("请先运行: python get_embeddings.py")
        return

    print(f"📂 加载embeddings: {embeddings_file}")
    with open(embeddings_file, 'rb') as f:
        data = pickle.load(f)

    embeddings = data['embeddings']
    image_paths = data['image_paths']

    print(f"✅ 加载了 {len(image_paths)} 张图片的embeddings")
    print(f"📦 Embedding维度: {embeddings.shape}")

    # 创建元数据
    metadata_list = []
    for path in image_paths:
        metadata_list.append({
            'filename': Path(path).name,
            'path': str(path)
        })

    # 建立FAISS索引
    print("\n🔄 构建FAISS索引...")
    faiss_manager = FAISSIndexManager()
    faiss_manager.build_index(embeddings.astype('float32'), image_paths, metadata_list)

    # 保存索引
    print("\n💾 保存FAISS索引...")
    faiss_manager.save_index()

    print("\n✅ FAISS索引创建成功！")
    print("📊 索引统计:")
    stats = faiss_manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n🚀 现在可以运行 python app_web.py 来启动Flask应用")

if __name__ == "__main__":
    build_faiss_index()
