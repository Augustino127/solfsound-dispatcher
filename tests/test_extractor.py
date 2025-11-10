"""
Unit tests for VideoAudioExtractor
"""

import pytest
from pathlib import Path
from solfsound.extractor import VideoAudioExtractor


class TestVideoAudioExtractor:
    """Test VideoAudioExtractor class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = VideoAudioExtractor(output_dir="test_output")

    def test_initialization(self):
        """Test extractor initialization."""
        assert self.extractor is not None
        assert self.extractor.output_dir.exists()

    def test_supported_formats(self):
        """Test supported format lists."""
        assert '.mp4' in self.extractor.SUPPORTED_VIDEO_FORMATS
        assert '.wav' in self.extractor.SUPPORTED_AUDIO_FORMATS

    def test_codec_mapping(self):
        """Test codec selection for formats."""
        assert self.extractor._get_codec_for_format('mp3') == 'libmp3lame'
        assert self.extractor._get_codec_for_format('wav') == 'pcm_s16le'
        assert self.extractor._get_codec_for_format('flac') == 'flac'

    def teardown_method(self):
        """Cleanup after tests."""
        import shutil
        if self.extractor.output_dir.exists():
            shutil.rmtree(self.extractor.output_dir)
