"""
Audio Source Separation Module

Separates audio into different stems (vocals, drums, bass, other).
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union, List
import torch
from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import save_audio
import torchaudio

logger = logging.getLogger(__name__)


class AudioSeparator:
    """Separate audio into different stems using Demucs."""

    # Available stem types
    STEM_TYPES = ['vocals', 'drums', 'bass', 'other']

    # Available models
    MODELS = {
        'htdemucs': 'High-quality 4-stem separation (vocals, drums, bass, other)',
        'htdemucs_ft': 'Fine-tuned version for better quality',
        'htdemucs_6s': '6-stem separation (vocals, drums, bass, guitar, piano, other)',
        'mdx_extra': 'Extra high quality model (slower)',
    }

    def __init__(self, output_dir: str = "separated_stems", model_name: str = "htdemucs"):
        """
        Initialize the AudioSeparator.

        Args:
            output_dir: Directory where separated stems will be saved
            model_name: Name of the Demucs model to use
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name

        # Determine device (GPU if available)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Load model
        logger.info(f"Loading model: {model_name}")
        try:
            self.model = get_model(model_name)
            self.model.to(self.device)
            self.stems = self.model.sources
            logger.info(f"Model loaded successfully. Available stems: {self.stems}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def separate(
        self,
        audio_file: Union[str, Path],
        output_stems: Optional[List[str]] = None,
        output_format: str = "wav",
        shifts: int = 1,
        overlap: float = 0.25,
    ) -> dict[str, Path]:
        """
        Separate audio file into stems.

        Args:
            audio_file: Path to the input audio file
            output_stems: List of stems to extract (None = all stems)
            output_format: Output format for stems (wav, mp3, flac)
            shifts: Number of random shifts for better quality (1-10, higher = slower)
            overlap: Overlap between chunks (0.0-0.99)

        Returns:
            Dictionary mapping stem names to their file paths

        Raises:
            FileNotFoundError: If audio file doesn't exist
        """
        audio_path = Path(audio_file)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Validate output stems
        if output_stems is None:
            output_stems = self.stems
        else:
            invalid_stems = set(output_stems) - set(self.stems)
            if invalid_stems:
                raise ValueError(
                    f"Invalid stems: {invalid_stems}. "
                    f"Available stems for {self.model_name}: {self.stems}"
                )

        logger.info(f"Separating audio: {audio_path}")
        logger.info(f"Output stems: {output_stems}")

        try:
            # Load audio
            wav, sr = torchaudio.load(str(audio_path))
            wav = wav.to(self.device)

            # Ensure stereo
            if wav.shape[0] == 1:
                wav = wav.repeat(2, 1)
            elif wav.shape[0] > 2:
                wav = wav[:2, :]

            # Apply model
            logger.info("Applying separation model...")
            ref = wav.mean(0)
            wav = (wav - ref.mean()) / ref.std()

            sources = apply_model(
                self.model,
                wav[None],
                device=self.device,
                shifts=shifts,
                split=True,
                overlap=overlap,
                progress=True,
            )[0]

            sources = sources * ref.std() + ref.mean()

            # Save stems
            output_files = {}
            stem_dir = self.output_dir / audio_path.stem
            stem_dir.mkdir(parents=True, exist_ok=True)

            for i, stem_name in enumerate(self.stems):
                if stem_name in output_stems:
                    output_file = stem_dir / f"{stem_name}.{output_format}"

                    # Save audio
                    stem_audio = sources[i].cpu()
                    save_audio(
                        stem_audio,
                        str(output_file),
                        sr,
                        clip="rescale",
                        as_float=False,
                        bits_per_sample=16,
                    )

                    output_files[stem_name] = output_file
                    logger.info(f"Saved {stem_name} stem: {output_file}")

            logger.info(f"Separation complete! Stems saved to: {stem_dir}")
            return output_files

        except Exception as e:
            logger.error(f"Separation failed: {e}")
            raise RuntimeError(f"Failed to separate audio: {e}")

    def get_available_stems(self) -> List[str]:
        """Get list of available stems for the current model."""
        return self.stems

    def count_stems(self, audio_file: Union[str, Path]) -> int:
        """
        Count the number of separable stems in an audio file.

        Args:
            audio_file: Path to the audio file

        Returns:
            Number of stems that can be separated
        """
        return len(self.stems)

    @staticmethod
    def list_models() -> dict:
        """List all available separation models."""
        return AudioSeparator.MODELS
