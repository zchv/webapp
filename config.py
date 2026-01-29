import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"

# Image paths
IMAGES_DIR = DATA_DIR / "images"
UPLOADS_DIR = STATIC_DIR / "uploads"

# FAISS index paths
FAISS_DIR = DATA_DIR / "faiss_index"
FAISS_INDEX_PATH = FAISS_DIR / "index.faiss"
METADATA_PATH = FAISS_DIR / "metadata.json"

# Database
FEEDBACK_DB_PATH = DATA_DIR / "feedback.db"

# CLIP model settings
CLIP_MODEL_NAME = "ViT-B-32"
# 使用本地模型文件（LAION训练版本，性能更好）
CLIP_PRETRAINED = "./models/ViT-B-32-laion2B-s34B-b79K/open_clip_pytorch_model.bin"

# Device settings - prioritize MPS > CUDA > CPU
import torch
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

# Search settings
DEFAULT_TOP_K = 20
FAISS_RETRIEVE_K = 100  # Retrieve top 100 for reranking
ENABLE_RERANK = True

# API settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Create directories if they don't exist
for directory in [DATA_DIR, IMAGES_DIR, UPLOADS_DIR, FAISS_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
