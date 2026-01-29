# CLIP Semantic Image Search - Flask Web Application

A complete web-based semantic image search application powered by OpenAI CLIP and FAISS. Search your image library using natural language, images, voice, or multimodal queries.

[中文版 README](README.md) | **English README (Flask Web Version)**

## Features

### 🔍 5 Search Modes
- **Text Search**: Natural language queries with automatic query enhancement
- **Voice Search**: Speech-to-text using Web Speech API
- **Image Search**: Upload an image to find similar images
- **Multimodal Search**: Combine text and image queries with adjustable weighting
- **Multi-Image Fusion**: Upload multiple images for averaged similarity search

### 🎨 Modern Web UI
- Responsive design (desktop, tablet, mobile)
- Real-time search results with lazy loading
- Similarity score color coding (green ≥30%, yellow ≥20%, red <20%)
- Dual loading modes: Pagination or Infinite Scroll
- Dark mode ready (CSS variables)

### 👥 User Feedback System
- Like, favorite, and mark-as-irrelevant buttons
- Real-time feedback persistence to SQLite
- Result reranking based on user feedback
- Statistics dashboard for popular queries and top-rated images

### ⚙️ Advanced Features
- Query enhancement for better results
- Top-100 retrieval with Top-20 reranking
- Search history (localStorage)
- Drag-and-drop file uploads
- Mobile-optimized voice input
- Health check API endpoint

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Images
```bash
# Place your images in the images/ directory
mkdir -p images
# Copy your images to images/
```

### 3. Generate FAISS Index
```bash
python get_embeddings.py
```

### 4. Run Flask App
```bash
python app_web.py
```

### 5. Open Browser
```
http://localhost:5000
```

## Usage

### Text Search
1. Navigate to the "Text" tab
2. Enter a natural language query (e.g., "a dog playing in the park")
3. Adjust settings (query enhancement, top-k)
4. Click "Search" or press Enter

### Voice Search
1. Navigate to the "Voice" tab
2. Click the microphone button
3. Speak your query clearly
4. Results appear automatically after transcription

### Image Search
1. Navigate to the "Image" tab
2. Drag and drop an image, or click to select
3. Click "Search by Image"

### Multimodal Search
1. Navigate to the "Multimodal" tab
2. Enter a text query
3. Upload an image
4. Adjust alpha slider (0 = pure image, 1 = pure text, 0.5 = balanced)
5. Click "Search"

### Multi-Image Search
1. Navigate to the "Multi-Image" tab
2. Upload up to 10 images
3. Click "Search by Images"
4. Results are based on averaged image vectors

## Architecture

```
Flask Web App (app_web.py)
    ↓
API Layer (api/search.py)
    ↓
Core Components:
  ├── CLIP Model (core/clip_model.py) - Multi-modal encoding
  ├── FAISS Index (core/faiss_index.py) - Vector similarity search
  └── Feedback DB (core/feedback.py) - SQLite feedback storage
    ↓
Frontend:
  ├── Templates (templates/) - Jinja2 HTML
  ├── Styles (static/css/) - Responsive CSS
  └── Scripts (static/js/) - Vanilla JavaScript
```

## API Endpoints

### Search
- `POST /api/search/text` - Text search
- `POST /api/search/image` - Image search
- `POST /api/search/multimodal` - Multimodal search
- `POST /api/search/voice` - Voice search
- `POST /api/search/multi-image` - Multi-image fusion
- `GET /api/search/stats` - Statistics

### Feedback
- `POST /api/search/feedback/record` - Record feedback
- `GET /api/search/feedback/stats/<image_id>` - Get feedback
- `GET /api/search/feedback/top-rated` - Top-rated images

### Utility
- `GET /api/health` - Health check
- `GET /api/examples` - Example queries

## Configuration

Edit `config.py`:

```python
# Search settings
DEFAULT_TOP_K = 20              # Default results
FAISS_RETRIEVE_K = 100          # Retrieve for reranking
ENABLE_RERANK = True            # Feedback-based reranking

# CLIP model
CLIP_MODEL_NAME = "ViT-B-32"
CLIP_PRETRAINED = "laion2b_s34b_b79k"

# Device (auto-detected)
DEVICE = "mps" | "cuda" | "cpu"  # Apple Silicon | NVIDIA | CPU

# Upload
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
```

