"""
Advanced Logging System for MAXX Ecosystem
Provides structured logging with proper formatting, rotation, and monitoring
"""
import logging
import logging.handlers
import sys
import json
import time
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from queue import Queue
import asyncio

from .config import get_monitoring_config, LogLevel


class LogFormat(Enum):
    """Log format types"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: float
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    extra_data: Optional[Dict[str, Any]] = None
    exception_info: Optional[str] = None


class StructuredFormatter(logging.Formatter):
    """Structured log formatter for JSON output"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = LogEntry(
            timestamp=record.created,
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            thread_id=record.thread,
            process_id=record.process,
            extra_data=getattr(record, 'extra_data', None),
            exception_info=self._format_exception(record) if record.exc_info else None
        )

        return json.dumps(asdict(log_entry), default=str)

    def _format_exception(self, record: logging.LogRecord) -> str:
        """Format exception information"""
        if record.exc_info:
            return ''.join(traceback.format_exception(*record.exc_info))
        return ""


class DetailedFormatter(logging.Formatter):
    """Detailed log formatter with rich formatting"""

    def __init__(self):
        super().__init__()
        self.colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
            'RESET': '\033[0m'      # Reset
        }

    def format(self, record: logging.LogRecord) -> str:
        color = self.colors.get(record.levelname, '')
        reset = self.colors['RESET']

        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = f"{color}[{record.levelname}]{reset}"
        module = f"{record.module}:{record.funcName}:{record.lineno}"
        thread_id = f"Thread-{record.thread}"

        base_msg = f"{timestamp} {level} {module} ({thread_id}) - {record.getMessage()}"

        # Add extra data if present
        if hasattr(record, 'extra_data') and record.extra_data:
            extra_str = json.dumps(record.extra_data, default=str)
            base_msg += f" | Extra: {extra_str}"

        # Add exception if present
        if record.exc_info:
            base_msg += f"\n{self.formatException(record.exc_info)}"

        return base_msg


class SimpleFormatter(logging.Formatter):
    """Simple log formatter for basic output"""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        return f"{timestamp} [{record.levelname}] {record.name}: {record.getMessage()}"


class AsyncLogHandler(logging.Handler):
    """Asynchronous log handler for non-blocking logging"""

    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def emit(self, record: logging.LogRecord):
        """Emit log record asynchronously"""
        try:
            self.queue.put_nowait(record)
        except Exception:
            # Fallback to synchronous logging if queue is full
            self._sync_emit(record)

    def _sync_emit(self, record: logging.LogRecord):
        """Synchronous fallback emit"""
        # This would be implemented by the concrete handler
        pass

    def _worker(self):
        """Worker thread for processing log records"""
        while not self._stop_event.is_set():
            try:
                record = self.queue.get(timeout=0.1)
                self._sync_emit(record)
                self.queue.task_done()
            except Exception:
                continue

    def close(self):
        """Close the async handler"""
        self._stop_event.set()
        self._worker_thread.join(timeout=5)
        super().close()


class LogMonitor:
    """Log monitoring and metrics collection"""

    def __init__(self):
        self.log_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def record_log(self, level: str, logger_name: str):
        """Record a log event"""
        with self._lock:
            key = f"{logger_name}:{level}"
            self.log_counts[key] = self.log_counts.get(key, 0) + 1

            if level in ['ERROR', 'CRITICAL']:
                self.error_counts[key] = self.error_counts.get(key, 0) + 1

    def record_performance(self, metric_name: str, value: float):
        """Record performance metric"""
        with self._lock:
            if metric_name not in self.performance_metrics:
                self.performance_metrics[metric_name] = []

            self.performance_metrics[metric_name].append(value)

            # Keep only last 1000 values
            if len(self.performance_metrics[metric_name]) > 1000:
                self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-1000:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        with self._lock:
            return {
                'log_counts': self.log_counts.copy(),
                'error_counts': self.error_counts.copy(),
                'performance_metrics': {
                    name: {
                        'count': len(values),
                        'avg': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }
                    for name, values in self.performance_metrics.items()
                }
            }


