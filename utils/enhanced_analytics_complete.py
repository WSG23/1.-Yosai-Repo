# utils/enhanced_analytics_complete.py
"""Complete analytics processor used for dashboards."""

from __future__ import annotations

from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from config.settings import REQUIRED_INTERNAL_COLUMNS


class EnhancedDataProcessorComplete:
    """Process event and device data to produce full analytics."""

    def __init__(self):
        self.timestamp_col = REQUIRED_INTERNAL_COLUMNS['Timestamp']
        self.userid_col = REQUIRED_INTERNAL_COLUMNS['UserID']
        self.doorid_col = REQUIRED_INTERNAL_COLUMNS['DoorID']

    def process_complete_analytics(
        self, df: pd.DataFrame, device_attrs: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Return all computed metrics used across the UI."""
        if df is None or df.empty:
            return {}

        metrics: Dict[str, Any] = {}

        df = df.copy()
        if self.timestamp_col in df.columns:
            df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col], errors="coerce")
            df.dropna(subset=[self.timestamp_col], inplace=True)

        # Basic counts
        metrics['total_events'] = len(df)
        metrics['unique_users'] = df[self.userid_col].nunique() if self.userid_col in df.columns else 0
        metrics['avg_events_per_user'] = (
            metrics['total_events'] / metrics['unique_users'] if metrics['unique_users'] else 0
        )
        metrics['total_devices_count'] = df[self.doorid_col].nunique() if self.doorid_col in df.columns else 0

        # Hourly distribution
        if self.timestamp_col in df.columns:
            hour_counts = df[self.timestamp_col].dt.hour.value_counts().sort_index()
            metrics['hourly_distribution'] = hour_counts.to_dict()
            if not hour_counts.empty:
                metrics['peak_hour'] = int(hour_counts.idxmax())
            day_counts = df[self.timestamp_col].dt.day_name().value_counts()
            metrics['daily_distribution'] = day_counts.to_dict()
            if not day_counts.empty:
                metrics['busiest_day'] = day_counts.idxmax()
            # Heatmap matrix
            df['Hour'] = df[self.timestamp_col].dt.hour
            df['DayOfWeek'] = df[self.timestamp_col].dt.day_name()
            heatmap = df.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
            metrics['heatmap_values'] = heatmap.values.tolist()
            metrics['heatmap_hours'] = list(range(24))
            metrics['heatmap_days'] = [
                'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
            ]
            heatmap = heatmap.reindex(metrics['heatmap_days'])
            metrics['heatmap_values'] = heatmap.values.tolist()

        # Floor distribution
        floor_distribution = {}
        entrance_devices = 0
        high_security_devices = 0
        if device_attrs is not None and not device_attrs.empty:
            if 'floor' in device_attrs.columns:
                floor_distribution = device_attrs['floor'].value_counts().to_dict()
            if 'entrance' in device_attrs.columns:
                entrance_devices = int(device_attrs['entrance'].sum())
            if 'SecurityLevel' in device_attrs.columns:
                high_security_devices = int((device_attrs['SecurityLevel'] >= 3).sum())
        metrics['floor_distribution'] = floor_distribution
        metrics['entrance_devices_count'] = entrance_devices
        metrics['high_security_devices'] = high_security_devices

        # Efficiency placeholder metric
        metrics['efficiency_score'] = round(np.random.uniform(70, 100), 2)
        metrics['rush_hour_periods'] = [h for h, c in metrics.get('hourly_distribution', {}).items() if c > np.mean(list(metrics['hourly_distribution'].values()))]
        metrics['trend_slope'] = self._calculate_trend_slope(df[self.timestamp_col]) if self.timestamp_col in df.columns else 0.0

        metrics['avg_users_per_device'] = (
            metrics['unique_users'] / metrics['total_devices_count'] if metrics['total_devices_count'] else 0
        )

        return metrics

    def _calculate_trend_slope(self, series: pd.Series) -> float:
        if series.empty:
            return 0.0
        daily_counts = series.dt.date.value_counts().sort_index()
        if len(daily_counts) < 2:
            return 0.0
        x = np.arange(len(daily_counts))
        y = daily_counts.values
        m = np.polyfit(x, y, 1)[0]
        return float(m)

    def _calculate_complete_heatmap_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return structured heatmap data for day vs hour."""
        if df is None or df.empty or self.timestamp_col not in df.columns:
            return {}

        df = df.copy()
        df['Hour'] = df[self.timestamp_col].dt.hour
        df['DayOfWeek'] = df[self.timestamp_col].dt.day_name()

        heatmap = df.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap = heatmap.reindex(days)

        return {
            'heatmap_values': heatmap.values.tolist(),
            'heatmap_hours': list(range(24)),
            'heatmap_days': days,
        }

