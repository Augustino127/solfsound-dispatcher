"""
Web API Backend for SolfSound Dispatcher

FastAPI backend for web and mobile interfaces.
"""

import os
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .extractor import VideoAudioExtractor
from .separator import AudioSeparator
from .analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SolfSound Dispatcher API",
    description="Audio extraction, separation, and analysis API",
    version="1.0.0"
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Global instances
extractor = VideoAudioExtractor(output_dir=str(OUTPUT_DIR / "extracted"))
analyzer = AudioAnalyzer()

# Job storage
jobs = {}


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None


class SeparationRequest(BaseModel):
    audio_file: str
    model: str = "htdemucs"
    stems: Optional[List[str]] = None
    output_format: str = "wav"
    shifts: int = 1


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SolfSound Dispatcher API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "upload": "/upload",
            "extract": "/extract",
            "separate": "/separate",
            "analyze": "/analyze",
            "process": "/process",
            "jobs": "/jobs/{job_id}",
            "models": "/models",
        }
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a video or audio file.

    Returns the file path for further processing.
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix
        filename = f"{timestamp}_{Path(file.filename).stem}{file_ext}"
        file_path = UPLOAD_DIR / filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file_path}")

        return {
            "status": "success",
            "filename": filename,
            "filepath": str(file_path),
            "size": file_path.stat().st_size,
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract")
async def extract_audio(
    filepath: str,
    output_format: str = "wav",
    bitrate: str = "320k",
    background_tasks: BackgroundTasks = None
):
    """Extract audio from video file."""
    try:
        file_path = Path(filepath)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Extract audio
        output_file = extractor.extract_audio(
            file_path,
            output_format=output_format,
            bitrate=bitrate
        )

        # Get info
        info = extractor.get_audio_info(output_file)

        return {
            "status": "success",
            "output_file": str(output_file),
            "info": info,
        }

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/separate")
async def separate_audio(request: SeparationRequest, background_tasks: BackgroundTasks):
    """Separate audio into stems (background task)."""
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    jobs[job_id] = JobStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Queued for processing"
    )

    # Start background task
    background_tasks.add_task(
        _separate_audio_task,
        job_id,
        request
    )

    return {
        "status": "success",
        "job_id": job_id,
        "message": "Separation started"
    }


async def _separate_audio_task(job_id: str, request: SeparationRequest):
    """Background task for audio separation."""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10
        jobs[job_id].message = "Loading model..."

        # Load separator
        separator = AudioSeparator(
            output_dir=str(OUTPUT_DIR / "stems"),
            model_name=request.model
        )

        jobs[job_id].progress = 30
        jobs[job_id].message = "Separating audio..."

        # Separate
        output_files = separator.separate(
            request.audio_file,
            output_stems=request.stems,
            output_format=request.output_format,
            shifts=request.shifts
        )

        jobs[job_id].progress = 100
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Separation completed"
        jobs[job_id].result = {
            "stems": {name: str(path) for name, path in output_files.items()}
        }

    except Exception as e:
        logger.error(f"Separation failed: {e}")
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
        jobs[job_id].message = "Separation failed"


@app.post("/analyze")
async def analyze_audio(filepath: str):
    """Analyze audio file."""
    try:
        file_path = Path(filepath)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Analyze
        analysis = analyzer.analyze_audio(file_path)

        return {
            "status": "success",
            "analysis": analysis,
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_complete(
    filepath: str,
    model: str = "htdemucs",
    background_tasks: BackgroundTasks = None
):
    """Complete processing pipeline."""
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    jobs[job_id] = JobStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Queued for processing"
    )

    background_tasks.add_task(
        _process_complete_task,
        job_id,
        filepath,
        model
    )

    return {
        "status": "success",
        "job_id": job_id,
        "message": "Processing started"
    }


async def _process_complete_task(job_id: str, filepath: str, model: str):
    """Complete processing pipeline background task."""
    try:
        file_path = Path(filepath)

        # Step 1: Extract audio if video
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10
        jobs[job_id].message = "Extracting audio..."

        if file_path.suffix.lower() in VideoAudioExtractor.SUPPORTED_VIDEO_FORMATS:
            audio_file = extractor.extract_audio(file_path, output_format='wav')
        else:
            audio_file = file_path

        # Step 2: Separate
        jobs[job_id].progress = 30
        jobs[job_id].message = "Separating stems..."

        separator = AudioSeparator(
            output_dir=str(OUTPUT_DIR / "stems"),
            model_name=model
        )
        stem_files = separator.separate(audio_file, output_format='wav')

        # Step 3: Analyze
        jobs[job_id].progress = 80
        jobs[job_id].message = "Analyzing audio..."

        analysis = analyzer.analyze_audio(audio_file)
        stem_comparison = analyzer.compare_stems(stem_files)

        jobs[job_id].progress = 100
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Processing completed"
        jobs[job_id].result = {
            "audio_file": str(audio_file),
            "stems": {name: str(path) for name, path in stem_files.items()},
            "analysis": analysis,
            "stem_comparison": stem_comparison,
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
        jobs[job_id].message = "Processing failed"


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.get("/models")
async def list_models():
    """List available separation models."""
    return {
        "models": AudioSeparator.list_models()
    }


@app.get("/download/{filepath:path}")
async def download_file(filepath: str):
    """Download a file."""
    file_path = Path(filepath)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type='application/octet-stream'
    )


@app.delete("/cleanup")
async def cleanup_files(older_than_hours: int = 24):
    """Clean up old files."""
    try:
        import time
        current_time = time.time()
        deleted_count = 0

        for directory in [UPLOAD_DIR, OUTPUT_DIR]:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
                    if file_age_hours > older_than_hours:
                        file_path.unlink()
                        deleted_count += 1

        return {
            "status": "success",
            "deleted_files": deleted_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
