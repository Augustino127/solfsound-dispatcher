"""
Advanced Configuration System

Centralized configuration management with environment variables,
config files, and runtime overrides.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
import yaml

logger = logging.getLogger(__name__)


@dataclass
class PathsConfig:
    """Path configuration."""
    home_dir: Path = field(default_factory=lambda: Path.home() / '.solfsound')
    database_dir: Path = field(default_factory=lambda: Path.home() / '.solfsound')
    output_dir: Path = field(default_factory=lambda: Path('output'))
    upload_dir: Path = field(default_factory=lambda: Path('uploads'))
    cache_dir: Path = field(default_factory=lambda: Path.home() / '.solfsound' / 'cache')
    models_dir: Path = field(default_factory=lambda: Path.home() / '.solfsound' / 'models')
    temp_dir: Path = field(default_factory=lambda: Path('temp'))
    log_dir: Path = field(default_factory=lambda: Path('logs'))


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    default_model: str = 'htdemucs_ft'
    default_shifts: int = 1
    default_output_format: str = 'wav'
    default_bitrate: str = '320k'
    default_sample_rate: int = 48000
    max_file_size_mb: int = 500
    max_duration_seconds: int = 1800  # 30 minutes
    enable_gpu: bool = True
    num_workers: int = 4
    chunk_size: int = 1024 * 1024  # 1MB


@dataclass
class WebServerConfig:
    """Web server configuration."""
    host: str = '0.0.0.0'
    port: int = 8000
    reload: bool = False
    workers: int = 1
    cors_origins: list = field(default_factory=lambda: ['*'])
    max_upload_size_mb: int = 500
    enable_docs: bool = True
    api_prefix: str = '/api'
    session_secret: str = 'change-me-in-production'


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False
    auto_migrate: bool = True


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    backend: str = 'file'  # file, redis
    redis_url: Optional[str] = None
    ttl_seconds: int = 3600
    max_size_mb: int = 1000


@dataclass
class QueueConfig:
    """Queue configuration for batch processing."""
    enabled: bool = False
    backend: str = 'memory'  # memory, redis, celery
    redis_url: Optional[str] = None
    celery_broker: Optional[str] = None
    max_queue_size: int = 100
    max_retries: int = 3
    retry_delay_seconds: int = 60


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_auth: bool = False
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 60
    enable_api_keys: bool = False
    enable_file_scanning: bool = True
    allowed_file_types: list = field(default_factory=lambda: [
        'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm',
        'mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a', 'wma'
    ])


@dataclass
class FeaturesConfig:
    """Feature flags."""
    enable_analytics: bool = True
    enable_presets: bool = True
    enable_projects: bool = True
    enable_batch_processing: bool = True
    enable_audio_editing: bool = True
    enable_waveform_viz: bool = True
    enable_cloud_storage: bool = False
    enable_plugins: bool = True
    enable_export_multiple_formats: bool = True


@dataclass
class UIConfig:
    """UI configuration."""
    theme: str = 'dark'
    language: str = 'fr'
    show_tutorial: bool = True
    enable_notifications: bool = True
    auto_save: bool = True
    max_recent_files: int = 10


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration."""
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    max_log_file_size_mb: int = 10
    log_retention_days: int = 30
    enable_performance_tracking: bool = True
    enable_error_reporting: bool = True


@dataclass
class LimitsConfig:
    """Resource limits configuration."""
    free_tier_monthly_jobs: int = 100
    premium_tier_monthly_jobs: int = 1000
    enterprise_tier_monthly_jobs: int = -1  # Unlimited
    max_concurrent_jobs: int = 5
    max_batch_size: int = 50
    job_timeout_seconds: int = 3600  # 1 hour


