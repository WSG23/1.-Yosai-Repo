# utils/monitoring.py
"""
Application monitoring and health checks
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Health check result"""
    name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    process_count: int
    uptime_seconds: float

class HealthChecker:
    """Health check manager"""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self.last_results: Dict[str, HealthCheckResult] = {}
        self.lock = threading.Lock()
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """Register a health check"""
        with self.lock:
            self.checks[name] = check_func
            logger.info(f"Registered health check: {name}")
    
    def run_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks"""
        results = {}
        
        with self.lock:
            checks_to_run = self.checks.copy()
        
        for name, check_func in checks_to_run.items():
            try:
                start_time = time.time()
                result = check_func()
                result.response_time_ms = (time.time() - start_time) * 1000
                result.timestamp = datetime.utcnow()
                results[name] = result
                
            except Exception as e:
                results[name] = HealthCheckResult(
                    name=name,
                    status='unhealthy',
                    message=f"Health check failed: {str(e)}",
                    response_time_ms=0,
                    timestamp=datetime.utcnow()
                )
                logger.error(f"Health check {name} failed: {str(e)}")
        
        with self.lock:
            self.last_results.update(results)
        
        return results
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall application health status"""
        with self.lock:
            results = self.last_results.copy()
        
        if not results:
            return {
                'status': 'unknown',
                'message': 'No health checks have been run',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Determine overall status
        statuses = [result.status for result in results.values()]
        
        if any(status == 'unhealthy' for status in statuses):
            overall_status = 'unhealthy'
        elif any(status == 'degraded' for status in statuses):
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {name: asdict(result) for name, result in results.items()},
            'summary': {
                'total_checks': len(results),
                'healthy': sum(1 for s in statuses if s == 'healthy'),
                'degraded': sum(1 for s in statuses if s == 'degraded'),
                'unhealthy': sum(1 for s in statuses if s == 'unhealthy')
            }
        }

