"""
Desktop GUI Application for SolfSound Dispatcher

Cross-platform desktop application using Flet.
"""

import flet as ft
import logging
import threading
from pathlib import Path
from typing import Optional

from .extractor import VideoAudioExtractor
from .separator import AudioSeparator
from .analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)


class SolfSoundApp:
    """Main desktop application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "SolfSound Dispatcher"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 1000
        self.page.window_height = 800
        self.page.padding = 20

        # State
        self.uploaded_file = None
        self.current_action = None
        self.processing = False

        # Initialize components
        self.extractor = VideoAudioExtractor(output_dir="output/extracted")
        self.analyzer = AudioAnalyzer()

        # UI Components
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)

        self.progress_bar = ft.ProgressBar(visible=False, width=600)
        self.progress_text = ft.Text("", visible=False, size=16)

        # Build UI
        self.build_ui()

    def build_ui(self):
        """Build the main UI."""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "🎵 SolfSound Dispatcher",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Extraction et Séparation Audio Professionnelle",
                    size=18,
                    color=ft.colors.GREY_400,
                    text_align=ft.TextAlign.CENTER,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
        )

        # Upload Section
        self.upload_container = ft.Container(
            content=ft.Column([
                ft.Text("📁 Sélectionner un Fichier", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Choisir un fichier vidéo ou audio",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: self.file_picker.pick_files(
                        allowed_extensions=["mp4", "avi", "mov", "mkv", "wav", "mp3", "flac", "ogg"]
                    ),
                    style=ft.ButtonStyle(
                        padding=20,
                        text_style=ft.TextStyle(size=16),
                    ),
                ),
                ft.Container(height=10),
                self.create_file_info_container(),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            padding=30,
        )

        # Action Selection
        self.actions_container = ft.Container(
            content=ft.Column([
                ft.Text("⚙️ Choisir une Action", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Row([
                    self.create_action_button("🎬", "Extraire Audio", "extract"),
                    self.create_action_button("🎼", "Séparer en Stems", "separate"),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row([
                    self.create_action_button("📊", "Analyser", "analyze"),
                    self.create_action_button("🔄", "Pipeline Complet", "process"),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            padding=30,
            visible=False,
        )

        # Options Section
        self.options_container = ft.Container(
            content=ft.Column([
                ft.Text("🎛️ Options", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Column([], ref=ft.Ref[ft.Column]()),  # Dynamic options
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            padding=30,
            visible=False,
        )

        self.options_column = self.options_container.content.controls[2]

        # Process Button
        self.process_button = ft.ElevatedButton(
            "Lancer le Traitement",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.process_action,
            style=ft.ButtonStyle(
                padding=20,
                text_style=ft.TextStyle(size=18),
                bgcolor=ft.colors.PRIMARY,
            ),
            visible=False,
        )

        # Progress Section
        self.progress_container = ft.Container(
            content=ft.Column([
                ft.Text("⏳ Traitement en Cours", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                self.progress_bar,
                ft.Container(height=10),
                self.progress_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            padding=30,
            visible=False,
        )

        # Results Section
        self.results_container = ft.Container(
            content=ft.Column([
                ft.Text("✅ Résultats", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Column([], ref=ft.Ref[ft.Column]()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=15,
            padding=30,
            visible=False,
        )

        self.results_column = self.results_container.content.controls[2]

        # Main Layout
        main_content = ft.Column([
            header,
            self.upload_container,
            self.actions_container,
            self.options_container,
            ft.Container(
                content=self.process_button,
                alignment=ft.alignment.center,
            ),
            self.progress_container,
            self.results_container,
        ], scroll=ft.ScrollMode.AUTO)

        self.page.add(main_content)

    def create_file_info_container(self):
        """Create file info container."""
        self.file_info_text = ft.Text("", size=14, color=ft.colors.GREEN_400)
        return ft.Container(
            content=self.file_info_text,
            visible=False,
        )

    def create_action_button(self, icon, text, action):
        """Create an action button."""
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=40),
                ft.Text(text, size=16, weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=200,
            height=120,
            bgcolor=ft.colors.SURFACE,
            border_radius=10,
            padding=20,
            ink=True,
            on_click=lambda _: self.select_action(action),
        )

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """Handle file selection."""
        if e.files:
            self.uploaded_file = e.files[0].path
            file_name = Path(self.uploaded_file).name
            file_size = Path(self.uploaded_file).stat().st_size / (1024 * 1024)

            self.file_info_text.value = f"✅ Fichier: {file_name} ({file_size:.2f} MB)"
            self.file_info_text.parent.visible = True
            self.actions_container.visible = True

            self.page.update()

    def select_action(self, action):
        """Select an action and show options."""
        self.current_action = action
        self.show_options(action)

    def show_options(self, action):
        """Show options for selected action."""
        self.options_column.controls.clear()

        if action == "extract":
            self.options_column.controls.extend([
                ft.Dropdown(
                    label="Format de sortie",
                    value="wav",
                    options=[
                        ft.dropdown.Option("wav", "WAV (Haute qualité)"),
                        ft.dropdown.Option("mp3", "MP3"),
                        ft.dropdown.Option("flac", "FLAC"),
                        ft.dropdown.Option("ogg", "OGG"),
                    ],
                    width=400,
                    ref=ft.Ref[ft.Dropdown](),
                ),
                ft.Dropdown(
                    label="Bitrate",
                    value="320k",
                    options=[
                        ft.dropdown.Option("320k", "320 kbps (Très haute)"),
                        ft.dropdown.Option("256k", "256 kbps (Haute)"),
                        ft.dropdown.Option("192k", "192 kbps (Moyenne)"),
                    ],
                    width=400,
                    ref=ft.Ref[ft.Dropdown](),
                ),
            ])
            self.extract_format_dd = self.options_column.controls[0]
            self.extract_bitrate_dd = self.options_column.controls[1]

        elif action == "separate":
            self.options_column.controls.extend([
                ft.Dropdown(
                    label="Modèle de séparation",
                    value="htdemucs",
                    options=[
                        ft.dropdown.Option("htdemucs", "HTDemucs (Rapide)"),
                        ft.dropdown.Option("htdemucs_ft", "HTDemucs Fine-Tuned"),
                        ft.dropdown.Option("htdemucs_6s", "HTDemucs 6-stems"),
                    ],
                    width=400,
                    ref=ft.Ref[ft.Dropdown](),
                ),
                ft.Text("Stems à extraire:", size=16),
                ft.Row([
                    ft.Checkbox(label="🎤 Voix", value=True, ref=ft.Ref[ft.Checkbox]()),
                    ft.Checkbox(label="🥁 Batterie", value=True, ref=ft.Ref[ft.Checkbox]()),
                ]),
                ft.Row([
                    ft.Checkbox(label="🎸 Basse", value=True, ref=ft.Ref[ft.Checkbox]()),
                    ft.Checkbox(label="🎹 Autres", value=True, ref=ft.Ref[ft.Checkbox]()),
                ]),
                ft.Dropdown(
                    label="Qualité (shifts)",
                    value="1",
                    options=[
                        ft.dropdown.Option("1", "1 (Rapide)"),
                        ft.dropdown.Option("3", "3 (Équilibré)"),
                        ft.dropdown.Option("5", "5 (Haute qualité)"),
                    ],
                    width=400,
                    ref=ft.Ref[ft.Dropdown](),
                ),
            ])
            self.separate_model_dd = self.options_column.controls[0]
            self.vocals_cb = self.options_column.controls[2].controls[0]
            self.drums_cb = self.options_column.controls[2].controls[1]
            self.bass_cb = self.options_column.controls[3].controls[0]
            self.other_cb = self.options_column.controls[3].controls[1]
            self.shifts_dd = self.options_column.controls[4]

        elif action == "analyze":
            self.options_column.controls.append(
                ft.Text(
                    "L'analyse fournira des informations détaillées sur la composition audio.",
                    size=14,
                    color=ft.colors.GREY_400,
                )
            )

        elif action == "process":
            self.options_column.controls.extend([
                ft.Dropdown(
                    label="Modèle de séparation",
                    value="htdemucs_ft",
                    options=[
                        ft.dropdown.Option("htdemucs", "HTDemucs (Rapide)"),
                        ft.dropdown.Option("htdemucs_ft", "HTDemucs Fine-Tuned"),
                    ],
                    width=400,
                    ref=ft.Ref[ft.Dropdown](),
                ),
                ft.Text(
                    "Pipeline complet: Extraction → Séparation → Analyse",
                    size=14,
                    color=ft.colors.GREY_400,
                ),
            ])
            self.process_model_dd = self.options_column.controls[0]

        self.options_container.visible = True
        self.process_button.visible = True
        self.page.update()

    def process_action(self, e):
        """Process the selected action."""
        if self.processing:
            return

        self.processing = True
        self.show_progress("Initialisation...", 0)

        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._process_thread)
        thread.start()

    def _process_thread(self):
        """Processing thread."""
        try:
            if self.current_action == "extract":
                self._extract_audio()
            elif self.current_action == "separate":
                self._separate_audio()
            elif self.current_action == "analyze":
                self._analyze_audio()
            elif self.current_action == "process":
                self._process_complete()
        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.show_error(str(e))
        finally:
            self.processing = False
            self.hide_progress()

    def _extract_audio(self):
        """Extract audio."""
        format_val = self.extract_format_dd.current.value
        bitrate = self.extract_bitrate_dd.current.value

        self.update_progress("Extraction de l'audio...", 50)

        output_file = self.extractor.extract_audio(
            self.uploaded_file,
            output_format=format_val,
            bitrate=bitrate
        )

        info = self.extractor.get_audio_info(output_file)
        self.show_results_extract(output_file, info)

    def _separate_audio(self):
        """Separate audio."""
        model = self.separate_model_dd.current.value
        shifts = int(self.shifts_dd.current.value)

        stems = []
        if self.vocals_cb.current.value:
            stems.append("vocals")
        if self.drums_cb.current.value:
            stems.append("drums")
        if self.bass_cb.current.value:
            stems.append("bass")
        if self.other_cb.current.value:
            stems.append("other")

        self.update_progress("Chargement du modèle...", 20)

        separator = AudioSeparator(output_dir="output/stems", model_name=model)

        self.update_progress("Séparation en cours...", 50)

        output_files = separator.separate(
            self.uploaded_file,
            output_stems=stems if stems else None,
            output_format="wav",
            shifts=shifts
        )

        self.show_results_separate(output_files)

    def _analyze_audio(self):
        """Analyze audio."""
        self.update_progress("Analyse en cours...", 50)

        analysis = self.analyzer.analyze_audio(self.uploaded_file)

        self.show_results_analyze(analysis)

    def _process_complete(self):
        """Complete processing pipeline."""
        model = self.process_model_dd.current.value

        # Extract if video
        self.update_progress("Extraction...", 10)
        file_path = Path(self.uploaded_file)
        if file_path.suffix.lower() in VideoAudioExtractor.SUPPORTED_VIDEO_FORMATS:
            audio_file = self.extractor.extract_audio(file_path, output_format='wav')
        else:
            audio_file = file_path

        # Separate
        self.update_progress("Séparation...", 40)
        separator = AudioSeparator(output_dir="output/stems", model_name=model)
        stem_files = separator.separate(audio_file, output_format='wav')

        # Analyze
        self.update_progress("Analyse...", 80)
        analysis = self.analyzer.analyze_audio(audio_file)
        stem_comparison = self.analyzer.compare_stems(stem_files)

        self.show_results_process(audio_file, stem_files, analysis, stem_comparison)

    def show_progress(self, message, progress):
        """Show progress."""
        self.progress_container.visible = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.update_progress(message, progress)

    def update_progress(self, message, progress):
        """Update progress."""
        self.progress_text.value = message
        self.progress_bar.value = progress / 100
        self.page.update()

    def hide_progress(self):
        """Hide progress."""
        self.progress_container.visible = False
        self.page.update()

    def show_error(self, message):
        """Show error."""
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Erreur: {message}"), bgcolor=ft.colors.RED)
        self.page.snack_bar.open = True
        self.page.update()

    def show_results_extract(self, output_file, info):
        """Show extraction results."""
        self.results_column.controls.clear()
        self.results_column.controls.extend([
            ft.Text("✅ Audio Extrait avec Succès", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Fichier: {output_file}"),
            ft.Text(f"Durée: {info['duration']:.2f}s"),
            ft.Text(f"Format: {info['format']}"),
            ft.ElevatedButton("Ouvrir le dossier", on_click=lambda _: self.open_folder(output_file)),
        ])
        self.results_container.visible = True
        self.page.update()

    def show_results_separate(self, output_files):
        """Show separation results."""
        self.results_column.controls.clear()
        self.results_column.controls.append(
            ft.Text("✅ Séparation Terminée", size=20, weight=ft.FontWeight.BOLD)
        )

        for stem, path in output_files.items():
            self.results_column.controls.append(
                ft.Text(f"🎵 {stem}: {path}")
            )

        self.results_column.controls.append(
            ft.ElevatedButton("Ouvrir le dossier", on_click=lambda _: self.open_folder(list(output_files.values())[0]))
        )

        self.results_container.visible = True
        self.page.update()

    def show_results_analyze(self, analysis):
        """Show analysis results."""
        self.results_column.controls.clear()
        self.results_column.controls.extend([
            ft.Text("📊 Analyse Audio", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Durée: {analysis['duration']:.1f}s"),
            ft.Text(f"Tempo: {analysis['rhythm']['tempo']:.0f} BPM"),
            ft.Text(f"Couches Sonores: {analysis['complexity']['estimated_sound_layers']}"),
            ft.Text(f"Ratio Harmonique: {analysis['harmony']['harmonic_ratio']*100:.1f}%"),
            ft.Text(f"Ratio Percussif: {analysis['harmony']['percussive_ratio']*100:.1f}%"),
        ])

        self.results_container.visible = True
        self.page.update()

    def show_results_process(self, audio_file, stem_files, analysis, stem_comparison):
        """Show complete processing results."""
        self.results_column.controls.clear()
        self.results_column.controls.extend([
            ft.Text("✅ Traitement Complet Terminé", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("\n🎼 Stems:", size=18),
        ])

        for stem, path in stem_files.items():
            pct = stem_comparison['stems'][stem]['percentage']
            self.results_column.controls.append(
                ft.Text(f"  {stem}: {pct:.1f}%")
            )

        self.results_column.controls.extend([
            ft.Text(f"\n📊 Analyse:", size=18),
            ft.Text(f"Tempo: {analysis['rhythm']['tempo']:.0f} BPM"),
            ft.Text(f"Couches Sonores: {analysis['complexity']['estimated_sound_layers']}"),
            ft.Text(f"Stem Dominant: {stem_comparison['dominant_stem']}"),
            ft.ElevatedButton("Ouvrir le dossier", on_click=lambda _: self.open_folder(audio_file)),
        ])

        self.results_container.visible = True
        self.page.update()

    def open_folder(self, file_path):
        """Open folder containing file."""
        import os
        import subprocess
        import platform

        folder = Path(file_path).parent

        if platform.system() == 'Windows':
            os.startfile(folder)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', folder])
        else:  # Linux
            subprocess.Popen(['xdg-open', folder])


def main():
    """Main entry point for desktop app."""
    ft.app(target=SolfSoundApp)


if __name__ == "__main__":
    main()