## 环境信息

### 已测试环境
- **Python**: 3.13.2
- **操作系统**: macOS 14+ (Apple Silicon)
- **Flask**: 3.1.2
- **PyTorch**: 2.10.0 (CPU 版本)
- **FAISS**: 1.13.2
- **设备加速**: MPS (Metal Performance Shaders)

## 浏览器兼容性

### 桌面
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### 移动设备
- ✅ iOS Safari 14+
- ✅ Android Chrome 90+

### 语音输入支持
- Chrome, Edge, Safari (Web Speech API)
- ❌ Firefox (不支持)

## Performance

On MacBook Pro M1 with 10K images:
- **Search latency**: <1s (text), <1.5s (image)
- **Page load**: <2s
- **CLIP loading**: ~5s (first request)
- **FAISS search**: <50ms

## File Structure

```
agent-webapp/
├── app_web.py                  # Flask app entry
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
│
├── api/                        # API layer
│   ├── search.py              # Endpoints
│   └── utils.py               # Utilities
│
├── core/                       # ML components
│   ├── clip_model.py          # CLIP wrapper
│   ├── faiss_index.py         # FAISS manager
│   └── feedback.py            # Feedback DB
│
├── utils/                      # Utilities
│   ├── image_processor.py     # Image processing
│   └── query_enhancer.py      # Query enhancement
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Search page
│   ├── settings.html          # Settings
│   └── stats.html             # Statistics
│
├── static/                     # Static assets
│   ├── css/                   # Stylesheets
│   │   ├── main.css           # Core styles
│   │   ├── search.css         # Search UI
│   │   ├── results.css        # Results grid
│   │   ├── feedback.css       # Feedback
│   │   ├── loading.css        # Loading states
│   │   ├── modal.css          # Modals
│   │   └── responsive.css     # Mobile
│   │
│   └── js/                    # JavaScript
│       ├── main.js            # API client
│       ├── ui.js              # UI utilities
│       ├── search.js          # Search forms
│       ├── results.js         # Results display
│       ├── upload.js          # File upload
│       ├── voice.js           # Voice input
│       ├── feedback.js        # Feedback
│       ├── modal.js           # Modals
│       ├── settings.js        # Settings
│       └── stats.js           # Statistics
│
└── data/                       # Data
    ├── faiss_index/           # FAISS index
    │   ├── index.faiss        # Vectors
    │   └── metadata.json      # Metadata
    │
    └── feedback.db            # SQLite DB
```

## Troubleshooting

### Model Loading Error
```
Error: CLIP model failed to load
```
**Solution**: Install `open-clip-torch` and check model name

### Index Not Found
```
Error: Index file not found
```
**Solution**: Run `python get_embeddings.py`

### Voice Not Working
**Solution**:
- Use Chrome/Edge/Safari
- Grant microphone permissions
- Use HTTPS in production

### Upload Fails
```
Error: File type not allowed
```
**Solution**: Only image files allowed (PNG, JPG, etc.)

## Development

### Debug Mode
```bash
export DEBUG=True
python app_web.py
```

### Custom Endpoints
1. Add route in `api/search.py`
2. Register in `app_web.py`
3. Create frontend handler

### UI Customization
- Edit CSS variables in `static/css/main.css`
- Modify templates in `templates/`
- Extend JavaScript classes

## Tech Stack

- **Backend**: Flask 2.3+
- **ML**: PyTorch + OpenCLIP + FAISS
- **Frontend**: Vanilla JavaScript (ES6+)
- **CSS**: Grid + Flexbox + Variables
- **Database**: SQLite
- **APIs**: Web Speech API, Fetch API

## Acknowledgments

- **OpenAI CLIP**: Multi-modal embeddings
- **FAISS**: Similarity search
- **Flask**: Web framework
- **Web Speech API**: Voice input

---

**Version**: 1.0
**Last Updated**: 2025-01-29
**Original Streamlit Version**: See [README.md](README.md)
