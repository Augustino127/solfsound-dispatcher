"""
Command-Line Interface for SolfSound Dispatcher

Provides user-friendly commands for audio extraction, separation, and analysis.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .extractor import VideoAudioExtractor
from .separator import AudioSeparator
from .analyzer import AudioAnalyzer

console = Console()


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('solfsound.log'),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler(),
        ]
    )


@click.group()
@click.version_option(version="1.0.0")
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
def main(verbose):
    """
    SolfSound Dispatcher - Audio Extraction and Separation Tool

    Extract audio from videos, separate music into stems, and analyze composition.
    """
    setup_logging(verbose)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', default='extracted_audio',
              help='Output directory for extracted audio')
@click.option('-f', '--format', 'output_format', default='wav',
              type=click.Choice(['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a']),
              help='Output audio format')
@click.option('-b', '--bitrate', default='320k', help='Audio bitrate (e.g., 320k)')
@click.option('-s', '--sample-rate', type=int, help='Sample rate in Hz (e.g., 44100)')
def extract(input_file, output_dir, output_format, bitrate, sample_rate):
    """
    Extract audio from a video file.

    Example:
        solfsound extract video.mp4
        solfsound extract video.mp4 -f mp3 -b 320k
    """
    try:
        console.print(f"\n[bold cyan]Extracting audio from:[/bold cyan] {input_file}")

        extractor = VideoAudioExtractor(output_dir=output_dir)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Extracting audio...", total=None)

            output_file = extractor.extract_audio(
                input_file,
                output_format=output_format,
                bitrate=bitrate,
                sample_rate=sample_rate
            )

        # Get audio info
        info = extractor.get_audio_info(output_file)

        console.print(f"\n[bold green]✓[/bold green] Audio extracted successfully!")
        console.print(f"[bold]Output file:[/bold] {output_file}")
        console.print(f"[bold]Duration:[/bold] {info['duration']:.2f} seconds")
        console.print(f"[bold]Format:[/bold] {info['format']}")
        console.print(f"[bold]Sample rate:[/bold] {info['sample_rate']} Hz")
        console.print(f"[bold]Channels:[/bold] {info['channels']}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', default='separated_stems',
              help='Output directory for separated stems')
@click.option('-m', '--model', default='htdemucs',
              type=click.Choice(['htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'mdx_extra']),
              help='Separation model to use')
@click.option('-s', '--stems', multiple=True,
              help='Specific stems to extract (can be used multiple times)')
@click.option('-f', '--format', 'output_format', default='wav',
              type=click.Choice(['wav', 'mp3', 'flac']),
              help='Output format for stems')
@click.option('--shifts', default=1, type=int,
              help='Number of random shifts for better quality (1-10)')
def separate(audio_file, output_dir, model, stems, output_format, shifts):
    """
    Separate audio into different stems (vocals, drums, bass, other).

    Examples:
        solfsound separate song.wav
        solfsound separate song.wav -s vocals -s drums
        solfsound separate song.wav -m htdemucs_ft --shifts 5
    """
    try:
        console.print(f"\n[bold cyan]Separating audio:[/bold cyan] {audio_file}")
        console.print(f"[bold]Model:[/bold] {model}")

        separator = AudioSeparator(output_dir=output_dir, model_name=model)

        console.print(f"[bold]Available stems:[/bold] {', '.join(separator.get_available_stems())}")

        if stems:
            console.print(f"[bold]Extracting stems:[/bold] {', '.join(stems)}")
        else:
            console.print("[bold]Extracting:[/bold] All stems")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Separating audio...", total=None)

            output_files = separator.separate(
                audio_file,
                output_stems=list(stems) if stems else None,
                output_format=output_format,
                shifts=shifts,
            )

        console.print(f"\n[bold green]✓[/bold green] Separation complete!")
        console.print(f"\n[bold]Extracted stems:[/bold]")
        for stem_name, stem_path in output_files.items():
            console.print(f"  • {stem_name}: {stem_path}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def analyze(audio_file, detailed):
    """
    Analyze audio file composition and structure.

    Examples:
        solfsound analyze song.wav
        solfsound analyze song.wav --detailed
    """
    try:
        console.print(f"\n[bold cyan]Analyzing audio:[/bold cyan] {audio_file}")

        analyzer = AudioAnalyzer()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Analyzing audio...", total=None)

            if detailed:
                analysis = analyzer.analyze_audio(audio_file)
            else:
                summary = analyzer.get_audio_summary(audio_file)

        console.print(f"\n[bold green]✓[/bold green] Analysis complete!\n")

        if detailed:
            # Display detailed analysis
            console.print("[bold]Basic Properties:[/bold]")
            for key, value in analysis['basic'].items():
                console.print(f"  • {key}: {value}")

            console.print("\n[bold]Rhythm:[/bold]")
            for key, value in analysis['rhythm'].items():
                console.print(f"  • {key}: {value}")

            console.print("\n[bold]Harmony:[/bold]")
            for key, value in analysis['harmony'].items():
                console.print(f"  • {key}: {value}")

            console.print("\n[bold]Complexity:[/bold]")
            for key, value in analysis['complexity'].items():
                if key != 'note':
                    console.print(f"  • {key}: {value}")

            if 'note' in analysis['complexity']:
                console.print(f"\n[dim]{analysis['complexity']['note']}[/dim]")
        else:
            # Display summary
            console.print(summary)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', default='output',
              help='Output directory')
@click.option('-m', '--model', default='htdemucs',
              type=click.Choice(['htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'mdx_extra']),
              help='Separation model')
@click.option('-f', '--format', 'output_format', default='wav',
              type=click.Choice(['mp3', 'wav', 'flac']),
              help='Output format')
def process(input_file, output_dir, model, output_format):
    """
    Complete processing pipeline: extract, separate, and analyze.

    Extracts audio from video, separates into stems, and provides analysis.

    Example:
        solfsound process video.mp4
    """
    try:
        input_path = Path(input_file)
        console.print(f"\n[bold cyan]Processing:[/bold cyan] {input_file}\n")

        # Step 1: Extract audio (if video file)
        extracted_file = None
        if input_path.suffix.lower() in VideoAudioExtractor.SUPPORTED_VIDEO_FORMATS:
            console.print("[bold]Step 1/3:[/bold] Extracting audio from video...")
            extractor = VideoAudioExtractor(output_dir=f"{output_dir}/extracted")
            extracted_file = extractor.extract_audio(input_file, output_format='wav')
            console.print(f"[green]✓[/green] Audio extracted: {extracted_file}\n")
            audio_file = extracted_file
        else:
            console.print("[bold]Step 1/3:[/bold] Input is already an audio file, skipping extraction\n")
            audio_file = input_file

        # Step 2: Separate stems
        console.print("[bold]Step 2/3:[/bold] Separating audio into stems...")
        separator = AudioSeparator(output_dir=f"{output_dir}/stems", model_name=model)
        stem_files = separator.separate(audio_file, output_format=output_format)
        console.print(f"[green]✓[/green] Separated into {len(stem_files)} stems\n")

        # Step 3: Analyze
        console.print("[bold]Step 3/3:[/bold] Analyzing audio...")
        analyzer = AudioAnalyzer()

        # Analyze original
        summary = analyzer.get_audio_summary(audio_file)

        # Compare stems
        stem_comparison = analyzer.compare_stems(stem_files)

        console.print(f"[green]✓[/green] Analysis complete!\n")

        # Display results
        console.print("[bold]=" * 50 + "[/bold]")
        console.print(summary)
        console.print("\n[bold]Stem Energy Distribution:[/bold]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Stem")
        table.add_column("Energy %", justify="right")
        table.add_column("RMS", justify="right")

        for stem_name, stem_data in stem_comparison['stems'].items():
            table.add_row(
                stem_name,
                f"{stem_data['percentage']:.1f}%",
                f"{stem_data['rms']:.4f}"
            )

        console.print(table)
        console.print(f"\n[bold]Dominant stem:[/bold] {stem_comparison['dominant_stem']}")
        console.print(f"[bold]Total stems:[/bold] {stem_comparison['total_stems']}")

        console.print("\n[bold]=" * 50 + "[/bold]")
        console.print(f"\n[bold green]✓ Processing complete![/bold green]")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


@main.command()
def models():
    """List available separation models."""
    console.print("\n[bold cyan]Available Separation Models:[/bold cyan]\n")

    models_info = AudioSeparator.list_models()

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Model Name", style="green")
    table.add_column("Description")

    for model_name, description in models_info.items():
        table.add_row(model_name, description)

    console.print(table)
    console.print("\n[dim]Use -m/--model option to select a model[/dim]\n")


@main.command()
def info():
    """Display system information and check dependencies."""
    console.print("\n[bold cyan]SolfSound Dispatcher - System Information[/bold cyan]\n")

    # Check PyTorch and CUDA
    try:
        import torch
        console.print(f"[green]✓[/green] PyTorch: {torch.__version__}")
        console.print(f"[green]✓[/green] CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            console.print(f"    CUDA Version: {torch.version.cuda}")
            console.print(f"    Device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        console.print("[red]✗[/red] PyTorch not installed")

    # Check FFmpeg
    try:
        import ffmpeg
        console.print(f"[green]✓[/green] FFmpeg: Available")
    except ImportError:
        console.print("[red]✗[/red] FFmpeg not installed")

    # Check other dependencies
    dependencies = ['librosa', 'soundfile', 'demucs', 'click', 'rich']
    for dep in dependencies:
        try:
            __import__(dep)
            console.print(f"[green]✓[/green] {dep}: Installed")
        except ImportError:
            console.print(f"[red]✗[/red] {dep}: Not installed")

    console.print()


if __name__ == '__main__':
    main()
