"""
Database Models and Management

SQLAlchemy models for project history, user data, and configuration.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model for authentication and preferences."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    api_key = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Preferences
    preferences = Column(JSON, default=dict)
    theme = Column(String(50), default='dark')
    language = Column(String(10), default='fr')

    # Quota and limits
    is_premium = Column(Boolean, default=False)
    monthly_quota = Column(Integer, default=100)  # Number of processing jobs
    used_quota = Column(Integer, default=0)

    # Relationships
    projects = relationship('Project', back_populates='user', cascade='all, delete-orphan')
    jobs = relationship('ProcessingJob', back_populates='user', cascade='all, delete-orphan')
    presets = relationship('Preset', back_populates='user', cascade='all, delete-orphan')


class Project(Base):
    """Project model for organizing related audio files."""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Project settings
    settings = Column(JSON, default=dict)
    tags = Column(JSON, default=list)

    # Statistics
    total_files = Column(Integer, default=0)
    total_size = Column(Float, default=0.0)  # In MB

    # Relationships
    user = relationship('User', back_populates='projects')
    jobs = relationship('ProcessingJob', back_populates='project', cascade='all, delete-orphan')
    audio_files = relationship('AudioFile', back_populates='project', cascade='all, delete-orphan')


class AudioFile(Base):
    """Audio file metadata."""
    __tablename__ = 'audio_files'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # File information
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_type = Column(String(50))  # video, audio
    format = Column(String(50))  # mp4, wav, mp3, etc.
    size = Column(Float)  # In MB

    # Audio metadata
    duration = Column(Float)
    sample_rate = Column(Integer)
    channels = Column(Integer)
    bitrate = Column(Integer)

    # Additional metadata
    metadata = Column(JSON, default=dict)  # Artist, title, album, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    imported_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship('Project', back_populates='audio_files')
    jobs = relationship('ProcessingJob', back_populates='source_file')


class ProcessingJob(Base):
    """Processing job tracking."""
    __tablename__ = 'processing_jobs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    source_file_id = Column(Integer, ForeignKey('audio_files.id'), nullable=True)

    # Job information
    job_type = Column(String(50), nullable=False)  # extract, separate, analyze, process
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    progress = Column(Integer, default=0)

    # Processing parameters
    parameters = Column(JSON, default=dict)
    preset_id = Column(Integer, ForeignKey('presets.id'), nullable=True)

    # Results
    output_files = Column(JSON, default=list)
    analysis_results = Column(JSON, default=dict)

    # Performance metrics
    processing_time = Column(Float)  # In seconds
    cpu_usage = Column(Float)
    memory_usage = Column(Float)

    # Error handling
    error_message = Column(Text)
    error_traceback = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship('User', back_populates='jobs')
    project = relationship('Project', back_populates='jobs')
    source_file = relationship('AudioFile', back_populates='jobs')
    preset = relationship('Preset')


class Preset(Base):
    """Saved presets for common workflows."""
    __tablename__ = 'presets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Preset information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # extraction, separation, analysis, custom

    # Settings
    job_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=False)

    # Metadata
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # Built-in presets
    usage_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='presets')


class AnalyticsEvent(Base):
    """Analytics and usage tracking."""
    __tablename__ = 'analytics_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Event information
    event_type = Column(String(100), nullable=False)  # page_view, job_started, etc.
    event_data = Column(JSON, default=dict)

    # Context
    session_id = Column(String(255))
    user_agent = Column(String(500))
    ip_address = Column(String(50))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemMetrics(Base):
    """System performance metrics."""
    __tablename__ = 'system_metrics'

    id = Column(Integer, primary_key=True)

    # Metrics
    metric_type = Column(String(100), nullable=False)  # cpu, memory, disk, queue_size
    value = Column(Float, nullable=False)

    # Additional data
    metadata = Column(JSON, default=dict)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database management class."""

    def __init__(self, db_url: str = None):
        """
        Initialize database manager.

        Args:
            db_url: Database URL (defaults to SQLite in app directory)
        """
        if db_url is None:
            db_path = Path.home() / '.solfsound' / 'solfsound.db'
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f'sqlite:///{db_path}'

        self.engine = create_engine(
            db_url,
            connect_args={'check_same_thread': False} if 'sqlite' in db_url else {},
            poolclass=StaticPool if 'sqlite' in db_url else None
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

        # Initialize default data
        self._init_defaults()

        logger.info(f"Database initialized: {db_url}")

    def _init_defaults(self):
        """Initialize default presets and system data."""
        session = self.get_session()

        try:
            # Check if system presets exist
            if session.query(Preset).filter_by(is_system=True).count() == 0:
                # Create default system presets
                default_presets = [
                    {
                        'name': 'Extraction Haute Qualité',
                        'description': 'Extraction audio en WAV haute qualité',
                        'category': 'extraction',
                        'job_type': 'extract',
                        'is_system': True,
                        'parameters': {
                            'output_format': 'wav',
                            'bitrate': '320k',
                            'sample_rate': 48000
                        }
                    },
                    {
                        'name': 'Extraction MP3 Standard',
                        'description': 'Extraction audio en MP3 320kbps',
                        'category': 'extraction',
                        'job_type': 'extract',
                        'is_system': True,
                        'parameters': {
                            'output_format': 'mp3',
                            'bitrate': '320k'
                        }
                    },
                    {
                        'name': 'Séparation Rapide',
                        'description': 'Séparation rapide avec HTDemucs',
                        'category': 'separation',
                        'job_type': 'separate',
                        'is_system': True,
                        'parameters': {
                            'model': 'htdemucs',
                            'shifts': 1,
                            'output_format': 'wav'
                        }
                    },
                    {
                        'name': 'Séparation Haute Qualité',
                        'description': 'Séparation haute qualité avec HTDemucs Fine-Tuned',
                        'category': 'separation',
                        'job_type': 'separate',
                        'is_system': True,
                        'parameters': {
                            'model': 'htdemucs_ft',
                            'shifts': 5,
                            'output_format': 'wav'
                        }
                    },
                    {
                        'name': 'Extraction Voix Seule',
                        'description': 'Extraire uniquement la voix',
                        'category': 'separation',
                        'job_type': 'separate',
                        'is_system': True,
                        'parameters': {
                            'model': 'htdemucs_ft',
                            'stems': ['vocals'],
                            'shifts': 3,
                            'output_format': 'wav'
                        }
                    },
                    {
                        'name': 'Version Karaoké',
                        'description': 'Extraire tout sauf la voix',
                        'category': 'separation',
                        'job_type': 'separate',
                        'is_system': True,
                        'parameters': {
                            'model': 'htdemucs_ft',
                            'stems': ['drums', 'bass', 'other'],
                            'shifts': 3,
                            'output_format': 'wav'
                        }
                    },
                ]

                for preset_data in default_presets:
                    preset = Preset(**preset_data)
                    session.add(preset)

                session.commit()
                logger.info("Default presets created")

        except Exception as e:
            logger.error(f"Error initializing defaults: {e}")
            session.rollback()
        finally:
            session.close()

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_user(self, username: str, email: str, **kwargs) -> User:
        """Create a new user."""
        session = self.get_session()
        try:
            user = User(username=username, email=email, **kwargs)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def get_user(self, user_id: int = None, username: str = None, email: str = None) -> Optional[User]:
        """Get user by ID, username, or email."""
        session = self.get_session()
        try:
            query = session.query(User)
            if user_id:
                return query.filter_by(id=user_id).first()
            elif username:
                return query.filter_by(username=username).first()
            elif email:
                return query.filter_by(email=email).first()
            return None
        finally:
            session.close()

    def create_project(self, name: str, user_id: int = None, **kwargs) -> Project:
        """Create a new project."""
        session = self.get_session()
        try:
            project = Project(name=name, user_id=user_id, **kwargs)
            session.add(project)
            session.commit()
            session.refresh(project)
            return project
        finally:
            session.close()

    def get_projects(self, user_id: int = None) -> List[Project]:
        """Get all projects for a user."""
        session = self.get_session()
        try:
            query = session.query(Project)
            if user_id:
                query = query.filter_by(user_id=user_id)
            return query.order_by(Project.updated_at.desc()).all()
        finally:
            session.close()

    def create_job(self, job_type: str, **kwargs) -> ProcessingJob:
        """Create a new processing job."""
        session = self.get_session()
        try:
            job = ProcessingJob(job_type=job_type, **kwargs)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        finally:
            session.close()

    def update_job(self, job_id: int, **kwargs) -> Optional[ProcessingJob]:
        """Update a processing job."""
        session = self.get_session()
        try:
            job = session.query(ProcessingJob).filter_by(id=job_id).first()
            if job:
                for key, value in kwargs.items():
                    setattr(job, key, value)
                session.commit()
                session.refresh(job)
            return job
        finally:
            session.close()

    def get_job(self, job_id: int) -> Optional[ProcessingJob]:
        """Get a job by ID."""
        session = self.get_session()
        try:
            return session.query(ProcessingJob).filter_by(id=job_id).first()
        finally:
            session.close()

    def get_jobs(self, user_id: int = None, project_id: int = None, status: str = None) -> List[ProcessingJob]:
        """Get jobs with optional filters."""
        session = self.get_session()
        try:
            query = session.query(ProcessingJob)
            if user_id:
                query = query.filter_by(user_id=user_id)
            if project_id:
                query = query.filter_by(project_id=project_id)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(ProcessingJob.created_at.desc()).all()
        finally:
            session.close()

    def get_presets(self, user_id: int = None, category: str = None, include_system: bool = True) -> List[Preset]:
        """Get presets with optional filters."""
        session = self.get_session()
        try:
            query = session.query(Preset)

            if include_system:
                if user_id:
                    query = query.filter(
                        (Preset.user_id == user_id) | (Preset.is_system == True)
                    )
                else:
                    query = query.filter_by(is_system=True)
            else:
                query = query.filter_by(user_id=user_id)

            if category:
                query = query.filter_by(category=category)

            return query.order_by(Preset.name).all()
        finally:
            session.close()

    def create_preset(self, name: str, job_type: str, parameters: dict, **kwargs) -> Preset:
        """Create a new preset."""
        session = self.get_session()
        try:
            preset = Preset(name=name, job_type=job_type, parameters=parameters, **kwargs)
            session.add(preset)
            session.commit()
            session.refresh(preset)
            return preset
        finally:
            session.close()

    def track_event(self, event_type: str, event_data: dict = None, user_id: int = None, **kwargs):
        """Track an analytics event."""
        session = self.get_session()
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                event_data=event_data or {},
                user_id=user_id,
                **kwargs
            )
            session.add(event)
            session.commit()
        finally:
            session.close()

    def record_metric(self, metric_type: str, value: float, metadata: dict = None):
        """Record a system metric."""
        session = self.get_session()
        try:
            metric = SystemMetrics(
                metric_type=metric_type,
                value=value,
                metadata=metadata or {}
            )
            session.add(metric)
            session.commit()
        finally:
            session.close()

    def get_statistics(self, user_id: int = None) -> dict:
        """Get usage statistics."""
        session = self.get_session()
        try:
            stats = {
                'total_jobs': session.query(ProcessingJob).count(),
                'completed_jobs': session.query(ProcessingJob).filter_by(status='completed').count(),
                'failed_jobs': session.query(ProcessingJob).filter_by(status='failed').count(),
                'total_projects': session.query(Project).count(),
                'total_presets': session.query(Preset).filter_by(is_system=False).count(),
            }

            if user_id:
                stats['user_jobs'] = session.query(ProcessingJob).filter_by(user_id=user_id).count()
                stats['user_projects'] = session.query(Project).filter_by(user_id=user_id).count()
                stats['user_presets'] = session.query(Preset).filter_by(user_id=user_id).count()

            return stats
        finally:
            session.close()


# Global database manager instance
_db_manager = None


def get_db() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
