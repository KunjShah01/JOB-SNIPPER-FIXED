"""
Utils package for JobSniper AI
Contains configuration, database, and utility functions
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
    'log_interaction'
]