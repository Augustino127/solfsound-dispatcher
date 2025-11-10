"""
SolfSound Dispatcher - Audio Extraction and Separation Tool

A powerful tool for extracting audio from videos and separating music into stems.
"""

__version__ = "1.0.0"
__author__ = "SolfSound Team"
__description__ = "Audio extraction and separation tool for videos and music"

from .extractor import VideoAudioExtractor
from .separator import AudioSeparator
from .analyzer import AudioAnalyzer

__all__ = ["VideoAudioExtractor", "AudioSeparator", "AudioAnalyzer"]
