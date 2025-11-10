"""
Audio Analysis Module

Analyzes audio files to extract information about composition and structure.
"""

import logging
from pathlib import Path
from typing import Union, Dict, List
import numpy as np
import librosa
import librosa.display
from scipy import signal

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyze audio files for composition and structure."""

    def __init__(self):
        """Initialize the AudioAnalyzer."""
        pass

    def analyze_audio(self, audio_file: Union[str, Path]) -> Dict:
        """
        Perform comprehensive analysis of an audio file.

        Args:
            audio_file: Path to the audio file

        Returns:
            Dictionary containing analysis results

        Raises:
            FileNotFoundError: If audio file doesn't exist
        """
        audio_path = Path(audio_file)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        logger.info(f"Analyzing audio: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            analysis = {
                'file': str(audio_path),
                'duration': float(len(y) / sr),
                'sample_rate': sr,
                'basic': self._analyze_basic_properties(y, sr),
                'spectral': self._analyze_spectral_features(y, sr),
                'rhythm': self._analyze_rhythm(y, sr),
                'harmony': self._analyze_harmony(y, sr),
                'complexity': self._estimate_complexity(y, sr),
            }

            logger.info("Analysis complete")
            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise RuntimeError(f"Failed to analyze audio: {e}")

    def _analyze_basic_properties(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze basic audio properties."""
        try:
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]

            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]

            return {
                'rms_mean': float(np.mean(rms)),
                'rms_std': float(np.std(rms)),
                'rms_max': float(np.max(rms)),
                'zero_crossing_rate': float(np.mean(zcr)),
                'loudness_db': float(librosa.amplitude_to_db(np.abs(y)).mean()),
            }
        except Exception as e:
            logger.warning(f"Failed to analyze basic properties: {e}")
            return {}

    def _analyze_spectral_features(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze spectral features."""
        try:
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]

            # Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

            # MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)

            return {
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'spectral_contrast_mean': float(np.mean(spectral_contrast)),
                'mfcc_mean': [float(x) for x in np.mean(mfcc, axis=1)],
                'chroma_mean': [float(x) for x in np.mean(chroma, axis=1)],
            }
        except Exception as e:
            logger.warning(f"Failed to analyze spectral features: {e}")
            return {}

    def _analyze_rhythm(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze rhythm and tempo."""
        try:
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

            # Onset detection
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

            return {
                'tempo': float(tempo),
                'beat_count': len(beats),
                'onset_count': len(onsets),
                'rhythmic_density': float(len(onsets) / (len(y) / sr)),  # onsets per second
            }
        except Exception as e:
            logger.warning(f"Failed to analyze rhythm: {e}")
            return {}

    def _analyze_harmony(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze harmonic content."""
        try:
            # Harmonic-percussive source separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Harmonic ratio (harmonic energy / total energy)
            harmonic_ratio = np.sum(y_harmonic ** 2) / (np.sum(y ** 2) + 1e-10)

            # Percussive ratio
            percussive_ratio = np.sum(y_percussive ** 2) / (np.sum(y ** 2) + 1e-10)

            # Chroma energy normalized statistics
            chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr)

            return {
                'harmonic_ratio': float(harmonic_ratio),
                'percussive_ratio': float(percussive_ratio),
                'chroma_cens_mean': float(np.mean(chroma_cens)),
                'chroma_cens_std': float(np.std(chroma_cens)),
            }
        except Exception as e:
            logger.warning(f"Failed to analyze harmony: {e}")
            return {}

    def _estimate_complexity(self, y: np.ndarray, sr: int) -> Dict:
        """
        Estimate the complexity of the audio.

        Attempts to estimate how many "layers" or components might be present.
        """
        try:
            # Spectral complexity (entropy)
            S = np.abs(librosa.stft(y))
            spectral_entropy = signal.entropy(S.mean(axis=1))

            # Temporal complexity
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            temporal_entropy = signal.entropy(onset_env + 1e-10)

            # Harmonic-percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Estimate instrument/source count based on spectral peaks
            S = np.abs(librosa.stft(y_harmonic))
            freqs = librosa.fft_frequencies(sr=sr)

            # Find prominent frequency bands
            S_mean = S.mean(axis=1)
            peaks, _ = signal.find_peaks(S_mean, height=np.max(S_mean) * 0.1)

            # Rough estimation of source count
            # This is a heuristic - actual source separation would be needed for accurate count
            estimated_sources = min(len(peaks) // 3, 10)  # Cap at 10

            return {
                'spectral_entropy': float(spectral_entropy),
                'temporal_entropy': float(temporal_entropy),
                'estimated_sound_layers': int(estimated_sources),
                'complexity_score': float((spectral_entropy + temporal_entropy) / 2),
                'note': 'Sound layer estimation is approximate. Use separation for accurate count.'
            }
        except Exception as e:
            logger.warning(f"Failed to estimate complexity: {e}")
            return {}

    def compare_stems(self, stem_files: Dict[str, Path]) -> Dict:
        """
        Compare energy distribution across different stems.

        Args:
            stem_files: Dictionary mapping stem names to file paths

        Returns:
            Dictionary with comparison results
        """
        try:
            stem_energies = {}

            for stem_name, stem_path in stem_files.items():
                y, sr = librosa.load(str(stem_path), sr=None)
                energy = float(np.sum(y ** 2))
                rms = float(np.sqrt(np.mean(y ** 2)))
                stem_energies[stem_name] = {
                    'energy': energy,
                    'rms': rms,
                }

            # Calculate percentages
            total_energy = sum(s['energy'] for s in stem_energies.values())

            for stem_name in stem_energies:
                stem_energies[stem_name]['percentage'] = (
                    stem_energies[stem_name]['energy'] / total_energy * 100
                    if total_energy > 0 else 0
                )

            return {
                'stems': stem_energies,
                'total_stems': len(stem_files),
                'dominant_stem': max(
                    stem_energies.items(),
                    key=lambda x: x[1]['energy']
                )[0] if stem_energies else None,
            }
        except Exception as e:
            logger.error(f"Failed to compare stems: {e}")
            raise RuntimeError(f"Failed to compare stems: {e}")

    def get_audio_summary(self, audio_file: Union[str, Path]) -> str:
        """
        Get a human-readable summary of the audio analysis.

        Args:
            audio_file: Path to the audio file

        Returns:
            Human-readable summary string
        """
        analysis = self.analyze_audio(audio_file)

        summary_parts = [
            f"Audio Analysis Summary for: {Path(audio_file).name}",
            f"Duration: {analysis['duration']:.2f} seconds",
            f"",
            "Basic Properties:",
            f"  - Loudness: {analysis['basic'].get('loudness_db', 0):.2f} dB",
            f"  - RMS Energy: {analysis['basic'].get('rms_mean', 0):.4f}",
            f"",
            "Rhythm:",
            f"  - Tempo: {analysis['rhythm'].get('tempo', 0):.1f} BPM",
            f"  - Beats: {analysis['rhythm'].get('beat_count', 0)}",
            f"  - Onsets: {analysis['rhythm'].get('onset_count', 0)}",
            f"",
            "Composition Estimate:",
            f"  - Estimated Sound Layers: {analysis['complexity'].get('estimated_sound_layers', 0)}",
            f"  - Harmonic Ratio: {analysis['harmony'].get('harmonic_ratio', 0):.2%}",
            f"  - Percussive Ratio: {analysis['harmony'].get('percussive_ratio', 0):.2%}",
            f"  - Complexity Score: {analysis['complexity'].get('complexity_score', 0):.2f}",
        ]

        return "\n".join(summary_parts)
