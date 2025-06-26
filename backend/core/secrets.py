"""
Utility module for handling Docker secrets and environment variables.
"""
import os
import pathlib
import structlog

logger = structlog.get_logger()

def read_secret_or_env(secret_path_env: str, fallback_env: str, default: str = None) -> str:
    """
    Read from Docker secret file if available, otherwise from environment variable.
    
    Args:
        secret_path_env: Environment variable containing path to secret file
        fallback_env: Environment variable to fall back to
        default: Default value if neither is available
    
    Returns:
        The secret/environment value
        
    Raises:
        ValueError: If neither secret nor environment variable is available
    """
    secret_path = os.getenv(secret_path_env)
    if secret_path and pathlib.Path(secret_path).exists():
        logger.info(f"Reading secret from {secret_path}")
        return pathlib.Path(secret_path).read_text().strip()
    
    value = os.getenv(fallback_env, default)
    if value:
        logger.info(f"Using environment variable {fallback_env}")
        return value
    
    if default is not None:
        logger.info(f"Using default value for {fallback_env}")
        return default
    
    raise ValueError(f"Neither secret file ({secret_path_env}) nor environment variable ({fallback_env}) is available")

def get_database_config() -> dict:
    """Get database configuration with secret support."""
    return {
        'user': os.getenv("POSTGRES_USER"),
        'password': read_secret_or_env("POSTGRES_PASSWORD_FILE", "POSTGRES_PASSWORD"),
        'host': os.getenv("POSTGRES_HOST"),
        'port': os.getenv("POSTGRES_PORT"),
        'database': os.getenv("POSTGRES_DB")
    }

def get_gemini_api_key() -> str:
    """Get Gemini API key with secret support."""
    return read_secret_or_env("GEMINI_API_KEY_FILE", "GEMINI_API_KEY")