class LoggingManager:
    """Advanced logging manager with multiple handlers and formats"""

    def __init__(self):
        self.config = get_monitoring_config()
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.monitor = LogMonitor()
        self._async_queue: Optional[Queue] = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level.value))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Setup console handler
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)

        # Setup file handler if configured
        if self.config.log_file:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)

        # Setup async queue if metrics are enabled
        if self.config.metrics_enabled:
            self._async_queue = Queue(maxsize=10000)

    def _create_console_handler(self) -> logging.Handler:
        """Create console handler with appropriate formatter"""
        handler = logging.StreamHandler(sys.stdout)

        # Choose formatter based on environment
        if self.config.log_level == LogLevel.DEBUG:
            formatter = DetailedFormatter()
        else:
            formatter = SimpleFormatter()

        handler.setFormatter(formatter)
        handler.setLevel(getattr(logging, self.config.log_level.value))

        self.handlers['console'] = handler
        return handler

    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler"""
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler to manage log size
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )

        # Use JSON formatter for file logs
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)  # Log everything to file

        self.handlers['file'] = handler
        return handler

    def get_logger(self, name: str, extra_data: Optional[Dict[str, Any]] = None) -> logging.Logger:
        """Get or create a logger with additional context"""
        if name not in self.loggers:
            logger = logging.getLogger(name)

            # Add custom adapter for extra data
            if extra_data:
                logger = LoggerAdapter(logger, extra_data)

            self.loggers[name] = logger

        return self.loggers[name]

    def log_with_context(self,
                        logger_name: str,
                        level: str,
                        message: str,
                        extra_data: Optional[Dict[str, Any]] = None,
                        exc_info: Optional[bool] = None):
        """Log message with context and metrics"""
        logger = self.get_logger(logger_name)

        # Add performance timing if requested
        if extra_data and 'timing' in extra_data:
            self.monitor.record_performance(
                f"{logger_name}_timing",
                extra_data['timing']
            )

        # Record log metrics
        self.monitor.record_log(level, logger_name)

        # Log the message
        log_method = getattr(logger, level.lower())
        log_method(message, extra={'extra_data': extra_data}, exc_info=exc_info)

    def setup_async_logging(self):
        """Setup asynchronous logging handlers"""
        if not self._async_queue:
            return

        # Replace existing handlers with async versions
        for name, handler in self.handlers.items():
            if isinstance(handler, logging.StreamHandler):
                async_handler = AsyncLogHandler(self._async_queue)
                async_handler.setLevel(handler.level)
                async_handler.setFormatter(handler.formatter)

                # Replace in root logger
                root_logger = logging.getLogger()
                root_logger.removeHandler(handler)
                root_logger.addHandler(async_handler)

                self.handlers[name] = async_handler

    def get_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        return self.monitor.get_metrics()

    def reload_configuration(self):
        """Reload logging configuration"""
        self.config = get_monitoring_config()
        self._setup_logging()

    def shutdown(self):
        """Shutdown logging system"""
        # Close all handlers
        for handler in self.handlers.values():
            handler.close()

        # Clear loggers
        self.loggers.clear()
        self.handlers.clear()


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for additional context"""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with additional context"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        # Merge adapter context with extra data
        if self.extra:
            kwargs['extra'].update(self.extra)

        return msg, kwargs


class PerformanceLogger:
    """Performance logging context manager"""

    def __init__(self, logger_name: str, operation: str, level: str = 'INFO'):
        self.logger_name = logger_name
        self.operation = operation
        self.level = level
        self.start_time: Optional[float] = None
        self.logging_manager = logging_manager

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time

            extra_data = {
                'operation': self.operation,
                'timing': duration,
                'success': exc_type is None
            }

            if exc_type:
                extra_data['exception'] = str(exc_val)
                self.logging_manager.log_with_context(
                    self.logger_name,
                    'ERROR',
                    f"Operation '{self.operation}' failed after {duration:.3f}s",
                    extra_data=extra_data,
                    exc_info=True
                )
            else:
                self.logging_manager.log_with_context(
                    self.logger_name,
                    self.level,
                    f"Operation '{self.operation}' completed in {duration:.3f}s",
                    extra_data=extra_data
                )


# Global logging manager instance
logging_manager = LoggingManager()


def get_logger(name: str, extra_data: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """Get logger with additional context"""
    return logging_manager.get_logger(name, extra_data)


def log_performance(logger_name: str, operation: str, level: str = 'INFO') -> PerformanceLogger:
    """Get performance logger context manager"""
    return PerformanceLogger(logger_name, operation, level)


def setup_logging():
    """Setup logging system (called at application startup)"""
    logging_manager.reload_configuration()


def get_logging_metrics() -> Dict[str, Any]:
    """Get logging metrics"""
    return logging_manager.get_metrics()


def shutdown_logging():
    """Shutdown logging system (called at application shutdown)"""
    logging_manager.shutdown()