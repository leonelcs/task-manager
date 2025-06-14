import os
from .base import BaseConfig
from .local import LocalConfig
from .production import ProductionConfig

def get_config() -> BaseConfig:
    """
    Factory function to get the appropriate configuration based on environment.
    
    Returns:
        BaseConfig: Configuration instance based on ENVIRONMENT variable
    """
    environment = os.getenv("ENVIRONMENT", "local").lower()
    
    config_mapping = {
        "local": LocalConfig,
        "development": LocalConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
        "gcp": ProductionConfig,
    }
    
    config_class = config_mapping.get(environment, LocalConfig)
    return config_class()

# Global config instance
config = get_config()
settings = config  # Alias for backward compatibility
