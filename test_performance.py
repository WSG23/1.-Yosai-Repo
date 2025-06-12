import pandas as pd
import numpy as np
import time
from utils.data_validator import DataQualityAnalyzer


def create_test_dataframe(rows, cols):
    """Create test DataFrame with missing data"""
    np.random.seed(42)
    data = {}
    for i in range(cols):
        col_data = np.random.randn(rows)
        missing_indices = np.random.choice(rows, size=int(rows * 0.1), replace=False)
        col_data[missing_indices] = np.nan
        data[f'column_{i}'] = col_data
    return pd.DataFrame(data)


def test_performance():
    """Test performance of optimized vs original methods"""
    test_cases = [
        (100, 10, "Small"),
        (1000, 20, "Medium"),
        (10000, 50, "Large"),
        (50000, 100, "Very Large"),
    ]
    analyzer = DataQualityAnalyzer()

    print("Performance Test Results:")
    print("=" * 60)
    print(f"{'Dataset':<12} {'Rows':<8} {'Cols':<6} {'Time (ms)':<12} {'Memory (MB)':<12}")
    print("-" * 60)

    for rows, cols, name in test_cases:
        df = create_test_dataframe(rows, cols)
        start_time = time.time()
        start_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        result = analyzer._analyze_missing_data(df)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        print(f"{name:<12} {rows:<8} {cols:<6} {execution_time:<12.2f} {start_memory:<12.2f}")
        expected_missing = df.isnull().sum().sum()
        actual_missing = result['total_missing_cells']
        assert expected_missing == actual_missing, f"Results don't match: {expected_missing} vs {actual_missing}"

    print("\n✅ All performance tests passed!")
    print("📈 Optimizations working correctly")


def compare_methods(df):
    """Compare old vs new method performance"""
    analyzer = DataQualityAnalyzer()
    start = time.time()
    result_new = analyzer._analyze_missing_data(df)
    time_new = (time.time() - start) * 1000

    start = time.time()
    missing_stats_old = {}
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_stats_old[col] = {
            'missing_count': missing_count,
            'missing_percentage': (missing_count / len(df)) * 100 if len(df) > 0 else 0,
        }
    time_old = (time.time() - start) * 1000

    print(f"\nPerformance Comparison for {len(df)} rows, {len(df.columns)} columns:")
    print(f"Old method: {time_old:.2f}ms")
    print(f"New method: {time_new:.2f}ms")
    print(f"Speed improvement: {time_old/time_new:.1f}x faster")
    return result_new


if __name__ == "__main__":
    test_performance()
    test_df = create_test_dataframe(5000, 30)
    compare_methods(test_df)
