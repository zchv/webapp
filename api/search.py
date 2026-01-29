from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import numpy as np
import config
from utils.query_enhancer import enhance_query
from utils.image_processor import load_image, resize_image
from api.utils import allowed_file, calculate_combined_score

search_bp = Blueprint('search', __name__)

# These will be injected by the main app
clip_model = None
faiss_index = None
feedback_manager = None


def init_search_api(clip, faiss, feedback):
    """Initialize API with model instances."""
    global clip_model, faiss_index, feedback_manager
    clip_model = clip
    faiss_index = faiss
    feedback_manager = feedback


def convert_image_path_to_url(image_path):
    """
    Convert file system image path to web URL.

    Args:
        image_path: Absolute or relative file path

    Returns:
        Web-accessible URL path
    """
    # Convert to Path object
    path = Path(image_path)

    # Get the filename
    filename = path.name

    # If path contains 'data/images', extract everything after it
    path_str = str(path)
    if 'data/images' in path_str:
        # Extract the part after 'data/images/'
        parts = path_str.split('data/images/')
        if len(parts) > 1:
            filename = parts[-1].lstrip('./')

    # Convert to web URL format
    return f"/images/{filename}"


@search_bp.route('/text', methods=['POST'])
def search_by_text():
    """
    Search images by text query.

    Request body:
        {
            "query": "a dog playing in the park",
            "top_k": 20,
            "enhance": true
        }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', config.DEFAULT_TOP_K)
        enhance = data.get('enhance', True)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Enhance query if requested
        if enhance:
            enhanced_query = enhance_query(query)
            print(f"Original query: '{query}' -> Enhanced: '{enhanced_query}'")
        else:
            enhanced_query = query

        # Encode query
        query_vector = clip_model.encode_text(enhanced_query)[0]

        # Search in FAISS
        retrieve_k = config.FAISS_RETRIEVE_K if config.ENABLE_RERANK else top_k
        results = faiss_index.search(query_vector, top_k=retrieve_k)

        # TODO: Add reranking if enabled
        if config.ENABLE_RERANK and len(results) > top_k:
            # For now, just truncate to top_k
            # Reranking will be implemented in Phase 6
            results = results[:top_k]

        # Update query stats
        if results:
            feedback_manager.update_query_stats(query, results[0]['score'])

        # Format results for frontend
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'image_path': convert_image_path_to_url(result['image_path']),
                'score': round(result['score'] * 100, 2),  # Convert to percentage
                'filename': result['metadata'].get('filename', ''),
                'metadata': result['metadata']
            })

        return jsonify({
            'success': True,
            'query': query,
            'enhanced_query': enhanced_query if enhance else None,
            'total_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        print(f"Error in text search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/image', methods=['POST'])
def search_by_image():
    """
    Search images by uploading an image.

    Request: multipart/form-data with 'image' file
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        top_k = int(request.form.get('top_k', config.DEFAULT_TOP_K))

        # Read and process image
        image_bytes = file.read()
        image = load_image(image_bytes)
        image = resize_image(image)

        # Encode image
        query_vector = clip_model.encode_image(image)[0]

        # Search in FAISS
        retrieve_k = config.FAISS_RETRIEVE_K if config.ENABLE_RERANK else top_k
        results = faiss_index.search(query_vector, top_k=retrieve_k)

        # TODO: Add reranking if enabled
        if config.ENABLE_RERANK and len(results) > top_k:
            results = results[:top_k]

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'image_path': convert_image_path_to_url(result['image_path']),
                'score': round(result['score'] * 100, 2),
                'filename': result['metadata'].get('filename', ''),
                'metadata': result['metadata']
            })

        return jsonify({
            'success': True,
            'search_type': 'image',
            'total_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        print(f"Error in image search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/multimodal', methods=['POST'])
def search_multimodal():
    """
    Search with both text and image.

    Request: multipart/form-data with:
        - query: text query
        - image: image file
        - alpha: text weight (0-1, default 0.5)
    """
    try:
        query = request.form.get('query', '').strip()
        alpha = float(request.form.get('alpha', 0.5))
        top_k = int(request.form.get('top_k', config.DEFAULT_TOP_K))

        if not query or 'image' not in request.files:
            return jsonify({'error': 'Both query and image are required'}), 400

        # Validate alpha
        if not 0 <= alpha <= 1:
            return jsonify({'error': 'Alpha must be between 0 and 1'}), 400

        # Load image
        file = request.files['image']
        image_bytes = file.read()
        image = load_image(image_bytes)
        image = resize_image(image)

        # Enhance query
        enhanced_query = enhance_query(query)

        # Encode multimodal query
        query_vector = clip_model.encode_multimodal(enhanced_query, image, alpha=alpha)

        # Search in FAISS
        retrieve_k = config.FAISS_RETRIEVE_K if config.ENABLE_RERANK else top_k
        results = faiss_index.search(query_vector, top_k=retrieve_k)

        # TODO: Add reranking if enabled
        if config.ENABLE_RERANK and len(results) > top_k:
            results = results[:top_k]

        # Update query stats
        if results:
            feedback_manager.update_query_stats(f"[multimodal] {query}", results[0]['score'])

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'image_path': convert_image_path_to_url(result['image_path']),
                'score': round(result['score'] * 100, 2),
                'filename': result['metadata'].get('filename', ''),
                'metadata': result['metadata']
            })

        return jsonify({
            'success': True,
            'search_type': 'multimodal',
            'query': query,
            'enhanced_query': enhanced_query,
            'alpha': alpha,
            'total_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        print(f"Error in multimodal search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/stats', methods=['GET'])
def get_search_stats():
    """Get search statistics."""
    try:
        index_stats = faiss_index.get_stats()
        popular_queries = feedback_manager.get_popular_queries(limit=10)

        return jsonify({
            'success': True,
            'index_stats': index_stats,
            'popular_queries': popular_queries
        })

    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/voice', methods=['POST'])
def search_by_voice():
    """
    Voice search endpoint.
    Receives transcribed text from Web Speech API and performs text search.

    Request body:
        {
            "query": "transcribed text from voice",
            "top_k": 20,
            "enhance": true
        }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', config.DEFAULT_TOP_K)
        enhance = data.get('enhance', True)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Enhance query if requested
        if enhance:
            enhanced_query = enhance_query(query)
            print(f"Voice query: '{query}' -> Enhanced: '{enhanced_query}'")
        else:
            enhanced_query = query

        # Encode query
        query_vector = clip_model.encode_text(enhanced_query)[0]

        # Search in FAISS
        retrieve_k = config.FAISS_RETRIEVE_K if config.ENABLE_RERANK else top_k
        results = faiss_index.search(query_vector, top_k=retrieve_k)

        # Rerank if enabled
        if config.ENABLE_RERANK and len(results) > top_k:
            results = rerank_results(results, query)[:top_k]

        # Update query stats
        if results:
            feedback_manager.update_query_stats(f"[voice] {query}", results[0]['score'])

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'image_path': convert_image_path_to_url(result['image_path']),
                'score': round(result['score'] * 100, 2),
                'filename': result['metadata'].get('filename', ''),
                'metadata': result['metadata']
            })

        return jsonify({
            'success': True,
            'search_type': 'voice',
            'query': query,
            'enhanced_query': enhanced_query if enhance else None,
            'total_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        print(f"Error in voice search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/multi-image', methods=['POST'])
def search_multi_image():
    """
    Multi-image fusion search.
    Averages vectors from multiple images.

    Request: multipart/form-data with multiple 'images' files
    """
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400

        files = request.files.getlist('images')
        if len(files) == 0:
            return jsonify({'error': 'No images provided'}), 400

        if len(files) > 10:
            return jsonify({'error': 'Maximum 10 images allowed'}), 400

        top_k = int(request.form.get('top_k', config.DEFAULT_TOP_K))

        # Load and process all images
        images = []
        for file in files:
            if file.filename == '':
                continue
            image_bytes = file.read()
            image = load_image(image_bytes)
            image = resize_image(image)
            images.append(image)

        if len(images) == 0:
            return jsonify({'error': 'No valid images provided'}), 400

        # Encode all images
        image_vectors = clip_model.encode_image(images)

        # Average and normalize
        query_vector = np.mean(image_vectors, axis=0)
        query_vector = query_vector / np.linalg.norm(query_vector)

        # Search in FAISS
        retrieve_k = config.FAISS_RETRIEVE_K if config.ENABLE_RERANK else top_k
        results = faiss_index.search(query_vector, top_k=retrieve_k)

        # Rerank if enabled
        if config.ENABLE_RERANK and len(results) > top_k:
            results = rerank_results(results, f"[multi-image:{len(images)}]")[:top_k]

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'image_id': result['image_id'],
                'image_path': convert_image_path_to_url(result['image_path']),
                'score': round(result['score'] * 100, 2),
                'filename': result['metadata'].get('filename', ''),
                'metadata': result['metadata']
            })

        return jsonify({
            'success': True,
            'search_type': 'multi-image',
            'num_images': len(images),
            'total_results': len(formatted_results),
            'results': formatted_results
        })

    except Exception as e:
        print(f"Error in multi-image search: {str(e)}")
        return jsonify({'error': str(e)}), 500


def rerank_results(results, query):
    """
    Rerank results based on similarity score and user feedback.

    Args:
        results: List of search results
        query: Search query for tracking

    Returns:
        Reranked results
    """
    reranked = []
    for result in results:
        # Get feedback stats for this image
        feedback_stats = feedback_manager.get_feedback_stats(result['image_id'])

        # Calculate combined score
        combined_score = calculate_combined_score(
            result['score'],
            feedback_stats,
            alpha=0.8  # 80% similarity, 20% feedback
        )

        # Add to reranked list
        reranked.append({
            **result,
            'combined_score': combined_score,
            'feedback_stats': feedback_stats
        })

    # Sort by combined score
    reranked.sort(key=lambda x: x['combined_score'], reverse=True)

    return reranked


@search_bp.route('/feedback/record', methods=['POST'])
def record_feedback():
    """
    Record user feedback.

    Request body:
        {
            "query": "search query",
            "image_id": 123,
            "feedback_type": "like" | "favorite" | "irrelevant"
        }
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        image_id = data.get('image_id')
        feedback_type = data.get('feedback_type')

        if image_id is None:
            return jsonify({'error': 'image_id is required'}), 400

        if feedback_type not in ['like', 'favorite', 'irrelevant']:
            return jsonify({'error': 'Invalid feedback_type'}), 400

        # Record feedback
        success = feedback_manager.record_feedback(
            query=query,
            image_id=image_id,
            feedback_type=feedback_type
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Feedback recorded'
            })
        else:
            return jsonify({'error': 'Failed to record feedback'}), 500

    except Exception as e:
        print(f"Error recording feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/feedback/stats/<int:image_id>', methods=['GET'])
def get_feedback_stats_endpoint(image_id):
    """Get feedback statistics for an image."""
    try:
        stats = feedback_manager.get_feedback_stats(image_id)
        return jsonify({
            'success': True,
            'image_id': image_id,
            'stats': stats
        })

    except Exception as e:
        print(f"Error getting feedback stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/feedback/top-rated', methods=['GET'])
def get_top_rated():
    """Get top-rated images based on user feedback."""
    try:
        limit = int(request.args.get('limit', 20))
        top_rated = feedback_manager.get_top_rated_images(limit=limit)

        # Add image paths to the results
        metadata = faiss_index.metadata
        enriched_results = []

        for item in top_rated:
            image_id = item['image_id']
            # image_id in feedback is 1-based, but metadata index is 0-based
            metadata_index = image_id - 1

            if 0 <= metadata_index < len(metadata['image_paths']):
                image_path = metadata['image_paths'][metadata_index]
                image_url = convert_image_path_to_url(image_path)
                filename = os.path.basename(image_path)

                enriched_results.append({
                    **item,
                    'image_path': image_url,
                    'filename': filename
                })
            else:
                # If image not found in metadata, still include it
                enriched_results.append(item)

        return jsonify({
            'success': True,
            'total': len(enriched_results),
            'images': enriched_results
        })

    except Exception as e:
        print(f"Error getting top-rated images: {str(e)}")
        return jsonify({'error': str(e)}), 500
