"""
Internationalization (i18n) Support

Multi-language support system.
"""

import logging
from typing import Dict, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class I18n:
    """Internationalization manager."""

    def __init__(self, locale: str = 'fr', locales_dir: Optional[Path] = None):
        """
        Initialize i18n.

        Args:
            locale: Default locale (e.g., 'fr', 'en')
            locales_dir: Directory containing locale files
        """
        if locales_dir is None:
            locales_dir = Path(__file__).parent / 'locales'

        self.locales_dir = Path(locales_dir)
        self.current_locale = locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_locale = 'en'

        # Load translations
        self._load_locale(self.fallback_locale)
        if locale != self.fallback_locale:
            self._load_locale(locale)

    def _load_locale(self, locale: str):
        """Load translations for a locale."""
        locale_file = self.locales_dir / f"{locale}.json"

        if not locale_file.exists():
            logger.warning(f"Locale file not found: {locale_file}")
            return

        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations[locale] = json.load(f)

            logger.info(f"Loaded locale: {locale}")

        except Exception as e:
            logger.error(f"Error loading locale {locale}: {e}")

    def t(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key.

        Args:
            key: Translation key
            locale: Locale (None = use current)
            **kwargs: Format parameters

        Returns:
            Translated string
        """
        if locale is None:
            locale = self.current_locale

        # Try current locale
        translation = self.translations.get(locale, {}).get(key)

        # Fallback to default locale
        if not translation:
            translation = self.translations.get(self.fallback_locale, {}).get(key, key)

        # Format
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except Exception as e:
                logger.warning(f"Error formatting translation: {e}")

        return translation

    def set_locale(self, locale: str):
        """Set current locale."""
        if locale not in self.translations:
            self._load_locale(locale)

        self.current_locale = locale
        logger.info(f"Locale set to: {locale}")


# Default translations
DEFAULT_TRANSLATIONS = {
    'en': {
        'app.title': 'SolfSound Dispatcher',
        'app.subtitle': 'Professional Audio Extraction and Separation',
        'upload.title': 'Upload File',
        'upload.hint': 'Click or drag a file here',
        'upload.supported': 'Video or Audio (MP4, AVI, WAV, MP3, etc.)',
        'action.extract': 'Extract Audio',
        'action.separate': 'Separate Stems',
        'action.analyze': 'Analyze',
        'action.process': 'Complete Pipeline',
        'processing.extracting': 'Extracting audio...',
        'processing.separating': 'Separating stems...',
        'processing.analyzing': 'Analyzing audio...',
        'result.success': 'Processing completed successfully!',
        'result.failed': 'Processing failed: {error}',
    },
    'fr': {
        'app.title': 'SolfSound Dispatcher',
        'app.subtitle': 'Extraction et Séparation Audio Professionnelle',
        'upload.title': 'Télécharger un Fichier',
        'upload.hint': 'Cliquez ou glissez un fichier ici',
        'upload.supported': 'Vidéo ou Audio (MP4, AVI, WAV, MP3, etc.)',
        'action.extract': 'Extraire Audio',
        'action.separate': 'Séparer en Stems',
        'action.analyze': 'Analyser',
        'action.process': 'Pipeline Complet',
        'processing.extracting': 'Extraction de l\'audio...',
        'processing.separating': 'Séparation en cours...',
        'processing.analyzing': 'Analyse en cours...',
        'result.success': 'Traitement terminé avec succès !',
        'result.failed': 'Traitement échoué : {error}',
    }
}


# Global i18n instance
_i18n = None


def get_i18n(locale: str = 'fr') -> I18n:
    """Get global i18n instance."""
    global _i18n
    if _i18n is None:
        _i18n = I18n(locale)

        # Load default translations if no files exist
        if not _i18n.translations:
            _i18n.translations = DEFAULT_TRANSLATIONS

    return _i18n


# Shortcut function
def t(key: str, **kwargs) -> str:
    """Translate shortcut."""
    return get_i18n().t(key, **kwargs)
