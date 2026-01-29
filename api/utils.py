"""
API Utility Functions
"""

from pathlib import Path
from werkzeug.utils import secure_filename
import config


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def save_upload(file, directory=None):
    """
    Save uploaded file and return the path.

    Args:
        file: FileStorage object from request
        directory: Optional directory to save to (defaults to UPLOADS_DIR)

    Returns:
        Path to saved file
    """
    if not file or file.filename == '':
        raise ValueError("No file provided")

    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}")

    filename = secure_filename(file.filename)
    save_dir = directory or config.UPLOADS_DIR
    save_dir.mkdir(parents=True, exist_ok=True)

    filepath = save_dir / filename

    # Handle duplicate filenames
    counter = 1
    while filepath.exists():
        name, ext = filename.rsplit('.', 1)
        filepath = save_dir / f"{name}_{counter}.{ext}"
        counter += 1

    file.save(str(filepath))
    return filepath


def calculate_combined_score(similarity_score, feedback_stats, alpha=0.8):
    """
    Calculate combined score from similarity and feedback.

    Args:
        similarity_score: FAISS similarity score (0-1)
        feedback_stats: Dict with 'like', 'favorite', 'irrelevant' counts
        alpha: Weight for similarity (1-alpha for feedback)

    Returns:
        Combined score (0-1)
    """
    # Calculate feedback score
    likes = feedback_stats.get('like', 0)
    favorites = feedback_stats.get('favorite', 0)
    irrelevant = feedback_stats.get('irrelevant', 0)

    total_feedback = likes + favorites + irrelevant
    if total_feedback == 0:
        feedback_score = 0.5  # Neutral if no feedback
    else:
        # Favorites worth 2x likes
        positive = likes + (favorites * 2)
        feedback_score = positive / (total_feedback + favorites)

    # Combine scores
    combined = (similarity_score * alpha) + (feedback_score * (1 - alpha))
    return combined
