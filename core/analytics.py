"""
Advanced Analytics and Monitoring System for MAXX Ecosystem
Provides real-time analytics, performance monitoring, and alerting
"""
import asyncio
import time
import json
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from decimal import Decimal

from .config import get_monitoring_config
from .logging import get_logger, log_performance
from .database import get_database_manager


class MetricType(Enum):
    """Metric types for monitoring"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeWindow(Enum):
    """Time windows for analytics"""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR_1 = "1h"
    HOUR_6 = "6h"
    DAY_1 = "1d"
    WEEK_1 = "1w"


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: Union[int, float, Decimal]
    metric_type: MetricType
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None

    def __post_init__(self):
        # Convert to float for consistency
        if isinstance(self.value, Decimal):
            self.value = float(self.value)


@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "value > 100", "rate > 0.5"
    severity: AlertSeverity
    threshold: float
    time_window: TimeWindow
    is_active: bool = True
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class PerformanceReport:
    """Performance report"""
    timestamp: float
    period: TimeWindow
    metrics: Dict[str, Any]
    alerts: List[Alert]
    summary: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)


class MetricsCollector:
    """Metrics collection and aggregation"""

    def __init__(self):
        self.config = get_monitoring_config()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics: Dict[str, List[Metric]] = {}
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.timers: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def record_metric(self, metric: Metric):
        """Record a metric"""
        async with self._lock:
            if metric.name not in self.metrics:
                self.metrics[metric.name] = []

            self.metrics[metric.name].append(metric)

            # Update specific metric types
            if metric.metric_type == MetricType.COUNTER:
                self.counters[metric.name] = self.counters.get(metric.name, 0) + float(metric.value)
            elif metric.metric_type == MetricType.GAUGE:
                self.gauges[metric.name] = float(metric.value)
            elif metric.metric_type == MetricType.HISTOGRAM:
                if metric.name not in self.histograms:
                    self.histograms[metric.name] = []
                self.histograms[metric.name].append(float(metric.value))
            elif metric.metric_type == MetricType.TIMER:
                if metric.name not in self.timers:
                    self.timers[metric.name] = []
                self.timers[metric.name].append(float(metric.value))

            # Keep only recent metrics (based on retention)
            cutoff_time = time.time() - (self.config.metrics_retention_hours * 3600)
            self.metrics[metric.name] = [
                m for m in self.metrics[metric.name] if m.timestamp > cutoff_time
            ]

    async def increment_counter(self, name: str, value: float = 1.0,
                              labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels or {}
        )
        await self.record_metric(metric)

    async def set_gauge(self, name: str, value: Union[int, float],
                       labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {}
        )
        await self.record_metric(metric)

    async def record_histogram(self, name: str, value: float,
                             labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {}
        )
        await self.record_metric(metric)

    async def record_timer(self, name: str, duration: float,
                         labels: Optional[Dict[str, str]] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            labels=labels or {}
        )
        await self.record_metric(metric)

    async def get_metrics(self, name: Optional[str] = None,
                         since: Optional[float] = None,
                         window: Optional[TimeWindow] = None) -> List[Metric]:
        """Get metrics with optional filtering"""
        async with self._lock:
            if name:
                metrics_list = self.metrics.get(name, [])
            else:
                # Flatten all metrics
                metrics_list = []
                for metric_list in self.metrics.values():
                    metrics_list.extend(metric_list)

            # Filter by time
            if since:
                metrics_list = [m for m in metrics_list if m.timestamp >= since]
            elif window:
                window_seconds = self._get_window_seconds(window)
                cutoff_time = time.time() - window_seconds
                metrics_list = [m for m in metrics_list if m.timestamp >= cutoff_time]

            # Sort by timestamp
            metrics_list.sort(key=lambda m: m.timestamp)
            return metrics_list

    def _get_window_seconds(self, window: TimeWindow) -> int:
        """Get window duration in seconds"""
        mapping = {
            TimeWindow.MINUTE_1: 60,
            TimeWindow.MINUTE_5: 300,
            TimeWindow.MINUTE_15: 900,
            TimeWindow.HOUR_1: 3600,
            TimeWindow.HOUR_6: 21600,
            TimeWindow.DAY_1: 86400,
            TimeWindow.WEEK_1: 604800
        }
        return mapping.get(window, 3600)

    async def get_aggregated_metrics(self, name: str,
                                   window: TimeWindow) -> Dict[str, float]:
        """Get aggregated metrics for a time window"""
        metrics = await self.get_metrics(name, window=window)

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            'count': len(values),
            'sum': sum(values),
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'p50': np.percentile(values, 50),
            'p90': np.percentile(values, 90),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }


class AlertManager:
    """Alert management and notification"""

    def __init__(self):
        self.config = get_monitoring_config()
        self.logger = get_logger(self.__class__.__name__)
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable] = []
        self._lock = asyncio.Lock()

    async def create_alert(self, name: str, description: str, metric_name: str,
                          condition: str, severity: AlertSeverity,
                          threshold: float, time_window: TimeWindow) -> Alert:
        """Create a new alert"""
        alert_id = f"alert_{int(time.time())}_{len(self.alerts)}"

        alert = Alert(
            id=alert_id,
            name=name,
            description=description,
            metric_name=metric_name,
            condition=condition,
            severity=severity,
            threshold=threshold,
            time_window=time_window
        )

        async with self._lock:
            self.alerts[alert_id] = alert

        self.logger.info(f"Created alert: {name}")
        return alert

    async def evaluate_alerts(self, metrics_collector: MetricsCollector):
        """Evaluate all active alerts"""
        current_time = time.time()

        async with self._lock:
            for alert in self.alerts.values():
                if not alert.is_active:
                    continue

                try:
                    # Get metrics for the alert
                    metrics = await metrics_collector.get_metrics(
                        alert.metric_name,
                        window=alert.time_window
                    )

                    if not metrics:
                        continue

                    # Evaluate condition
                    triggered = await self._evaluate_condition(
                        alert.condition,
                        [m.value for m in metrics],
                        alert.threshold
                    )

                    if triggered:
                        alert.trigger_count += 1
                        alert.last_triggered = current_time

                        # Record alert trigger
                        alert_event = {
                            'alert_id': alert.id,
                            'name': alert.name,
                            'severity': alert.severity.value,
                            'timestamp': current_time,
                            'metric_value': metrics[-1].value if metrics else None,
                            'threshold': alert.threshold
                        }

                        self.alert_history.append(alert_event)

                        # Send notifications
                        await self._send_notifications(alert, alert_event)

                        self.logger.warning(f"Alert triggered: {alert.name}")

                except Exception as e:
                    self.logger.error(f"Error evaluating alert {alert.name}: {e}")

    async def _evaluate_condition(self, condition: str, values: List[float],
                                threshold: float) -> bool:
        """Evaluate alert condition"""
        if not values:
            return False

        latest_value = values[-1]

        # Simple condition evaluation
        if condition == "value > threshold":
            return latest_value > threshold
        elif condition == "value < threshold":
            return latest_value < threshold
        elif condition == "value == threshold":
            return abs(latest_value - threshold) < 0.0001
        elif condition == "rate > threshold":
            if len(values) < 2:
                return False
            rate = (values[-1] - values[0]) / len(values)
            return rate > threshold
        elif condition == "avg > threshold":
            avg = statistics.mean(values)
            return avg > threshold
        elif condition == "max > threshold":
            return max(values) > threshold
        elif condition == "min < threshold":
            return min(values) < threshold

        return False

    async def _send_notifications(self, alert: Alert, alert_event: Dict[str, Any]):
        """Send alert notifications"""
        for handler in self.notification_handlers:
            try:
                await handler(alert, alert_event)
            except Exception as e:
                self.logger.error(f"Notification handler error: {e}")

    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)

    async def get_alerts(self, active_only: bool = True) -> List[Alert]:
        """Get alerts"""
        async with self._lock:
            alerts = list(self.alerts.values())

            if active_only:
                alerts = [a for a in alerts if a.is_active]

            return alerts

    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        async with self._lock:
            return self.alert_history[-limit:]


class PerformanceAnalyzer:
    """Performance analysis and reporting"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.db_manager = None

    async def initialize(self):
        """Initialize performance analyzer"""
        self.db_manager = await get_database_manager()

        # Setup default alerts
        await self._setup_default_alerts()

        self.logger.info("Performance analyzer initialized")

    async def _setup_default_alerts(self):
        """Setup default alerts"""
        # High error rate alert
        await self.alert_manager.create_alert(
            name="High Error Rate",
            description="Error rate exceeds 5%",
            metric_name="error_rate",
            condition="rate > threshold",
            severity=AlertSeverity.HIGH,
            threshold=0.05,
            time_window=TimeWindow.MINUTE_5
        )

        # High response time alert
        await self.alert_manager.create_alert(
            name="High Response Time",
            description="Average response time exceeds 1 second",
            metric_name="response_time",
            condition="avg > threshold",
            severity=AlertSeverity.MEDIUM,
            threshold=1.0,
            time_window=TimeWindow.MINUTE_5
        )

        # Low memory alert
        await self.alert_manager.create_alert(
            name="Low Memory",
            description="Available memory below 10%",
            metric_name="memory_available",
            condition="value < threshold",
            severity=AlertSeverity.CRITICAL,
            threshold=10.0,
            time_window=TimeWindow.MINUTE_1
        )

    @log_performance("analytics.generate_report")
    async def generate_report(self, window: TimeWindow = TimeWindow.HOUR_1) -> PerformanceReport:
        """Generate performance report"""
        current_time = time.time()

        # Collect metrics
        report_metrics = {}

        # System metrics
        system_metrics = [
            "cpu_usage", "memory_usage", "disk_usage", "network_io"
        ]

        for metric_name in system_metrics:
            metrics = await self.metrics_collector.get_metrics(
                metric_name, window=window
            )

            if metrics:
                values = [m.value for m in metrics]
                report_metrics[metric_name] = {
                    'current': values[-1] if values else 0,
                    'avg': statistics.mean(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }

        # Application metrics
        app_metrics = [
            "request_count", "response_time", "error_rate", "active_connections"
        ]

        for metric_name in app_metrics:
            aggregated = await self.metrics_collector.get_aggregated_metrics(
                metric_name, window
            )
            if aggregated:
                report_metrics[metric_name] = aggregated

        # Get active alerts
        active_alerts = await self.alert_manager.get_alerts(active_only=True)

        # Generate summary
        summary = {
            'total_metrics': len(report_metrics),
            'active_alerts': len(active_alerts),
            'critical_alerts': len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            'performance_score': self._calculate_performance_score(report_metrics),
            'health_status': self._determine_health_status(report_metrics, active_alerts)
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(report_metrics, active_alerts)

        return PerformanceReport(
            timestamp=current_time,
            period=window,
            metrics=report_metrics,
            alerts=active_alerts,
            summary=summary,
            recommendations=recommendations
        )

    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        if not metrics:
            return 50.0

        scores = []

        # CPU usage score (lower is better)
        if 'cpu_usage' in metrics:
            cpu_usage = metrics['cpu_usage']['current']
            cpu_score = max(0, 100 - cpu_usage)
            scores.append(cpu_score)

        # Memory usage score (lower is better)
        if 'memory_usage' in metrics:
            memory_usage = metrics['memory_usage']['current']
            memory_score = max(0, 100 - memory_usage)
            scores.append(memory_score)

        # Response time score (lower is better)
        if 'response_time' in metrics:
            response_time = metrics['response_time']['avg']
            # Convert to score (0-100)
            response_score = max(0, 100 - (response_time * 10))
            scores.append(response_score)

        # Error rate score (lower is better)
        if 'error_rate' in metrics:
            error_rate = metrics['error_rate']['current']
            error_score = max(0, 100 - (error_rate * 1000))
            scores.append(error_score)

        return statistics.mean(scores) if scores else 50.0

    def _determine_health_status(self, metrics: Dict[str, Any],
                                alerts: List[Alert]) -> str:
        """Determine overall health status"""
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        high_alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]

        if critical_alerts:
            return "CRITICAL"
        elif high_alerts:
            return "WARNING"
        elif self._calculate_performance_score(metrics) < 70:
            return "DEGRADED"
        else:
            return "HEALTHY"

    def _generate_recommendations(self, metrics: Dict[str, Any],
                                 alerts: List[Alert]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        # CPU recommendations
        if 'cpu_usage' in metrics and metrics['cpu_usage']['current'] > 80:
            recommendations.append("High CPU usage detected. Consider scaling up or optimizing CPU-intensive operations.")

        # Memory recommendations
        if 'memory_usage' in metrics and metrics['memory_usage']['current'] > 85:
            recommendations.append("High memory usage detected. Check for memory leaks or increase available memory.")

        # Response time recommendations
        if 'response_time' in metrics and metrics['response_time']['avg'] > 1.0:
            recommendations.append("Slow response times detected. Optimize database queries and consider caching.")

        # Error rate recommendations
        if 'error_rate' in metrics and metrics['error_rate']['current'] > 0.01:
            recommendations.append("High error rate detected. Review application logs and fix underlying issues.")

        # Alert-specific recommendations
        for alert in alerts:
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                recommendations.append(f"Address critical alert: {alert.name}")

        return recommendations

    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.logger.info("Starting performance monitoring...")

        while True:
            try:
                # Evaluate alerts
                await self.alert_manager.evaluate_alerts(self.metrics_collector)

                # Generate periodic reports
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    report = await self.generate_report(TimeWindow.MINUTE_5)
                    await self._store_report(report)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)

    async def _store_report(self, report: PerformanceReport):
        """Store performance report in database"""
        if not self.db_manager:
            return

        try:
            await self.db_manager.execute_query(
                """
                INSERT INTO performance_reports
                (timestamp, period, metrics, alerts, summary, recommendations)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report.timestamp,
                    report.period.value,
                    json.dumps(report.metrics),
                    json.dumps([asdict(a) for a in report.alerts]),
                    json.dumps(report.summary),
                    json.dumps(report.recommendations)
                ),
                query_type=QueryType.INSERT
            )

        except Exception as e:
            self.logger.error(f"Failed to store report: {e}")


class AnalyticsManager:
    """Unified analytics management"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_analyzer = PerformanceAnalyzer()
        self.is_running = False

    async def initialize(self):
        """Initialize analytics manager"""
        await self.performance_analyzer.initialize()

        # Set up notification handlers
        self.alert_manager.add_notification_handler(self._log_notification)

        self.is_running = True
        self.logger.info("Analytics manager initialized")

    async def start(self):
        """Start analytics monitoring"""
        if not self.is_running:
            await self.initialize()

        # Start monitoring in background
        asyncio.create_task(self.performance_analyzer.start_monitoring())

        self.logger.info("Analytics monitoring started")

    async def stop(self):
        """Stop analytics monitoring"""
        self.is_running = False
        self.logger.info("Analytics monitoring stopped")

    async def _log_notification(self, alert: Alert, alert_event: Dict[str, Any]):
        """Log alert notification"""
        self.logger.warning(
            f"ALERT: {alert.name} - {alert.description} "
            f"(Severity: {alert.severity.value}, Value: {alert_event.get('metric_value')})"
        )

    def get_metrics_collector(self) -> MetricsCollector:
        """Get metrics collector"""
        return self.metrics_collector

    def get_alert_manager(self) -> AlertManager:
        """Get alert manager"""
        return self.alert_manager

    def get_performance_analyzer(self) -> PerformanceAnalyzer:
        """Get performance analyzer"""
        return self.performance_analyzer


# Global analytics manager
_analytics_manager: Optional[AnalyticsManager] = None


async def get_analytics_manager() -> AnalyticsManager:
    """Get global analytics manager instance"""
    global _analytics_manager

    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
        await _analytics_manager.initialize()

    return _analytics_manager


async def close_analytics():
    """Close global analytics manager"""
    global _analytics_manager

    if _analytics_manager:
        await _analytics_manager.stop()
        _analytics_manager = None