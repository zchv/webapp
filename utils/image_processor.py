from PIL import Image
import io
from typing import Union


def load_image(image_source: Union[str, bytes, Image.Image]) -> Image.Image:
    """
    Load image from various sources.

    Args:
        image_source: File path, bytes, or PIL Image

    Returns:
        PIL Image in RGB mode
    """
    if isinstance(image_source, Image.Image):
        image = image_source
    elif isinstance(image_source, bytes):
        image = Image.open(io.BytesIO(image_source))
    elif isinstance(image_source, str):
        image = Image.open(image_source)
    else:
        raise ValueError(f"Unsupported image source type: {type(image_source)}")

    # Convert to RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')

    return image


def validate_image(image: Image.Image, max_size: int = 4096) -> bool:
    """
    Validate image dimensions.

    Args:
        image: PIL Image
        max_size: Maximum dimension size

    Returns:
        True if valid
    """
    width, height = image.size
    return width <= max_size and height <= max_size


def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize image if too large, maintaining aspect ratio.

    Args:
        image: PIL Image
        max_size: Maximum dimension size

    Returns:
        Resized PIL Image
    """
    width, height = image.size

    if width <= max_size and height <= max_size:
        return image

    # Calculate new dimensions
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