class MetricsCollector:
    """System metrics collector"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Performance counters
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process count
            process_count = len(psutil.pids())
            
            # Uptime
            uptime = time.time() - self.start_time
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                process_count=process_count,
                uptime_seconds=uptime
            )
            
            with self.lock:
                self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            raise
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric"""
        with self.lock:
            self.counters[name] += value
    
    def record_timing(self, name: str, duration_ms: float):
        """Record a timing metric"""
        with self.lock:
            self.timers[name].append(duration_ms)
            # Keep only recent timings
            if len(self.timers[name]) > 100:
                self.timers[name] = self.timers[name][-100:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        with self.lock:
            recent_metrics = list(self.metrics_history)[-10:]  # Last 10 readings
            counters_copy = dict(self.counters)
            timers_copy = {k: list(v) for k, v in self.timers.items()}
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        latest_metrics = recent_metrics[-1]
        
        # Calculate averages for recent metrics
        if len(recent_metrics) > 1:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = latest_metrics.cpu_percent
            avg_memory = latest_metrics.memory_percent
        
        # Calculate timing statistics
        timing_stats = {}
        for name, timings in timers_copy.items():
            if timings:
                timing_stats[name] = {
                    'count': len(timings),
                    'avg_ms': sum(timings) / len(timings),
                    'min_ms': min(timings),
                    'max_ms': max(timings)
                }
        
        return {
            'timestamp': latest_metrics.timestamp.isoformat(),
            'system': {
                'cpu_percent': latest_metrics.cpu_percent,
                'cpu_percent_avg': avg_cpu,
                'memory_percent': latest_metrics.memory_percent,
                'memory_percent_avg': avg_memory,
                'memory_used_mb': latest_metrics.memory_used_mb,
                'disk_usage_percent': latest_metrics.disk_usage_percent,
                'disk_free_gb': latest_metrics.disk_free_gb,
                'uptime_seconds': latest_metrics.uptime_seconds
            },
            'counters': counters_copy,
            'timings': timing_stats
        }

class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def add_alert_rule(self, name: str, condition: Callable[[SystemMetrics], bool], 
                      severity: str = 'warning', message: str = ""):
        """Add an alert rule"""
        rule = {
            'name': name,
            'condition': condition,
            'severity': severity,
            'message': message,
            'last_triggered': None
        }
        
        with self.lock:
            self.alert_rules.append(rule)
        
        logger.info(f"Added alert rule: {name}")
    
    def check_alerts(self, metrics: SystemMetrics):
        """Check alert conditions against current metrics"""
        with self.lock:
            rules_to_check = self.alert_rules.copy()
        
        for rule in rules_to_check:
            try:
                if rule['condition'](metrics):
                    # Prevent spam - only trigger if not triggered in last 5 minutes
                    now = datetime.utcnow()
                    if (rule['last_triggered'] is None or 
                        now - rule['last_triggered'] > timedelta(minutes=5)):
                        
                        alert = {
                            'name': rule['name'],
                            'severity': rule['severity'],
                            'message': rule['message'],
                            'timestamp': now,
                            'metrics': asdict(metrics)
                        }
                        
                        with self.lock:
                            self.alerts.append(alert)
                            rule['last_triggered'] = now
                        
                        logger.warning(f"Alert triggered: {rule['name']} - {rule['message']}")
                        
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {str(e)}")
    
    def get_active_alerts(self, max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """Get active alerts within time window"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        with self.lock:
            active_alerts = [
                alert for alert in self.alerts
                if alert['timestamp'] > cutoff
            ]
        
        return sorted(active_alerts, key=lambda x: x['timestamp'], reverse=True)

# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()

def setup_default_health_checks():
    """Setup default health checks"""
    
    def database_health() -> HealthCheckResult:
        """Check database connectivity (placeholder)"""
        # In a real app, check database connection
        return HealthCheckResult(
            name='database',
            status='healthy',
            message='Database connection is healthy',
            response_time_ms=0,
            timestamp=datetime.utcnow()
        )
    
    def memory_health() -> HealthCheckResult:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            status = 'unhealthy'
            message = f'High memory usage: {memory.percent:.1f}%'
        elif memory.percent > 75:
            status = 'degraded'
            message = f'Elevated memory usage: {memory.percent:.1f}%'
        else:
            status = 'healthy'
            message = f'Memory usage normal: {memory.percent:.1f}%'
        
        return HealthCheckResult(
            name='memory',
            status=status,
            message=message,
            response_time_ms=0,
            timestamp=datetime.utcnow(),
            details={'memory_percent': memory.percent}
        )
    
    def disk_health() -> HealthCheckResult:
        """Check disk space"""
        disk = psutil.disk_usage('/')
        
        if disk.percent > 95:
            status = 'unhealthy'
            message = f'Very low disk space: {disk.percent:.1f}% used'
        elif disk.percent > 85:
            status = 'degraded'
            message = f'Low disk space: {disk.percent:.1f}% used'
        else:
            status = 'healthy'
            message = f'Disk space normal: {disk.percent:.1f}% used'
        
        return HealthCheckResult(
            name='disk',
            status=status,
            message=message,
            response_time_ms=0,
            timestamp=datetime.utcnow(),
            details={'disk_percent': disk.percent}
        )
    
    # Register health checks
    health_checker.register_check('database', database_health)
    health_checker.register_check('memory', memory_health)
    health_checker.register_check('disk', disk_health)

def setup_default_alerts():
    """Setup default alert rules"""
    
    # High CPU usage alert
    alert_manager.add_alert_rule(
        name='high_cpu',
        condition=lambda m: m.cpu_percent > 80,
        severity='warning',
        message='High CPU usage detected'
    )
    
    # High memory usage alert
    alert_manager.add_alert_rule(
        name='high_memory',
        condition=lambda m: m.memory_percent > 85,
        severity='warning',
        message='High memory usage detected'
    )
    
    # Low disk space alert
    alert_manager.add_alert_rule(
        name='low_disk',
        condition=lambda m: m.disk_usage_percent > 90,
        severity='critical',
        message='Low disk space detected'
    )

def initialize_monitoring():
    """Initialize monitoring system"""
    setup_default_health_checks()
    setup_default_alerts()
    logger.info("Monitoring system initialized")

# Monitoring thread
class MonitoringThread(threading.Thread):
    """Background monitoring thread"""
    
    def __init__(self, interval_seconds: int = 60):
        super().__init__(daemon=True)
        self.interval = interval_seconds
        self.running = False
    
    def run(self):
        """Run monitoring loop"""
        self.running = True
        logger.info("Monitoring thread started")
        
        while self.running:
            try:
                # Collect metrics
                metrics = metrics_collector.collect_system_metrics()
                
                # Check alerts
                alert_manager.check_alerts(metrics)
                
                # Log performance metrics
                perf_logger = logging.getLogger('performance')
                perf_logger.info(
                    "System metrics collected",
                    extra={
                        'cpu_percent': metrics.cpu_percent,
                        'memory_percent': metrics.memory_percent,
                        'disk_percent': metrics.disk_usage_percent,
                        'uptime': metrics.uptime_seconds
                    }
                )
                
            except Exception as e:
                logger.error(f"Error in monitoring thread: {str(e)}")
            
            time.sleep(self.interval)
    
    def stop(self):
        """Stop monitoring thread"""
        self.running = False
        logger.info("Monitoring thread stopped")

# Global monitoring thread
monitoring_thread = None

def start_monitoring(interval_seconds: int = 60):
    """Start background monitoring"""
    global monitoring_thread
    
    if monitoring_thread and monitoring_thread.is_alive():
        logger.warning("Monitoring thread already running")
        return
    
    monitoring_thread = MonitoringThread(interval_seconds)
    monitoring_thread.start()
    logger.info("Background monitoring started")

def stop_monitoring():
    """Stop background monitoring"""
    global monitoring_thread
    
    if monitoring_thread:
        monitoring_thread.stop()
        monitoring_thread.join(timeout=5)
        logger.info("Background monitoring stopped")