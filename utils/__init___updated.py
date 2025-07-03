"""
Utils package for JobSniper AI
Contains configuration, database, JSON handling, and utility functions
"""

from .config import (
    load_config,
    validate_config,
    GEMINI_AVAILABLE,
    MISTRAL_AVAILABLE,
    EMAIL_AVAILABLE,
    AI_PROVIDER,
    FEATURES
)

from .sqlite_logger import (
    SQLiteLogger,
    init_db,
    save_to_db,
    get_history,
    get_resume_details,
    log_interaction
)

from .json_helper import (
    safe_json_loads,
    safe_json_dumps,
    extract_data_safely,
    normalize_agent_response
)

from .pdf_reader import (
    extract_text_from_pdf,
    validate_pdf,
    get_pdf_info
)

__all__ = [
    'load_config',
    'validate_config',
    'GEMINI_AVAILABLE',
    'MISTRAL_AVAILABLE', 
    'EMAIL_AVAILABLE',
    'AI_PROVIDER',
    'FEATURES',
    'SQLiteLogger',
    'init_db',
    'save_to_db',
    'get_history',
    'get_resume_details',
    'log_interaction',
    'safe_json_loads',
    'safe_json_dumps', 
    'extract_data_safely',
    'normalize_agent_response',
    'extract_text_from_pdf',
    'validate_pdf',
    'get_pdf_info'
]