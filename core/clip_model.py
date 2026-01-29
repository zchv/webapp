import torch
import open_clip
from PIL import Image
import numpy as np
from typing import Union, List
import config


class CLIPModelWrapper:
    """
    Singleton wrapper for CLIP model with multi-modal encoding support.
    Optimized for Apple Silicon (MPS), CUDA, and CPU.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        print(f"Loading CLIP model on device: {config.DEVICE}")
        self.device = config.DEVICE

        # Load CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            config.CLIP_MODEL_NAME,
            pretrained=config.CLIP_PRETRAINED
        )
        self.model = self.model.to(self.device)
        self.model.eval()

        # Load tokenizer
        self.tokenizer = open_clip.get_tokenizer(config.CLIP_MODEL_NAME)

        self._initialized = True
        print("CLIP model loaded successfully")

    @torch.no_grad()
    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Encode text to feature vector(s).

        Args:
            text: Single text string or list of text strings

        Returns:
            Normalized feature vector(s) as numpy array
        """
        if isinstance(text, str):
            text = [text]

        # Tokenize
        text_tokens = self.tokenizer(text).to(self.device)

        # Encode
        text_features = self.model.encode_text(text_tokens)

        # Normalize
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()

    @torch.no_grad()
    def encode_image(self, image: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        """
        Encode image(s) to feature vector(s).

        Args:
            image: Single PIL Image or list of PIL Images

        Returns:
            Normalized feature vector(s) as numpy array
        """
        if isinstance(image, Image.Image):
            image = [image]

        # Preprocess
        image_tensors = torch.stack([self.preprocess(img) for img in image])
        image_tensors = image_tensors.to(self.device)

        # Encode
        image_features = self.model.encode_image(image_tensors)

        # Normalize
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()

    @torch.no_grad()
    def encode_multimodal(
        self,
        text: str,
        image: Image.Image,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Encode text and image with weighted fusion.

        Args:
            text: Text query
            image: PIL Image
            alpha: Weight for text (0=pure image, 1=pure text, 0.5=balanced)

        Returns:
            Normalized fused feature vector
        """
        # Encode both modalities
        text_features = self.encode_text(text)[0]
        image_features = self.encode_image(image)[0]

        # Weighted fusion
        combined_features = alpha * text_features + (1 - alpha) * image_features

        # Re-normalize
        combined_features = combined_features / np.linalg.norm(combined_features)

        return combined_features

    def encode_batch_images(self, images: List[Image.Image], batch_size: int = 32) -> np.ndarray:
        """
        Encode images in batches for efficiency.

        Args:
            images: List of PIL Images
            batch_size: Batch size for encoding

        Returns:
            Normalized feature vectors as numpy array
        """
        all_features = []

        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            features = self.encode_image(batch)
            all_features.append(features)

        return np.vstack(all_features)
