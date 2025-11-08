"""
Utils package for AI Chat Portal
Provides helper functions and utilities
"""

from .helpers import (
    # String utilities
    sanitize_input,
    truncate_text,
    extract_keywords,
    count_tokens_estimate,
    
    # Hash & ID utilities
    generate_unique_id,
    generate_short_id,
    hash_text,
    generate_share_token,
    
    # Date/time utilities
    get_time_difference,
    get_date_range,
    is_today,
    is_this_week,
    is_this_month,
    
    # Validation
    validate_email,
    validate_conversation_title,
    validate_message_content,
    
    # Data processing
    paginate_list,
    filter_dict,
    merge_dicts,
    flatten_dict,
    group_by,
    
    # JSON utilities
    safe_json_dumps,
    safe_json_loads,
    
    # Performance
    measure_execution_time,
    retry,
    
    # Statistics
    calculate_average,
    calculate_median,
    calculate_standard_deviation,
    get_percentile,
    
    # Error handling
    log_error,
    safe_call,
    
    # Response formatting
    format_success_response,
    format_error_response,
)

__all__ = [
    'sanitize_input',
    'truncate_text',
    'extract_keywords',
    'count_tokens_estimate',
    'generate_unique_id',
    'generate_short_id',
    'hash_text',
    'generate_share_token',
    'get_time_difference',
    'get_date_range',
    'is_today',
    'is_this_week',
    'is_this_month',
    'validate_email',
    'validate_conversation_title',
    'validate_message_content',
    'paginate_list',
    'filter_dict',
    'merge_dicts',
    'flatten_dict',
    'group_by',
    'safe_json_dumps',
    'safe_json_loads',
    'measure_execution_time',
    'retry',
    'calculate_average',
    'calculate_median',
    'calculate_standard_deviation',
    'get_percentile',
    'log_error',
    'safe_call',
    'format_success_response',
    'format_error_response',
]