class Config:
    """Main configuration class."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        self.paths = PathsConfig()
        self.processing = ProcessingConfig()
        self.web_server = WebServerConfig()
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.queue = QueueConfig()
        self.security = SecurityConfig()
        self.features = FeaturesConfig()
        self.ui = UIConfig()
        self.monitoring = MonitoringConfig()
        self.limits = LimitsConfig()

        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)

        # Load from environment variables
        self.load_from_env()

        # Create necessary directories
        self._create_directories()

        # Setup logging
        self._setup_logging()

        logger.info("Configuration initialized")

    def load_from_file(self, config_file: str):
        """Load configuration from JSON or YAML file."""
        config_path = Path(config_file)

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_file}")
            return

        try:
            with open(config_path, 'r') as f:
                if config_path.suffix == '.json':
                    data = json.load(f)
                elif config_path.suffix in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported config file format: {config_path.suffix}")
                    return

            self._update_from_dict(data)
            logger.info(f"Configuration loaded from: {config_file}")

        except Exception as e:
            logger.error(f"Error loading config file: {e}")

    def load_from_env(self):
        """Load configuration from environment variables."""
        # Processing
        if os.getenv('SOLFSOUND_DEFAULT_MODEL'):
            self.processing.default_model = os.getenv('SOLFSOUND_DEFAULT_MODEL')
        if os.getenv('SOLFSOUND_ENABLE_GPU'):
            self.processing.enable_gpu = os.getenv('SOLFSOUND_ENABLE_GPU').lower() == 'true'

        # Web Server
        if os.getenv('SOLFSOUND_HOST'):
            self.web_server.host = os.getenv('SOLFSOUND_HOST')
        if os.getenv('SOLFSOUND_PORT'):
            self.web_server.port = int(os.getenv('SOLFSOUND_PORT'))

        # Database
        if os.getenv('SOLFSOUND_DATABASE_URL'):
            self.database.url = os.getenv('SOLFSOUND_DATABASE_URL')

        # Cache
        if os.getenv('SOLFSOUND_REDIS_URL'):
            self.cache.redis_url = os.getenv('SOLFSOUND_REDIS_URL')
            self.cache.backend = 'redis'

        # Queue
        if os.getenv('SOLFSOUND_QUEUE_BACKEND'):
            self.queue.backend = os.getenv('SOLFSOUND_QUEUE_BACKEND')
            self.queue.enabled = True
        if os.getenv('SOLFSOUND_CELERY_BROKER'):
            self.queue.celery_broker = os.getenv('SOLFSOUND_CELERY_BROKER')

        # Security
        if os.getenv('SOLFSOUND_ENABLE_AUTH'):
            self.security.enable_auth = os.getenv('SOLFSOUND_ENABLE_AUTH').lower() == 'true'
        if os.getenv('SOLFSOUND_SESSION_SECRET'):
            self.web_server.session_secret = os.getenv('SOLFSOUND_SESSION_SECRET')

        # Monitoring
        if os.getenv('SOLFSOUND_LOG_LEVEL'):
            self.monitoring.log_level = os.getenv('SOLFSOUND_LOG_LEVEL')

    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for section_name, section_data in data.items():
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, value)

    def _create_directories(self):
        """Create necessary directories."""
        dirs_to_create = [
            self.paths.home_dir,
            self.paths.database_dir,
            self.paths.output_dir,
            self.paths.upload_dir,
            self.paths.cache_dir,
            self.paths.models_dir,
            self.paths.temp_dir,
            self.paths.log_dir,
        ]

        for directory in dirs_to_create:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.monitoring.log_level.upper())

        handlers = []

        if self.monitoring.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(logging.Formatter(self.monitoring.log_format))
            handlers.append(console_handler)

        if self.monitoring.enable_file_logging:
            log_file = self.paths.log_dir / 'solfsound.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(self.monitoring.log_format))
            handlers.append(file_handler)

        logging.basicConfig(
            level=log_level,
            handlers=handlers
        )

    def save_to_file(self, config_file: str, format: str = 'yaml'):
        """
        Save configuration to file.

        Args:
            config_file: Path to save configuration
            format: File format ('json' or 'yaml')
        """
        config_data = {
            'paths': asdict(self.paths),
            'processing': asdict(self.processing),
            'web_server': asdict(self.web_server),
            'database': asdict(self.database),
            'cache': asdict(self.cache),
            'queue': asdict(self.queue),
            'security': asdict(self.security),
            'features': asdict(self.features),
            'ui': asdict(self.ui),
            'monitoring': asdict(self.monitoring),
            'limits': asdict(self.limits),
        }

        # Convert Path objects to strings
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            return obj

        config_data = convert_paths(config_data)

        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, 'w') as f:
                if format == 'json':
                    json.dump(config_data, f, indent=2)
                elif format == 'yaml':
                    yaml.dump(config_data, f, default_flow_style=False)

            logger.info(f"Configuration saved to: {config_file}")

        except Exception as e:
            logger.error(f"Error saving config file: {e}")

    def get_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            'paths': asdict(self.paths),
            'processing': asdict(self.processing),
            'web_server': asdict(self.web_server),
            'database': asdict(self.database),
            'cache': asdict(self.cache),
            'queue': asdict(self.queue),
            'security': asdict(self.security),
            'features': asdict(self.features),
            'ui': asdict(self.ui),
            'monitoring': asdict(self.monitoring),
            'limits': asdict(self.limits),
        }


# Global configuration instance
_config = None


def get_config(config_file: Optional[str] = None) -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to find config file in default locations
        if config_file is None:
            default_locations = [
                'solfsound.yml',
                'solfsound.yaml',
                'solfsound.json',
                Path.home() / '.solfsound' / 'config.yml',
                Path.home() / '.solfsound' / 'config.yaml',
                '/etc/solfsound/config.yml',
            ]

            for location in default_locations:
                if Path(location).exists():
                    config_file = str(location)
                    break

        _config = Config(config_file)

    return _config
