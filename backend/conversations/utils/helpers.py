"""
Helper Functions for AI Chat Portal
Provides common utility functions and data processing helpers
Used throughout the application for data manipulation, validation, and formatting
"""

import logging
import json
import hashlib
import uuid
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from functools import wraps
import time

logger = logging.getLogger(__name__)


# ==================== STRING UTILITIES ====================

def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input
    Removes dangerous characters and limits length
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text
    Simple word extraction (can be enhanced with NLP)
    
    Args:
        text: Input text
        min_length: Minimum keyword length
    
    Returns:
        List of keywords
    """
    # Common stopwords to exclude
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where'
    }
    
    words = text.lower().split()
    keywords = [
        word.strip('.,!?;:') for word in words
        if len(word) >= min_length and word.lower() not in stopwords
    ]
    
    return list(set(keywords))  # Remove duplicates


def count_tokens_estimate(text: str) -> int:
    """
    Estimate token count (simple calculation)
    More accurate methods require tokenizer libraries
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    # Simple estimation: ~1 token per 4 characters
    return max(1, len(text) // 4)


# ==================== HASH & ID UTILITIES ====================

def generate_unique_id() -> str:
    """
    Generate unique ID
    
    Returns:
        Unique ID string
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate short unique ID
    
    Args:
        length: Length of ID
    
    Returns:
        Short unique ID
    """
    return str(uuid.uuid4())[:length]


def hash_text(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash text using specified algorithm
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (sha256, md5, etc.)
    
    Returns:
        Hashed text
    """
    if algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    else:
        return hashlib.sha256(text.encode()).hexdigest()


def generate_share_token(length: int = 32) -> str:
    """
    Generate share token for public conversations
    
    Args:
        length: Token length
    
    Returns:
        Random share token
    """
    return uuid.uuid4().hex[:length]


# ==================== DATE/TIME UTILITIES ====================

def get_time_difference(dt1: datetime, dt2: datetime) -> str:
    """
    Get human-readable time difference
    
    Args:
        dt1: First datetime
        dt2: Second datetime
    
    Returns:
        Time difference string (e.g., "2 hours ago")
    """
    if not dt1 or not dt2:
        return "Unknown"
    
    diff = abs((dt1 - dt2).total_seconds())
    
    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = int(diff // 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff < 604800:
        days = int(diff // 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        weeks = int(diff // 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"


def get_date_range(days: int = 7) -> Tuple[datetime, datetime]:
    """
    Get date range for specified number of days
    
    Args:
        days: Number of days
    
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def is_today(dt: datetime) -> bool:
    """Check if datetime is today"""
    if not dt:
        return False
    return dt.date() == datetime.now().date()


def is_this_week(dt: datetime) -> bool:
    """Check if datetime is this week"""
    if not dt:
        return False
    now = datetime.now()
    start_week = now - timedelta(days=now.weekday())
    return dt >= start_week


def is_this_month(dt: datetime) -> bool:
    """Check if datetime is this month"""
    if not dt:
        return False
    now = datetime.now()
    return dt.month == now.month and dt.year == now.year


# ==================== DATA VALIDATION ====================

def validate_email(email: str) -> bool:
    """
    Validate email address (simple check)
    
    Args:
        email: Email address
    
    Returns:
        True if valid, False otherwise
    """
    if not email or '@' not in email:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain or '.' not in domain:
        return False
    
    return True


def validate_conversation_title(title: str) -> Tuple[bool, Optional[str]]:
    """
    Validate conversation title
    
    Args:
        title: Conversation title
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not isinstance(title, str):
        return False, "Title must be a non-empty string"
    
    if len(title) < 3:
        return False, "Title must be at least 3 characters"
    
    if len(title) > 255:
        return False, "Title must not exceed 255 characters"
    
    return True, None


def validate_message_content(content: str, max_length: int = 2000) -> Tuple[bool, Optional[str]]:
    """
    Validate message content
    
    Args:
        content: Message content
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or not isinstance(content, str):
        return False, "Content must be a non-empty string"
    
    if len(content.strip()) == 0:
        return False, "Content cannot be empty or whitespace only"
    
    if len(content) > max_length:
        return False, f"Content must not exceed {max_length} characters"
    
    return True, None


# ==================== DATA PROCESSING ====================

def paginate_list(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list
    
    Args:
        items: List of items
        page: Page number (1-indexed)
        page_size: Items per page
    
    Returns:
        Dictionary with pagination data
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    # Validate page
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        'items': items[start_idx:end_idx],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1
    }


def filter_dict(
    data: Dict[str, Any],
    allowed_keys: List[str]
) -> Dict[str, Any]:
    """
    Filter dictionary to only include allowed keys
    
    Args:
        data: Input dictionary
        allowed_keys: Keys to include
    
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in allowed_keys}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries
    Later dictionaries override earlier ones
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = '',
    sep: str = '_'
) -> Dict[str, Any]:
    """
    Flatten nested dictionary
    
    Args:
        d: Input dictionary
        parent_key: Parent key prefix
        sep: Separator character
    
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def group_by(items: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group list of dictionaries by key
    
    Args:
        items: List of dictionaries
        key: Key to group by
    
    Returns:
        Dictionary with grouped items
    """
    groups = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups


# ==================== JSON UTILITIES ====================

def safe_json_dumps(obj: Any, default=None) -> str:
    """
    Safely convert object to JSON string
    
    Args:
        obj: Object to serialize
        default: Default handler for non-serializable objects
    
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=default or str)
    except Exception as e:
        logger.error(f'JSON serialization error: {str(e)}')
        return '{}'


def safe_json_loads(json_str: str, default=None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string
        default: Default value if parsing fails
    
    Returns:
        Parsed object or default value
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f'JSON parsing error: {str(e)}')
        return default or {}


# ==================== PERFORMANCE UTILITIES ====================

def measure_execution_time(func):
    """
    Decorator to measure function execution time
    
    Args:
        func: Function to measure
    
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f'{func.__name__} executed in {elapsed:.4f}s')
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: int = 1):
    """
    Decorator for retrying function with exponential backoff
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay in seconds
    
    Returns:
        Decorator
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f'{func.__name__} failed after {max_attempts} attempts')
                        raise
                    
                    logger.warning(f'{func.__name__} attempt {attempt} failed, retrying in {current_delay}s')
                    time.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff
                    attempt += 1
        
        return wrapper
    return decorator


# ==================== STATISTICS ====================

def calculate_average(values: List[float]) -> float:
    """Calculate average of list"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_median(values: List[float]) -> float:
    """Calculate median of list"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    return float(sorted_values[n//2])


def calculate_standard_deviation(values: List[float]) -> float:
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0.0
    avg = calculate_average(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance ** 0.5


def get_percentile(values: List[float], percentile: int) -> float:
    """Calculate percentile of list"""
    if not values or not (0 <= percentile <= 100):
        return 0.0
    sorted_values = sorted(values)
    index = int((percentile / 100) * len(sorted_values))
    return float(sorted_values[min(index, len(sorted_values) - 1)])


# ==================== ERROR HANDLING ====================

def log_error(
    error: Exception,
    context: str = '',
    extra_data: Dict[str, Any] = None
):
    """
    Log error with context
    
    Args:
        error: Exception object
        context: Error context
        extra_data: Additional data to log
    """
    error_msg = f'{context}: {str(error)}' if context else str(error)
    logger.error(error_msg, extra={'data': extra_data})


def safe_call(
    func,
    default=None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    Safely call function with error handling
    
    Args:
        func: Function to call
        default: Default return value if error occurs
        log_error: Whether to log errors
        **kwargs: Function arguments
    
    Returns:
        Function result or default value
    """
    try:
        return func(**kwargs)
    except Exception as e:
        if log_error:
            logger.error(f'Error in {func.__name__}: {str(e)}')
        return default


# ==================== RESPONSE FORMATTING ====================

def format_success_response(
    data: Any = None,
    message: str = 'Success',
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Format success response
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Formatted response dictionary
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code
    }


def format_error_response(
    error: str,
    message: str = 'An error occurred',
    status_code: int = 400,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Format error response
    
    Args:
        error: Error type
        message: Error message
        status_code: HTTP status code
        details: Additional error details
    
    Returns:
        Formatted error response dictionary
    """
    return {
        'success': False,
        'error': error,
        'message': message,
        'status_code': status_code,
        'details': details or {}
    }
