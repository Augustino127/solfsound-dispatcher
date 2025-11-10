"""
Video to Audio Extraction Module

Extracts audio from video files in various formats.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union
import ffmpeg
from pydub import AudioSegment
from pydub.utils import mediainfo

logger = logging.getLogger(__name__)


class VideoAudioExtractor:
    """Extract audio from video files."""

    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v']
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac']

    def __init__(self, output_dir: str = "extracted_audio"):
        """
        Initialize the VideoAudioExtractor.

        Args:
            output_dir: Directory where extracted audio files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_audio(
        self,
        input_file: Union[str, Path],
        output_format: str = "wav",
        output_filename: Optional[str] = None,
        bitrate: str = "320k",
        sample_rate: Optional[int] = None
    ) -> Path:
        """
        Extract audio from a video file.

        Args:
            input_file: Path to the input video or audio file
            output_format: Output audio format (mp3, wav, flac, etc.)
            output_filename: Custom output filename (without extension)
            bitrate: Audio bitrate for compressed formats (e.g., "320k")
            sample_rate: Sample rate in Hz (e.g., 44100, 48000)

        Returns:
            Path to the extracted audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If format is not supported
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Determine if input is video or audio
        file_ext = input_path.suffix.lower()
        is_video = file_ext in self.SUPPORTED_VIDEO_FORMATS
        is_audio = file_ext in self.SUPPORTED_AUDIO_FORMATS

        if not (is_video or is_audio):
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {self.SUPPORTED_VIDEO_FORMATS + self.SUPPORTED_AUDIO_FORMATS}"
            )

        # Generate output filename
        if output_filename is None:
            output_filename = input_path.stem

        output_path = self.output_dir / f"{output_filename}.{output_format}"

        logger.info(f"Extracting audio from: {input_path}")
        logger.info(f"Output file: {output_path}")

        try:
            # Use ffmpeg for extraction
            stream = ffmpeg.input(str(input_path))

            # Configure output options
            output_options = {
                'acodec': self._get_codec_for_format(output_format),
                'audio_bitrate': bitrate,
            }

            if sample_rate:
                output_options['ar'] = sample_rate

            # Extract audio
            stream = ffmpeg.output(stream, str(output_path), **output_options)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            logger.info(f"Audio extracted successfully: {output_path}")
            return output_path

        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg error: {error_msg}")
            raise RuntimeError(f"Failed to extract audio: {error_msg}")

    def get_audio_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about an audio or video file.

        Args:
            file_path: Path to the audio or video file

        Returns:
            Dictionary containing audio information
        """
        try:
            probe = ffmpeg.probe(str(file_path))

            # Find audio stream
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )

            if not audio_stream:
                raise ValueError("No audio stream found in file")

            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'format': probe['format'].get('format_name', 'unknown'),
                'bit_rate': int(probe['format'].get('bit_rate', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
                'codec': audio_stream.get('codec_name', 'unknown'),
            }

            return info

        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Failed to get audio info: {error_msg}")

    def _get_codec_for_format(self, format: str) -> str:
        """Get the appropriate codec for the output format."""
        codec_map = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'flac': 'flac',
            'ogg': 'libvorbis',
            'aac': 'aac',
            'm4a': 'aac',
        }
        return codec_map.get(format.lower(), 'libmp3lame')

    def batch_extract(
        self,
        input_files: list[Union[str, Path]],
        output_format: str = "wav",
        **kwargs
    ) -> list[Path]:
        """
        Extract audio from multiple video files.

        Args:
            input_files: List of input video file paths
            output_format: Output audio format
            **kwargs: Additional arguments passed to extract_audio

        Returns:
            List of paths to extracted audio files
        """
        output_files = []

        for input_file in input_files:
            try:
                output_file = self.extract_audio(
                    input_file,
                    output_format=output_format,
                    **kwargs
                )
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"Failed to extract audio from {input_file}: {e}")

        return output_files
