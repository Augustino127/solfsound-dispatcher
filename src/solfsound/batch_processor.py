"""
Advanced Batch Processing System

Queue-based batch processing with parallel execution and progress tracking.
"""

import logging
import threading
import queue
import time
from pathlib import Path
from typing import List, Dict, Callable, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enum."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Batch job data class."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = ""
    input_file: Path = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: float = 0.0
    priority: int = 0  # Higher = more priority

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'job_type': self.job_type,
            'input_file': str(self.input_file) if self.input_file else None,
            'parameters': self.parameters,
            'status': self.status.value,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time,
            'priority': self.priority,
        }


class BatchProcessor:
    """Batch processor with queue and worker threads."""

    def __init__(
        self,
        num_workers: int = 4,
        max_queue_size: int = 100,
        auto_start: bool = True
    ):
        """
        Initialize batch processor.

        Args:
            num_workers: Number of worker threads
            max_queue_size: Maximum queue size
            auto_start: Auto-start worker threads
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size

        # Job queue (priority queue)
        self.job_queue = queue.PriorityQueue(maxsize=max_queue_size)

        # Job storage
        self.jobs: Dict[str, BatchJob] = {}
        self.jobs_lock = threading.Lock()

        # Worker threads
        self.workers: List[threading.Thread] = []
        self.running = False

        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'cancelled_jobs': 0,
            'total_processing_time': 0.0,
        }

        # Job processors (job_type -> function)
        self.processors: Dict[str, Callable] = {}

        # Callbacks
        self.on_job_start: Optional[Callable] = None
        self.on_job_complete: Optional[Callable] = None
        self.on_job_failed: Optional[Callable] = None
        self.on_job_progress: Optional[Callable] = None

        if auto_start:
            self.start()

    def register_processor(self, job_type: str, processor: Callable):
        """
        Register a job processor.

        Args:
            job_type: Job type identifier
            processor: Processing function (takes BatchJob, returns result)
        """
        self.processors[job_type] = processor
        logger.info(f"Registered processor for job type: {job_type}")

    def add_job(
        self,
        job_type: str,
        input_file: Path,
        parameters: Dict[str, Any] = None,
        priority: int = 0
    ) -> str:
        """
        Add a job to the queue.

        Args:
            job_type: Type of job
            input_file: Input file path
            parameters: Job parameters
            priority: Job priority (higher = more important)

        Returns:
            Job ID
        """
        if job_type not in self.processors:
            raise ValueError(f"No processor registered for job type: {job_type}")

        job = BatchJob(
            job_type=job_type,
            input_file=Path(input_file),
            parameters=parameters or {},
            status=JobStatus.QUEUED,
            priority=priority
        )

        with self.jobs_lock:
            self.jobs[job.id] = job
            self.stats['total_jobs'] += 1

        # Add to queue (negative priority for max heap behavior)
        self.job_queue.put((-priority, time.time(), job.id))

        logger.info(f"Job added to queue: {job.id} ({job_type})")
        return job.id

    def add_batch(
        self,
        job_type: str,
        input_files: List[Path],
        parameters: Dict[str, Any] = None,
        priority: int = 0
    ) -> List[str]:
        """
        Add multiple jobs to the queue.

        Args:
            job_type: Type of jobs
            input_files: List of input file paths
            parameters: Job parameters (same for all)
            priority: Job priority

        Returns:
            List of job IDs
        """
        job_ids = []

        for input_file in input_files:
            job_id = self.add_job(
                job_type=job_type,
                input_file=input_file,
                parameters=parameters,
                priority=priority
            )
            job_ids.append(job_id)

        logger.info(f"Batch added: {len(job_ids)} jobs")
        return job_ids

    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID."""
        with self.jobs_lock:
            return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status as dictionary."""
        job = self.get_job(job_id)
        return job.to_dict() if job else None

    def get_queue_status(self) -> Dict:
        """Get queue status."""
        with self.jobs_lock:
            pending_jobs = sum(1 for j in self.jobs.values() if j.status == JobStatus.QUEUED)
            processing_jobs = sum(1 for j in self.jobs.values() if j.status == JobStatus.PROCESSING)

        return {
            'queue_size': self.job_queue.qsize(),
            'pending_jobs': pending_jobs,
            'processing_jobs': processing_jobs,
            'total_jobs': self.stats['total_jobs'],
            'completed_jobs': self.stats['completed_jobs'],
            'failed_jobs': self.stats['failed_jobs'],
            'cancelled_jobs': self.stats['cancelled_jobs'],
            'avg_processing_time': (
                self.stats['total_processing_time'] / self.stats['completed_jobs']
                if self.stats['completed_jobs'] > 0 else 0
            ),
            'workers': self.num_workers,
            'running': self.running,
        }

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled, False if not possible
        """
        with self.jobs_lock:
            job = self.jobs.get(job_id)

            if not job:
                return False

            if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now()
                self.stats['cancelled_jobs'] += 1
                logger.info(f"Job cancelled: {job_id}")
                return True

        return False

    def clear_queue(self):
        """Clear all pending jobs from queue."""
        with self.job_queue.mutex:
            self.job_queue.queue.clear()

        with self.jobs_lock:
            for job in self.jobs.values():
                if job.status == JobStatus.QUEUED:
                    job.status = JobStatus.CANCELLED
                    job.completed_at = datetime.now()
                    self.stats['cancelled_jobs'] += 1

        logger.info("Queue cleared")

    def start(self):
        """Start worker threads."""
        if self.running:
            logger.warning("Batch processor already running")
            return

        self.running = True

        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"BatchWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

        logger.info(f"Batch processor started with {self.num_workers} workers")

    def stop(self, wait: bool = True):
        """
        Stop worker threads.

        Args:
            wait: Wait for workers to finish current jobs
        """
        self.running = False

        if wait:
            # Wait for workers to finish
            for worker in self.workers:
                worker.join(timeout=5.0)

        self.workers.clear()
        logger.info("Batch processor stopped")

    def _worker_loop(self):
        """Worker thread loop."""
        logger.info(f"Worker {threading.current_thread().name} started")

        while self.running:
            try:
                # Get job from queue (timeout to check running flag)
                try:
                    priority, timestamp, job_id = self.job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Get job
                with self.jobs_lock:
                    job = self.jobs.get(job_id)

                if not job or job.status == JobStatus.CANCELLED:
                    self.job_queue.task_done()
                    continue

                # Process job
                self._process_job(job)

                self.job_queue.task_done()

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)

        logger.info(f"Worker {threading.current_thread().name} stopped")

    def _process_job(self, job: BatchJob):
        """Process a single job."""
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now()

        # Call on_start callback
        if self.on_job_start:
            try:
                self.on_job_start(job)
            except Exception as e:
                logger.error(f"Error in on_job_start callback: {e}")

        logger.info(f"Processing job: {job.id} ({job.job_type})")

        try:
            # Get processor
            processor = self.processors.get(job.job_type)

            if not processor:
                raise ValueError(f"No processor for job type: {job.job_type}")

            # Process
            result = processor(job)

            # Update job
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.processing_time = (job.completed_at - job.started_at).total_seconds()
            job.progress = 100.0

            # Update stats
            with self.jobs_lock:
                self.stats['completed_jobs'] += 1
                self.stats['total_processing_time'] += job.processing_time

            # Call on_complete callback
            if self.on_job_complete:
                try:
                    self.on_job_complete(job)
                except Exception as e:
                    logger.error(f"Error in on_job_complete callback: {e}")

            logger.info(f"Job completed: {job.id} in {job.processing_time:.2f}s")

        except Exception as e:
            job.error = str(e)
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()

            # Update stats
            with self.jobs_lock:
                self.stats['failed_jobs'] += 1

            # Call on_failed callback
            if self.on_job_failed:
                try:
                    self.on_job_failed(job, e)
                except Exception as err:
                    logger.error(f"Error in on_job_failed callback: {err}")

            logger.error(f"Job failed: {job.id} - {e}", exc_info=True)

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all jobs to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if all completed, False if timeout
        """
        return self.job_queue.join() if timeout is None else self.job_queue.join(timeout)

    def get_all_jobs(self, status_filter: Optional[JobStatus] = None) -> List[BatchJob]:
        """
        Get all jobs, optionally filtered by status.

        Args:
            status_filter: Filter by job status

        Returns:
            List of jobs
        """
        with self.jobs_lock:
            if status_filter:
                return [j for j in self.jobs.values() if j.status == status_filter]
            return list(self.jobs.values())

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Remove old completed/failed jobs from memory.

        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self.jobs_lock:
            jobs_to_remove = [
                job_id for job_id, job in self.jobs.items()
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
                and job.completed_at
                and job.completed_at.timestamp() < cutoff_time
            ]

            for job_id in jobs_to_remove:
                del self.jobs[job_id]

        logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
