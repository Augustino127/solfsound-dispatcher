"""
Monitoring and Performance Tracking

System monitoring, performance metrics, and analytics.
"""

import logging
import time
import psutil
import threading
from typing import Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    processing_times: list = field(default_factory=list)
    success_rate: float = 100.0
    error_count: int = 0
    total_jobs: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'avg_processing_time': statistics.mean(self.processing_times) if self.processing_times else 0,
            'success_rate': self.success_rate,
            'error_count': self.error_count,
            'total_jobs': self.total_jobs,
            'timestamp': self.timestamp.isoformat(),
        }


class PerformanceMonitor:
    """Monitor system and application performance."""

    def __init__(self, interval: int = 60):
        """
        Initialize performance monitor.

        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Metrics
        self.current_metrics = PerformanceMetrics()
        self.metrics_history: list[PerformanceMetrics] = []
        self.max_history_size = 1000

        # Callbacks
        self.on_metrics_update: Optional[Callable] = None

    def start(self):
        """Start monitoring."""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="PerformanceMonitor"
        )
        self.monitor_thread.start()

        logger.info("Performance monitor started")

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        logger.info("Performance monitor stopped")

    def _monitor_loop(self):
        """Monitoring loop."""
        while self.running:
            try:
                # Collect metrics
                self.current_metrics = self._collect_metrics()

                # Store in history
                self.metrics_history.append(self.current_metrics)

                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]

                # Call callback
                if self.on_metrics_update:
                    try:
                        self.on_metrics_update(self.current_metrics)
                    except Exception as e:
                        logger.error(f"Error in metrics callback: {e}")

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")

            time.sleep(self.interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current metrics."""
        metrics = PerformanceMetrics()

        try:
            # CPU usage
            metrics.cpu_usage = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            metrics.memory_usage = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            metrics.disk_usage = disk.percent

            # Preserve other metrics
            metrics.processing_times = self.current_metrics.processing_times.copy()
            metrics.error_count = self.current_metrics.error_count
            metrics.total_jobs = self.current_metrics.total_jobs

            # Calculate success rate
            if metrics.total_jobs > 0:
                metrics.success_rate = ((metrics.total_jobs - metrics.error_count) / metrics.total_jobs) * 100

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

        return metrics

    def record_processing_time(self, time_seconds: float):
        """Record a processing time."""
        self.current_metrics.processing_times.append(time_seconds)

        # Keep only recent times
        if len(self.current_metrics.processing_times) > 100:
            self.current_metrics.processing_times = self.current_metrics.processing_times[-100:]

    def record_job(self, success: bool = True):
        """Record a job execution."""
        self.current_metrics.total_jobs += 1
        if not success:
            self.current_metrics.error_count += 1

    def get_current_metrics(self) -> Dict:
        """Get current metrics as dictionary."""
        return self.current_metrics.to_dict()

    def get_metrics_history(self, limit: int = 100) -> list[Dict]:
        """Get metrics history."""
        return [m.to_dict() for m in self.metrics_history[-limit:]]


# Global monitor instance
_monitor = None


def get_monitor(interval: int = 60) -> PerformanceMonitor:
    """Get global performance monitor."""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor(interval)
        _monitor.start()
    return _monitor
