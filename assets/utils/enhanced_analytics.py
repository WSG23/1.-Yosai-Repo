# utils/enhanced_analytics.py
"""
Enhanced Analytics Utilities
Comprehensive data processing, export, and analysis utilities for enhanced statistics
"""

import pandas as pd
import numpy as np
import json
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config.settings import REQUIRED_INTERNAL_COLUMNS
from ui.themes.style_config import COLORS
from utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedDataProcessor:
    """Enhanced data processing for comprehensive analytics"""
    
    def __init__(self):
        self.timestamp_col = REQUIRED_INTERNAL_COLUMNS['Timestamp']
        self.doorid_col = REQUIRED_INTERNAL_COLUMNS['DoorID']
        self.userid_col = REQUIRED_INTERNAL_COLUMNS['UserID']
        self.eventtype_col = REQUIRED_INTERNAL_COLUMNS['EventType']
        
    def process_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal access patterns"""
        if df is None or df.empty or self.timestamp_col not in df.columns:
            return self._get_default_temporal_patterns()
        
        patterns = {}
        
        # Hourly patterns
        hourly_counts = df.groupby(df[self.timestamp_col].dt.hour).size()
        patterns['hourly_distribution'] = hourly_counts.to_dict()
        patterns['peak_hour'] = hourly_counts.idxmax()
        patterns['peak_hour_count'] = hourly_counts.max()
        patterns['lowest_hour'] = hourly_counts.idxmin()
        patterns['lowest_hour_count'] = hourly_counts.min()
        
        # Daily patterns
        daily_counts = df.groupby(df[self.timestamp_col].dt.day_name()).size()
        patterns['daily_distribution'] = daily_counts.to_dict()
        patterns['busiest_day'] = daily_counts.idxmax()
        patterns['busiest_day_count'] = daily_counts.max()
        
        # Weekly patterns
        weekly_counts = df.groupby(df[self.timestamp_col].dt.date).size()
        patterns['daily_average'] = weekly_counts.mean()
        patterns['daily_variance'] = weekly_counts.var()
        patterns['trend_slope'] = self._calculate_trend_slope(weekly_counts)
        
        # Activity intensity analysis
        patterns['activity_intensity'] = self._calculate_activity_intensity(hourly_counts)
        patterns['rush_hour_periods'] = self._identify_rush_hours(hourly_counts)
        
        return patterns
    
    def process_user_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        if df is None or df.empty or self.userid_col not in df.columns:
            return self._get_default_user_behavior()
        
        behavior = {}
        
        # User activity metrics
        user_counts = df[self.userid_col].value_counts()
        behavior['total_unique_users'] = len(user_counts)
        behavior['most_active_user'] = user_counts.index[0] if len(user_counts) > 0 else 'N/A'
        behavior['most_active_user_count'] = user_counts.iloc[0] if len(user_counts) > 0 else 0
        behavior['average_events_per_user'] = user_counts.mean()
        behavior['user_activity_variance'] = user_counts.var()
        
        # User session analysis
        if self.timestamp_col in df.columns:
            sessions = self._analyze_user_sessions(df)
            behavior['average_session_length'] = sessions['avg_length']
            behavior['total_sessions'] = sessions['total_count']
            behavior['sessions_per_user'] = sessions['avg_per_user']
        
        # User access patterns
        if self.doorid_col in df.columns:
            access_patterns = self._analyze_access_patterns(df)
            behavior['common_access_sequences'] = access_patterns['sequences']
            behavior['unique_access_patterns'] = access_patterns['unique_patterns']
        
        return behavior
    
    def process_device_analytics(self, df: pd.DataFrame, device_attrs: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Analyze device usage and performance"""
        if df is None or df.empty or self.doorid_col not in df.columns:
            return self._get_default_device_analytics()
        
        analytics = {}
        
        # Device usage metrics
        device_counts = df[self.doorid_col].value_counts()
        analytics['total_devices'] = len(device_counts)
        analytics['most_active_device'] = device_counts.index[0] if len(device_counts) > 0 else 'N/A'
        analytics['most_active_device_count'] = device_counts.iloc[0] if len(device_counts) > 0 else 0
        analytics['average_events_per_device'] = device_counts.mean()
        analytics['device_usage_variance'] = device_counts.var()
        
        # Device performance metrics
        if self.timestamp_col in df.columns:
            # Devices active today
            today = datetime.now().date()
            today_data = df[df[self.timestamp_col].dt.date == today]
            analytics['devices_active_today'] = today_data[self.doorid_col].nunique() if not today_data.empty else 0
            
            # Device activity trends
            device_trends = self._calculate_device_trends(df)
            analytics['trending_devices'] = device_trends
        
        # Security-related device analysis
        if device_attrs is not None and not device_attrs.empty:
            security_analysis = self._analyze_device_security(device_attrs)
            analytics['security_distribution'] = security_analysis
        
        return analytics
    
    def process_security_analytics(self, device_attrs: Optional[pd.DataFrame] = None, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Analyze security-related metrics"""
        security = {}
        
        if device_attrs is not None and not device_attrs.empty:
            # Security level distribution
            if 'SecurityLevel' in device_attrs.columns:
                security_counts = device_attrs['SecurityLevel'].value_counts()
                total_devices = len(device_attrs)
                
                security['distribution'] = security_counts.to_dict()
                security['distribution_percentages'] = (security_counts / total_devices * 100).to_dict()
                security['compliance_score'] = self._calculate_compliance_score(security_counts, total_devices)
                security['security_balance'] = self._assess_security_balance(security_counts)
            
            # Access control effectiveness
            if df is not None and not df.empty:
                effectiveness = self._analyze_access_control_effectiveness(df, device_attrs)
                security['access_control_metrics'] = effectiveness
        
        return security
    
    def _calculate_trend_slope(self, time_series: pd.Series) -> float:
        """Calculate trend slope for time series data"""
        if len(time_series) < 2:
            return 0.0
        
        x = np.arange(len(time_series))
        y = time_series.values
        
        # Simple linear regression
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x))**2)
        return slope
    
    def _calculate_activity_intensity(self, hourly_counts: pd.Series) -> str:
        """Calculate activity intensity level"""
        variance = hourly_counts.var()
        
        if variance > 1000:
            return "High"
        elif variance > 500:
            return "Medium"
        else:
            return "Low"
    
    def _identify_rush_hours(self, hourly_counts: pd.Series) -> List[Tuple[int, int]]:
        """Identify rush hour periods"""
        threshold = hourly_counts.mean() + hourly_counts.std()
        rush_hours = hourly_counts[hourly_counts > threshold]
        
        # Group consecutive hours
        periods = []
        current_start = None
        
        for hour in sorted(rush_hours.index):
            if current_start is None:
                current_start = hour
                current_end = hour
            elif hour == current_end + 1:
                current_end = hour
            else:
                periods.append((current_start, current_end))
                current_start = hour
                current_end = hour
        
        if current_start is not None:
            periods.append((current_start, current_end))
        
        return periods
    
    def _analyze_user_sessions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user session patterns"""
        sessions = []
        
        for user_id in df[self.userid_col].unique():
            user_data = df[df[self.userid_col] == user_id].sort_values(self.timestamp_col)
            
            # Define session breaks (gaps > 30 minutes)
            time_diffs = user_data[self.timestamp_col].diff()
            session_breaks = time_diffs > timedelta(minutes=30)
            
            session_groups = session_breaks.cumsum()
            
            for session_id, session_data in user_data.groupby(session_groups):
                session_length = (session_data[self.timestamp_col].max() - 
                                session_data[self.timestamp_col].min()).total_seconds() / 60
                sessions.append({
                    'user_id': user_id,
                    'length_minutes': session_length,
                    'event_count': len(session_data)
                })
        
        if sessions:
            sessions_df = pd.DataFrame(sessions)
            return {
                'avg_length': sessions_df['length_minutes'].mean(),
                'total_count': len(sessions),
                'avg_per_user': len(sessions) / df[self.userid_col].nunique()
            }
        else:
            return {'avg_length': 0, 'total_count': 0, 'avg_per_user': 0}
    
    def _analyze_access_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze access sequence patterns"""
        sequences = []
        
        for user_id in df[self.userid_col].unique():
            user_data = df[df[self.userid_col] == user_id].sort_values(self.timestamp_col)
            door_sequence = user_data[self.doorid_col].tolist()
            
            # Find common 2-door sequences
            for i in range(len(door_sequence) - 1):
                sequence = (door_sequence[i], door_sequence[i + 1])
                sequences.append(sequence)
        
        if sequences:
            sequence_counts = pd.Series(sequences).value_counts()
            return {
                'sequences': sequence_counts.head(10).to_dict(),
                'unique_patterns': len(sequence_counts)
            }
        else:
            return {'sequences': {}, 'unique_patterns': 0}
    
    def _calculate_device_trends(self, df: pd.DataFrame) -> Dict[str, str]:
        """Calculate device usage trends"""
        trends = {}
        
        # Calculate trend for each device over the last week
        week_ago = datetime.now() - timedelta(days=7)
        recent_data = df[df[self.timestamp_col] >= week_ago]
        
        if recent_data.empty:
            return trends
        
        device_daily_counts = recent_data.groupby([
            recent_data[self.timestamp_col].dt.date,
            self.doorid_col
        ]).size().unstack(fill_value=0)
        
        for device in device_daily_counts.columns:
            device_series = device_daily_counts[device]
            slope = self._calculate_trend_slope(device_series)
            
            if slope > 0.5:
                trends[device] = "📈 Increasing"
            elif slope < -0.5:
                trends[device] = "📉 Decreasing"
            else:
                trends[device] = "📊 Stable"
        
        return trends
    
    def _analyze_device_security(self, device_attrs: pd.DataFrame) -> Dict[str, Any]:
        """Analyze device security configuration"""
        security_analysis = {}
        
        if 'SecurityLevel' in device_attrs.columns:
            security_counts = device_attrs['SecurityLevel'].value_counts()
            security_analysis['level_distribution'] = security_counts.to_dict()
            
        if 'IsOfficialEntrance' in device_attrs.columns:
            entrance_count = device_attrs['IsOfficialEntrance'].sum()
            security_analysis['entrance_devices'] = int(entrance_count)
            
        if 'IsStaircase' in device_attrs.columns:
            stair_count = device_attrs['IsStaircase'].sum()
            security_analysis['stairway_devices'] = int(stair_count)
        
        return security_analysis
    
    def _calculate_compliance_score(self, security_counts: pd.Series, total_devices: int) -> float:
        """Calculate security compliance score"""
        if total_devices == 0:
            return 0.0
        
        # Scoring based on classification completeness and security distribution
        classified_devices = security_counts.sum()
        classification_score = (classified_devices / total_devices) * 70
        
        # Bonus for having high-security devices
        high_security_count = security_counts.get('red', 0)
        security_balance_score = min(30, (high_security_count / total_devices) * 100)
        
        return round(classification_score + security_balance_score, 1)
    
    def _assess_security_balance(self, security_counts: pd.Series) -> str:
        """Assess the balance of security levels"""
        total = security_counts.sum()
        if total == 0:
            return "No data"
        
        red_pct = (security_counts.get('red', 0) / total) * 100
        green_pct = (security_counts.get('green', 0) / total) * 100
        
        if red_pct > 50:
            return "High security focus"
        elif green_pct > 70:
            return "Low security focus"
        else:
            return "Balanced security"
    
    def _analyze_access_control_effectiveness(self, df: pd.DataFrame, device_attrs: pd.DataFrame) -> Dict[str, Any]:
        """Analyze access control effectiveness"""
        effectiveness = {}
        
        # Calculate denied access rate if available
        if self.eventtype_col in df.columns:
            denied_events = df[df[self.eventtype_col].str.contains('DENIED|FAILED', case=False, na=False)]
            total_events = len(df)
            
            if total_events > 0:
                denial_rate = (len(denied_events) / total_events) * 100
                effectiveness['denial_rate'] = round(denial_rate, 2)
                effectiveness['access_success_rate'] = round(100 - denial_rate, 2)
        
        return effectiveness
    
    def _get_default_temporal_patterns(self) -> Dict[str, Any]:
        """Get default temporal patterns structure"""
        return {
            'hourly_distribution': {},
            'peak_hour': 'N/A',
            'peak_hour_count': 0,
            'lowest_hour': 'N/A',
            'lowest_hour_count': 0,
            'daily_distribution': {},
            'busiest_day': 'N/A',
            'busiest_day_count': 0,
            'daily_average': 0,
            'daily_variance': 0,
            'trend_slope': 0,
            'activity_intensity': 'Low',
            'rush_hour_periods': []
        }
    
    def _get_default_user_behavior(self) -> Dict[str, Any]:
        """Get default user behavior structure"""
        return {
            'total_unique_users': 0,
            'most_active_user': 'N/A',
            'most_active_user_count': 0,
            'average_events_per_user': 0,
            'user_activity_variance': 0,
            'average_session_length': 0,
            'total_sessions': 0,
            'sessions_per_user': 0,
            'common_access_sequences': {},
            'unique_access_patterns': 0
        }
    
    def _get_default_device_analytics(self) -> Dict[str, Any]:
        """Get default device analytics structure"""
        return {
            'total_devices': 0,
            'most_active_device': 'N/A',
            'most_active_device_count': 0,
            'average_events_per_device': 0,
            'device_usage_variance': 0,
            'devices_active_today': 0,
            'trending_devices': {},
            'security_distribution': {}
        }


class EnhancedExportManager:
    """Enhanced export functionality for analytics data"""
    
    def __init__(self):
        self.supported_formats = ['PDF', 'Excel', 'PNG', 'JSON', 'CSV']
        
    def export_comprehensive_report(self, stats_data: Dict[str, Any], format: str = 'PDF') -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        try:
            if format.upper() == 'PDF':
                return self._export_pdf_report(stats_data)
            elif format.upper() == 'EXCEL':
                return self._export_excel_report(stats_data)
            elif format.upper() == 'JSON':
                return self._export_json_report(stats_data)
            elif format.upper() == 'CSV':
                return self._export_csv_report(stats_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            return {
                'success': False,
                'error': str(e),
                'format': format
            }
    
    def _export_pdf_report(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export PDF report (placeholder implementation)"""
        # This would use libraries like reportlab or weasyprint
        report_content = self._generate_report_content(stats_data)
        
        return {
            'success': True,
            'format': 'PDF',
            'filename': f'analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            'content': report_content,
            'download_ready': True
        }
    
    def _export_excel_report(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export Excel report"""
        try:
            # Create Excel workbook with multiple sheets
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([stats_data])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Additional sheets for detailed data
                if 'hourly_distribution' in stats_data:
                    hourly_df = pd.DataFrame(list(stats_data['hourly_distribution'].items()), 
                                           columns=['Hour', 'Events'])
                    hourly_df.to_excel(writer, sheet_name='Hourly_Patterns', index=False)
            
            output.seek(0)
            encoded_content = base64.b64encode(output.read()).decode('utf-8')
            
            return {
                'success': True,
                'format': 'Excel',
                'filename': f'analytics_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                'content': encoded_content,
                'download_ready': True
            }
            
        except Exception as e:
            logger.error(f"Excel export error: {e}")
            return {
                'success': False,
                'error': str(e),
                'format': 'Excel'
            }
    
    def _export_json_report(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export JSON report"""
        try:
            # Clean data for JSON serialization
            clean_data = self._clean_data_for_json(stats_data)
            
            json_content = json.dumps(clean_data, indent=2, default=str)
            encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
            
            return {
                'success': True,
                'format': 'JSON',
                'filename': f'analytics_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'content': encoded_content,
                'download_ready': True
            }
            
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return {
                'success': False,
                'error': str(e),
                'format': 'JSON'
            }
    
    def _export_csv_report(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export CSV report"""
        try:
            # Convert stats to DataFrame
            flattened_data = self._flatten_dict(stats_data)
            df = pd.DataFrame([flattened_data])
            
            output = io.StringIO()
            df.to_csv(output, index=False)
            csv_content = output.getvalue()
            encoded_content = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
            
            return {
                'success': True,
                'format': 'CSV',
                'filename': f'analytics_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'content': encoded_content,
                'download_ready': True
            }
            
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return {
                'success': False,
                'error': str(e),
                'format': 'CSV'
            }
    
    def _generate_report_content(self, stats_data: Dict[str, Any]) -> str:
        """Generate formatted report content"""
        report_lines = [
            "ENHANCED ANALYTICS REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 20,
            f"Total Events: {stats_data.get('total_events', 'N/A')}",
            f"Peak Hour: {stats_data.get('peak_hour', 'N/A')}",
            f"Total Devices: {stats_data.get('num_devices', 'N/A')}",
            f"Unique Users: {stats_data.get('unique_users', 'N/A')}",
            f"Compliance Score: {stats_data.get('compliance_score', 'N/A')}%",
            "",
            "DETAILED METRICS",
            "-" * 20,
        ]
        
        # Add more detailed metrics
        for key, value in stats_data.items():
            if key not in ['total_events', 'peak_hour', 'num_devices', 'unique_users', 'compliance_score']:
                report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(report_lines)
    
    def _clean_data_for_json(self, data: Any) -> Any:
        """Clean data for JSON serialization"""
        if isinstance(data, dict):
            return {k: self._clean_data_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_data_for_json(item) for item in data]
        elif isinstance(data, (pd.Timestamp, datetime)):
            return data.isoformat()
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif pd.isna(data):
            return None
        else:
            return data
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


class EnhancedAnomalyDetector:
    """Enhanced anomaly detection for access control data"""
    
    def __init__(self):
        self.detection_methods = ['statistical', 'time_based', 'pattern_based']
        
    def detect_anomalies(self, df: pd.DataFrame, stats_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect various types of anomalies"""
        anomalies = []
        
        try:
            # Statistical anomalies
            stat_anomalies = self._detect_statistical_anomalies(stats_data)
            anomalies.extend(stat_anomalies)
            
            # Time-based anomalies
            if df is not None and not df.empty:
                time_anomalies = self._detect_time_anomalies(df)
                anomalies.extend(time_anomalies)
                
                # Pattern-based anomalies
                pattern_anomalies = self._detect_pattern_anomalies(df)
                anomalies.extend(pattern_anomalies)
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            anomalies.append({
                'type': 'detection_error',
                'severity': 'low',
                'message': f"Error during anomaly detection: {str(e)}",
                'timestamp': datetime.now().isoformat()
            })
        
        return anomalies
    
    def _detect_statistical_anomalies(self, stats_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies"""
        anomalies = []
        
        # Check for unusually high peak activity
        peak_events = stats_data.get('peak_hour_events', 0)
        if peak_events > 1000:
            anomalies.append({
                'type': 'high_peak_activity',
                'severity': 'medium',
                'message': f"Unusually high peak activity: {peak_events} events",
                'value': peak_events,
                'threshold': 1000,
                'timestamp': datetime.now().isoformat()
            })
        
        # Check compliance score
        compliance_score = stats_data.get('compliance_score', 100)
        if compliance_score < 50:
            anomalies.append({
                'type': 'low_compliance',
                'severity': 'high',
                'message': f"Low security compliance score: {compliance_score}%",
                'value': compliance_score,
                'threshold': 50,
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for inactive devices
        devices_today = stats_data.get('devices_active_today', 0)
        total_devices = stats_data.get('num_devices', 0)
        if total_devices > 0 and devices_today / total_devices < 0.5:
            anomalies.append({
                'type': 'low_device_activity',
                'severity': 'medium',
                'message': f"Low device activity: only {devices_today}/{total_devices} devices active today",
                'value': devices_today / total_devices,
                'threshold': 0.5,
                'timestamp': datetime.now().isoformat()
            })
        
        return anomalies
    
    def _detect_time_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect time-based anomalies"""
        anomalies = []
        
        try:
            timestamp_col = REQUIRED_INTERNAL_COLUMNS['Timestamp']
            if timestamp_col not in df.columns:
                return anomalies
            
            # Check for unusual after-hours activity
            night_events = df[df[timestamp_col].dt.hour.isin([22, 23, 0, 1, 2, 3, 4, 5])]
            total_events = len(df)
            
            if total_events > 0:
                night_ratio = len(night_events) / total_events
                if night_ratio > 0.2:  # More than 20% of events at night
                    anomalies.append({
                        'type': 'unusual_night_activity',
                        'severity': 'medium',
                        'message': f"High night-time activity: {night_ratio:.1%} of events",
                        'value': night_ratio,
                        'threshold': 0.2,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check for weekend activity
            weekend_events = df[df[timestamp_col].dt.dayofweek.isin([5, 6])]
            if total_events > 0:
                weekend_ratio = len(weekend_events) / total_events
                if weekend_ratio > 0.3:  # More than 30% on weekends
                    anomalies.append({
                        'type': 'high_weekend_activity',
                        'severity': 'low',
                        'message': f"High weekend activity: {weekend_ratio:.1%} of events",
                        'value': weekend_ratio,
                        'threshold': 0.3,
                        'timestamp': datetime.now().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Time anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_pattern_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect pattern-based anomalies"""
        anomalies = []
        
        try:
            doorid_col = REQUIRED_INTERNAL_COLUMNS['DoorID']
            userid_col = REQUIRED_INTERNAL_COLUMNS['UserID']
            
            if doorid_col not in df.columns or userid_col not in df.columns:
                return anomalies
            
            # Check for users with unusually high activity
            user_counts = df[userid_col].value_counts()
            mean_activity = user_counts.mean()
            std_activity = user_counts.std()
            
            if std_activity > 0:
                threshold = mean_activity + 3 * std_activity
                high_activity_users = user_counts[user_counts > threshold]
                
                for user, count in high_activity_users.items():
                    anomalies.append({
                        'type': 'high_user_activity',
                        'severity': 'medium',
                        'message': f"User {user} has unusually high activity: {count} events",
                        'user_id': user,
                        'value': count,
                        'threshold': threshold,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check for devices with no activity
            device_counts = df[doorid_col].value_counts()
            if len(device_counts) > 0 and device_counts.min() == 0:
                inactive_devices = device_counts[device_counts == 0]
                for device in inactive_devices.index:
                    anomalies.append({
                        'type': 'inactive_device',
                        'severity': 'low',
                        'message': f"Device {device} has no recorded activity",
                        'device_id': device,
                        'value': 0,
                        'threshold': 1,
                        'timestamp': datetime.now().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Pattern anomaly detection error: {e}")
        
        return anomalies


# Factory functions
def create_enhanced_data_processor():
    """Create enhanced data processor instance"""
    return EnhancedDataProcessor()

def create_enhanced_export_manager():
    """Create enhanced export manager instance"""
    return EnhancedExportManager()

def create_enhanced_anomaly_detector():
    """Create enhanced anomaly detector instance"""
    return EnhancedAnomalyDetector()


# Utility functions
def format_large_number(num: Union[int, float]) -> str:
    """Format large numbers with appropriate suffixes"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(int(num))

def calculate_percentage_change(current: float, previous: float) -> Tuple[float, str]:
    """Calculate percentage change and return with direction indicator"""
    if previous == 0:
        return 0.0, "📊"
    
    change = ((current - previous) / previous) * 100
    
    if change > 5:
        return change, "📈"
    elif change < -5:
        return change, "📉"
    else:
        return change, "📊"

def generate_trend_indicator(values: List[float]) -> str:
    """Generate trend indicator from a series of values"""
    if len(values) < 2:
        return "📊"
    
    # Simple trend calculation
    recent_avg = sum(values[-3:]) / min(3, len(values))
    older_avg = sum(values[:-3]) / max(1, len(values) - 3)
    
    if recent_avg > older_avg * 1.1:
        return "📈"
    elif recent_avg < older_avg * 0.9:
        return "📉"
    else:
        return "📊"