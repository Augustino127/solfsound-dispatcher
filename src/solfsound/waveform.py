"""
Audio Waveform Visualization

Generate waveform images and data for audio visualization.
"""

import logging
from pathlib import Path
from typing import Union, Tuple, Optional
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


class WaveformGenerator:
    """Generate waveform visualizations."""

    def __init__(self, output_dir: str = "waveforms"):
        """
        Initialize waveform generator.

        Args:
            output_dir: Directory for waveform images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_waveform(
        self,
        audio_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        width: int = 1200,
        height: int = 300,
        color: str = '#6366f1',
        background: str = '#0f172a'
    ) -> Path:
        """
        Generate waveform image.

        Args:
            audio_file: Path to audio file
            output_file: Path to output image
            width: Image width in pixels
            height: Image height in pixels
            color: Waveform color (hex)
            background: Background color (hex)

        Returns:
            Path to generated waveform image
        """
        audio_path = Path(audio_file)

        if output_file is None:
            output_file = self.output_dir / f"{audio_path.stem}_waveform.png"
        else:
            output_file = Path(output_file)

        logger.info(f"Generating waveform for: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Create figure
            fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
            fig.patch.set_facecolor(background)
            ax.set_facecolor(background)

            # Plot waveform
            librosa.display.waveshow(y, sr=sr, ax=ax, color=color)

            # Style
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            # Save
            plt.tight_layout(pad=0)
            plt.savefig(
                str(output_file),
                facecolor=background,
                edgecolor='none',
                bbox_inches='tight',
                pad_inches=0
            )
            plt.close()

            logger.info(f"Waveform saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error generating waveform: {e}")
            raise

    def generate_spectrogram(
        self,
        audio_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        width: int = 1200,
        height: int = 300,
        colormap: str = 'viridis'
    ) -> Path:
        """
        Generate spectrogram image.

        Args:
            audio_file: Path to audio file
            output_file: Path to output image
            width: Image width in pixels
            height: Image height in pixels
            colormap: Matplotlib colormap name

        Returns:
            Path to generated spectrogram image
        """
        audio_path = Path(audio_file)

        if output_file is None:
            output_file = self.output_dir / f"{audio_path.stem}_spectrogram.png"
        else:
            output_file = Path(output_file)

        logger.info(f"Generating spectrogram for: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Create spectrogram
            D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

            # Create figure
            fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)

            # Plot spectrogram
            img = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=ax, cmap=colormap)

            # Style
            ax.set_xlabel('Time (s)', color='white')
            ax.set_ylabel('Frequency (Hz)', color='white')
            ax.tick_params(colors='white')

            # Colorbar
            cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
            cbar.ax.tick_params(colors='white')

            # Save
            plt.tight_layout()
            plt.savefig(str(output_file), facecolor='#0f172a', edgecolor='none')
            plt.close()

            logger.info(f"Spectrogram saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error generating spectrogram: {e}")
            raise

    def get_waveform_data(
        self,
        audio_file: Union[str, Path],
        num_points: int = 1000
    ) -> dict:
        """
        Get waveform data for programmatic use.

        Args:
            audio_file: Path to audio file
            num_points: Number of data points to return

        Returns:
            Dictionary with waveform data
        """
        audio_path = Path(audio_file)

        logger.info(f"Extracting waveform data for: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Downsample to num_points
            if len(y) > num_points:
                step = len(y) // num_points
                y_downsampled = y[::step][:num_points]
            else:
                y_downsampled = y

            # Time axis
            duration = len(y) / sr
            times = np.linspace(0, duration, len(y_downsampled))

            return {
                'waveform': y_downsampled.tolist(),
                'times': times.tolist(),
                'sample_rate': sr,
                'duration': duration,
                'num_samples': len(y),
            }

        except Exception as e:
            logger.error(f"Error extracting waveform data: {e}")
            raise

    def generate_waveform_base64(
        self,
        audio_file: Union[str, Path],
        width: int = 1200,
        height: int = 300
    ) -> str:
        """
        Generate waveform as base64-encoded PNG (for web use).

        Args:
            audio_file: Path to audio file
            width: Image width
            height: Image height

        Returns:
            Base64-encoded PNG string
        """
        try:
            # Generate to temp file
            temp_file = self.output_dir / "temp_waveform.png"
            self.generate_waveform(audio_file, temp_file, width, height)

            # Read and encode
            with open(temp_file, 'rb') as f:
                img_data = f.read()

            # Clean up
            temp_file.unlink()

            # Encode to base64
            base64_str = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{base64_str}"

        except Exception as e:
            logger.error(f"Error generating base64 waveform: {e}")
            raise
