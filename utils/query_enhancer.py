import re


def enhance_query(query: str) -> str:
    """
    Enhance user query for better CLIP retrieval.

    Args:
        query: Raw user query

    Returns:
        Enhanced query string
    """
    # Basic cleaning
    query = query.strip()

    if not query:
        return query

    # Check if it's a simple query (1-2 words)
    words = query.split()

    # Don't enhance if it's already a complete sentence
    if len(words) > 5 or query.endswith('.') or query.endswith('?'):
        return query

    # Don't enhance if it starts with common prefixes
    prefixes = ['a photo of', 'an image of', 'a picture of', 'photo of', 'image of']
    query_lower = query.lower()
    if any(query_lower.startswith(prefix) for prefix in prefixes):
        return query

    # For simple queries, add "a photo of" prefix
    if len(words) <= 3:
        # Check if it contains Chinese characters
        if contains_chinese(query):
            # For Chinese queries, don't add prefix as CLIP handles it well
            return query
        else:
            return f"a photo of {query}"

    return query


def contains_chinese(text: str) -> bool:
    """
    Check if text contains Chinese characters.

    Args:
        text: Input text

    Returns:
        True if contains Chinese characters
    """
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def is_simple_query(query: str) -> bool:
    """
    Check if query is simple (1-2 words).

    Args:
        query: Query string

    Returns:
        True if simple query
    """
    return len(query.split()) <= 2
