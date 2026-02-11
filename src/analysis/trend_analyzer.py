"""
Market Trend Analyzer
Identifies patterns and trends in app performance data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path


class TrendAnalyzer:
    """Analyze market trends from SensorTower data"""

    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def analyze_category_performance(
        self,
        apps_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Analyze performance across categories

        Args:
            apps_data: List of app data dictionaries

        Returns:
            DataFrame with category performance metrics
        """
        df = pd.DataFrame(apps_data)

        if df.empty:
            return df

        # Group by category
        category_stats = df.groupby('category').agg({
            'revenue': ['mean', 'median', 'sum'],
            'downloads': ['mean', 'median', 'sum'],
            'rating': 'mean',
            'app_id': 'count'
        }).round(2)

        category_stats.columns = ['_'.join(col) for col in category_stats.columns]
        category_stats = category_stats.rename(columns={'app_id_count': 'app_count'})

        return category_stats.sort_values('revenue_sum', ascending=False)

    def identify_emerging_trends(
        self,
        historical_data: pd.DataFrame,
        lookback_days: int = 30
    ) -> List[Dict]:
        """
        Identify emerging trends in the data

        Args:
            historical_data: Time-series data of app performance
            lookback_days: Number of days to analyze

        Returns:
            List of identified trends
        """
        trends = []

        # Example: Rising categories
        if 'category' in historical_data.columns:
            recent_growth = historical_data.groupby('category')['downloads'].pct_change()
            growing_categories = recent_growth[recent_growth > 0.1].index.unique()

            for category in growing_categories:
                trends.append({
                    'type': 'category_growth',
                    'category': category,
                    'growth_rate': recent_growth[category]
                })

        return trends

    def analyze_successful_app_patterns(
        self,
        top_apps: List[Dict],
        threshold_percentile: int = 90
    ) -> Dict:
        """
        Identify common patterns in successful apps

        Args:
            top_apps: List of top-performing apps
            threshold_percentile: Percentile to define "successful"

        Returns:
            Dictionary of identified patterns
        """
        df = pd.DataFrame(top_apps)

        if df.empty:
            return {}

        patterns = {
            'avg_price': df['price'].mean() if 'price' in df else 0,
            'common_categories': df['category'].value_counts().head(5).to_dict() if 'category' in df else {},
            'avg_rating': df['rating'].mean() if 'rating' in df else 0,
            'monetization_models': df['monetization'].value_counts().to_dict() if 'monetization' in df else {}
        }

        return patterns

    def compare_competitors(
        self,
        app_id: str,
        competitor_ids: List[str],
        apps_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Compare an app against its competitors

        Args:
            app_id: Target app ID
            competitor_ids: List of competitor app IDs
            apps_data: Complete app data

        Returns:
            Comparison DataFrame
        """
        all_ids = [app_id] + competitor_ids
        df = pd.DataFrame(apps_data)

        if df.empty or 'app_id' not in df:
            return pd.DataFrame()

        comparison = df[df['app_id'].isin(all_ids)]

        return comparison.set_index('app_id')[
            ['name', 'category', 'rating', 'downloads', 'revenue']
        ]

    def generate_insights_report(
        self,
        apps_data: List[Dict],
        output_file: str = "market_insights.md"
    ) -> str:
        """
        Generate a comprehensive insights report

        Args:
            apps_data: Complete app data
            output_file: Output filename

        Returns:
            Path to generated report
        """
        df = pd.DataFrame(apps_data)
        report_path = self.data_dir / output_file

        with open(report_path, 'w') as f:
            f.write("# Market Insights Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

            # Summary statistics
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total apps analyzed: {len(df)}\n")

            if 'category' in df:
                f.write(f"- Categories covered: {df['category'].nunique()}\n")

            if 'revenue' in df:
                f.write(f"- Total revenue: ${df['revenue'].sum():,.0f}\n")
                f.write(f"- Average revenue: ${df['revenue'].mean():,.0f}\n")

            # Category performance
            if not df.empty and 'category' in df:
                f.write("\n## Top Categories by Revenue\n\n")
                cat_perf = self.analyze_category_performance(apps_data)
                f.write(cat_perf.head(10).to_markdown())

            # Success patterns
            f.write("\n\n## Success Patterns\n\n")
            patterns = self.analyze_successful_app_patterns(apps_data)
            for key, value in patterns.items():
                f.write(f"- **{key}**: {value}\n")

        print(f"Report generated: {report_path}")
        return str(report_path)


def main():
    """Example usage"""
    analyzer = TrendAnalyzer()

    # Example data
    sample_data = [
        {'app_id': '1', 'name': 'App1', 'category': 'Games', 'revenue': 100000, 'downloads': 50000, 'rating': 4.5},
        {'app_id': '2', 'name': 'App2', 'category': 'Games', 'revenue': 80000, 'downloads': 60000, 'rating': 4.3},
        {'app_id': '3', 'name': 'App3', 'category': 'Finance', 'revenue': 120000, 'downloads': 30000, 'rating': 4.7},
    ]

    # Analyze
    category_perf = analyzer.analyze_category_performance(sample_data)
    print("Category Performance:")
    print(category_perf)

    patterns = analyzer.analyze_successful_app_patterns(sample_data)
    print("\nSuccess Patterns:")
    print(patterns)


if __name__ == "__main__":
    main()
