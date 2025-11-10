"""
Advanced Audio Editing Module

Provides audio manipulation features: trim, fade, normalize, merge, effects.
"""

import logging
from pathlib import Path
from typing import Union, Tuple, Optional, List
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import librosa
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioEditor:
    """Advanced audio editing capabilities."""

    def __init__(self, output_dir: str = "edited_audio"):
        """
        Initialize the AudioEditor.

        Args:
            output_dir: Directory where edited audio files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def trim(
        self,
        input_file: Union[str, Path],
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Trim audio file to specified time range.

        Args:
            input_file: Path to input audio file
            start_time: Start time in seconds
            end_time: End time in seconds (None = end of file)
            output_file: Path to output file (None = auto-generate)
            output_format: Output format

        Returns:
            Path to trimmed audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_trimmed.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Trimming audio: {input_path} from {start_time}s to {end_time}s")

        try:
            # Load audio
            audio = AudioSegment.from_file(str(input_path))

            # Convert times to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000) if end_time is not None else len(audio)

            # Trim
            trimmed = audio[start_ms:end_ms]

            # Export
            trimmed.export(str(output_file), format=output_format)

            logger.info(f"Trimmed audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error trimming audio: {e}")
            raise

    def fade(
        self,
        input_file: Union[str, Path],
        fade_in_duration: float = 0.0,
        fade_out_duration: float = 0.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Apply fade in/out effects to audio.

        Args:
            input_file: Path to input audio file
            fade_in_duration: Fade in duration in seconds
            fade_out_duration: Fade out duration in seconds
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to faded audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_faded.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Applying fade to audio: {input_path}")

        try:
            audio = AudioSegment.from_file(str(input_path))

            # Apply fades
            if fade_in_duration > 0:
                fade_in_ms = int(fade_in_duration * 1000)
                audio = audio.fade_in(fade_in_ms)

            if fade_out_duration > 0:
                fade_out_ms = int(fade_out_duration * 1000)
                audio = audio.fade_out(fade_out_ms)

            audio.export(str(output_file), format=output_format)

            logger.info(f"Faded audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error applying fade: {e}")
            raise

    def normalize_audio(
        self,
        input_file: Union[str, Path],
        target_dBFS: float = -20.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Normalize audio to target loudness.

        Args:
            input_file: Path to input audio file
            target_dBFS: Target loudness in dBFS
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to normalized audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_normalized.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Normalizing audio: {input_path} to {target_dBFS} dBFS")

        try:
            audio = AudioSegment.from_file(str(input_path))

            # Normalize
            change_in_dBFS = target_dBFS - audio.dBFS
            normalized = audio.apply_gain(change_in_dBFS)

            normalized.export(str(output_file), format=output_format)

            logger.info(f"Normalized audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            raise

    def merge(
        self,
        input_files: List[Union[str, Path]],
        crossfade_duration: float = 0.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Merge multiple audio files into one.

        Args:
            input_files: List of input audio file paths
            crossfade_duration: Crossfade duration in seconds
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to merged audio file
        """
        if output_file is None:
            output_file = self.output_dir / f"merged.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Merging {len(input_files)} audio files")

        try:
            merged = None

            for file_path in input_files:
                audio = AudioSegment.from_file(str(file_path))

                if merged is None:
                    merged = audio
                else:
                    if crossfade_duration > 0:
                        crossfade_ms = int(crossfade_duration * 1000)
                        merged = merged.append(audio, crossfade=crossfade_ms)
                    else:
                        merged = merged + audio

            if merged:
                merged.export(str(output_file), format=output_format)
                logger.info(f"Merged audio saved: {output_file}")
                return output_file
            else:
                raise ValueError("No audio to merge")

        except Exception as e:
            logger.error(f"Error merging audio: {e}")
            raise

    def mix(
        self,
        input_files: List[Union[str, Path]],
        volumes: Optional[List[float]] = None,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Mix multiple audio files (overlay).

        Args:
            input_files: List of input audio file paths
            volumes: List of volume multipliers (0.0-1.0) for each track
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to mixed audio file
        """
        if output_file is None:
            output_file = self.output_dir / f"mixed.{output_format}"
        else:
            output_file = Path(output_file)

        if volumes and len(volumes) != len(input_files):
            raise ValueError("Number of volumes must match number of input files")

        logger.info(f"Mixing {len(input_files)} audio files")

        try:
            mixed = None

            for i, file_path in enumerate(input_files):
                audio = AudioSegment.from_file(str(file_path))

                # Apply volume
                if volumes:
                    volume_dB = 20 * np.log10(volumes[i]) if volumes[i] > 0 else -60
                    audio = audio + volume_dB

                if mixed is None:
                    mixed = audio
                else:
                    mixed = mixed.overlay(audio)

            if mixed:
                mixed.export(str(output_file), format=output_format)
                logger.info(f"Mixed audio saved: {output_file}")
                return output_file
            else:
                raise ValueError("No audio to mix")

        except Exception as e:
            logger.error(f"Error mixing audio: {e}")
            raise

    def change_speed(
        self,
        input_file: Union[str, Path],
        speed_factor: float = 1.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Change audio playback speed.

        Args:
            input_file: Path to input audio file
            speed_factor: Speed multiplier (0.5 = half speed, 2.0 = double speed)
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to speed-changed audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_speed{speed_factor:.1f}x.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Changing speed of audio: {input_path} by {speed_factor}x")

        try:
            # Load with librosa
            y, sr = librosa.load(str(input_path), sr=None)

            # Time stretch
            y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)

            # Save
            sf.write(str(output_file), y_stretched, sr)

            logger.info(f"Speed-changed audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error changing speed: {e}")
            raise

    def change_pitch(
        self,
        input_file: Union[str, Path],
        semitones: float = 0.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Change audio pitch.

        Args:
            input_file: Path to input audio file
            semitones: Number of semitones to shift (+/-)
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to pitch-shifted audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_pitch{semitones:+.1f}.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Changing pitch of audio: {input_path} by {semitones} semitones")

        try:
            # Load with librosa
            y, sr = librosa.load(str(input_path), sr=None)

            # Pitch shift
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)

            # Save
            sf.write(str(output_file), y_shifted, sr)

            logger.info(f"Pitch-shifted audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error changing pitch: {e}")
            raise

    def apply_reverb(
        self,
        input_file: Union[str, Path],
        room_scale: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Apply reverb effect to audio.

        Args:
            input_file: Path to input audio file
            room_scale: Room size (0.0-1.0)
            damping: Damping factor (0.0-1.0)
            wet_level: Wet signal level (0.0-1.0)
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to reverb-applied audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_reverb.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Applying reverb to audio: {input_path}")

        try:
            # Simple reverb simulation using delay and feedback
            audio = AudioSegment.from_file(str(input_path))

            # Create a simple reverb effect
            # This is a simplified version - for production use a proper reverb library
            delay_ms = int(room_scale * 100)  # 0-100ms delay based on room size
            wet = audio - (wet_level * 10)  # Reduce volume of wet signal

            # Apply multiple delays for reverb effect
            reverb = audio
            for i in range(1, 5):
                delay = delay_ms * i
                decay = (1 - damping) ** i * wet_level * 10
                delayed = audio - decay
                reverb = reverb.overlay(delayed, position=delay)

            # Mix with original
            mixed = audio.overlay(reverb - 6)  # Reduce reverb volume

            mixed.export(str(output_file), format=output_format)

            logger.info(f"Reverb-applied audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error applying reverb: {e}")
            raise

    def compress(
        self,
        input_file: Union[str, Path],
        threshold: float = -20.0,
        ratio: float = 4.0,
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> Path:
        """
        Apply dynamic range compression.

        Args:
            input_file: Path to input audio file
            threshold: Threshold in dBFS
            ratio: Compression ratio
            output_file: Path to output file
            output_format: Output format

        Returns:
            Path to compressed audio file
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = self.output_dir / f"{input_path.stem}_compressed.{output_format}"
        else:
            output_file = Path(output_file)

        logger.info(f"Compressing audio: {input_path}")

        try:
            audio = AudioSegment.from_file(str(input_path))

            # Apply compression
            compressed = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)

            compressed.export(str(output_file), format=output_format)

            logger.info(f"Compressed audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error compressing audio: {e}")
            raise

    def convert_format(
        self,
        input_file: Union[str, Path],
        output_formats: List[str],
        bitrate: str = "320k",
        sample_rate: Optional[int] = None
    ) -> List[Path]:
        """
        Convert audio to multiple formats simultaneously.

        Args:
            input_file: Path to input audio file
            output_formats: List of output formats (e.g., ['mp3', 'wav', 'flac'])
            bitrate: Bitrate for compressed formats
            sample_rate: Sample rate (None = keep original)

        Returns:
            List of paths to converted audio files
        """
        input_path = Path(input_file)

        logger.info(f"Converting audio to {len(output_formats)} formats: {input_path}")

        output_files = []

        try:
            audio = AudioSegment.from_file(str(input_path))

            # Change sample rate if specified
            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)

            for fmt in output_formats:
                output_file = self.output_dir / f"{input_path.stem}.{fmt}"

                # Export with appropriate parameters
                export_params = {'format': fmt}

                if fmt in ['mp3', 'ogg', 'aac']:
                    export_params['bitrate'] = bitrate

                audio.export(str(output_file), **export_params)
                output_files.append(output_file)
                logger.info(f"Converted to {fmt}: {output_file}")

            logger.info(f"Conversion complete: {len(output_files)} files created")
            return output_files

        except Exception as e:
            logger.error(f"Error converting formats: {e}")
            raise

    def extract_segment(
        self,
        input_file: Union[str, Path],
        segments: List[Tuple[float, float]],
        output_dir: Optional[Union[str, Path]] = None,
        output_format: str = "wav"
    ) -> List[Path]:
        """
        Extract multiple segments from audio file.

        Args:
            input_file: Path to input audio file
            segments: List of (start_time, end_time) tuples in seconds
            output_dir: Directory for output files
            output_format: Output format

        Returns:
            List of paths to extracted segments
        """
        input_path = Path(input_file)

        if output_dir is None:
            output_dir = self.output_dir / f"{input_path.stem}_segments"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting {len(segments)} segments from: {input_path}")

        output_files = []

        try:
            audio = AudioSegment.from_file(str(input_path))

            for i, (start_time, end_time) in enumerate(segments, 1):
                start_ms = int(start_time * 1000)
                end_ms = int(end_time * 1000)

                segment = audio[start_ms:end_ms]

                output_file = output_dir / f"segment_{i:03d}.{output_format}"
                segment.export(str(output_file), format=output_format)

                output_files.append(output_file)
                logger.info(f"Extracted segment {i}: {start_time}s - {end_time}s")

            logger.info(f"Segment extraction complete: {len(output_files)} segments")
            return output_files

        except Exception as e:
            logger.error(f"Error extracting segments: {e}")
            raise
