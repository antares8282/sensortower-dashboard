"""
SensorTower API Client
Handles all API requests with caching to minimize API usage

Verified working endpoints (Feb 2025):
- GET /v1/ios/ranking          - Top charts (returns app IDs)
- GET /v1/ios/apps             - App metadata
- GET /v1/ios/sales_report_estimates    - Download/revenue estimates
- GET /v1/android/ranking      - Android top charts
- GET /v1/android/apps         - Android app metadata
- GET /v1/android/sales_report_estimates - Android download/revenue
- GET /v1/unified/apps         - Cross-platform app lookup
"""
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

load_dotenv()


# Chart type constants
CHART_TOP_FREE = "topfreeapplications"
CHART_TOP_PAID = "toppaidapplications"
CHART_TOP_GROSSING = "topgrossingapplications"


class SensorTowerClient:
    """API client with smart caching to minimize requests"""

    BASE_URL = "https://api.sensortower.com/v1"
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    CACHE_DIR = _PROJECT_ROOT / "data" / "raw" / "cache"

    def __init__(
        self,
        api_token: Optional[str] = None,
        cache_ttl_hours: int = 168,  # 1 week default
        rate_limit_delay: float = 1.0
    ):
        self.api_token = api_token or os.getenv('SENSORTOWER_API_TOKEN')
        if not self.api_token:
            raise ValueError("API token required. Set SENSORTOWER_API_TOKEN env variable")

        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.request_count = 0

        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        self.usage_log_file = self._PROJECT_ROOT / "data" / "api_usage_log.json"
        self._load_usage_log()

    # ---- Usage tracking ----

    def _load_usage_log(self):
        if self.usage_log_file.exists():
            with open(self.usage_log_file, 'r') as f:
                self.usage_log = json.load(f)
        else:
            self.usage_log = {"requests": [], "monthly_counts": {}}

    def _save_usage_log(self):
        with open(self.usage_log_file, 'w') as f:
            json.dump(self.usage_log, f, indent=2)

    def _log_request(self, endpoint: str):
        timestamp = datetime.now().isoformat()
        month_key = datetime.now().strftime("%Y-%m")

        self.usage_log["requests"].append({
            "timestamp": timestamp,
            "endpoint": endpoint
        })

        if month_key not in self.usage_log["monthly_counts"]:
            self.usage_log["monthly_counts"][month_key] = 0
        self.usage_log["monthly_counts"][month_key] += 1

        self._save_usage_log()
        self.request_count += 1

    def get_monthly_usage(self, month: Optional[str] = None) -> int:
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        return self.usage_log["monthly_counts"].get(month, 0)

    # ---- Caching ----

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        cache_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        return self.CACHE_DIR / f"{cache_key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - modified_time < self.cache_ttl

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        cache_path = self._get_cache_path(cache_key)
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r') as f:
                cached = json.load(f)
                print(f"  [cache hit] {cache_key[:8]}...")
                return cached["data"]
        return None

    def _save_to_cache(self, cache_key: str, data: Any):
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, 'w') as f:
            json.dump({
                "cached_at": datetime.now().isoformat(),
                "data": data
            }, f, indent=2)

    # ---- Core request method ----

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Any:
        params = params or {}
        cache_key = self._get_cache_key(endpoint, params)

        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        usage = self.get_monthly_usage()
        print(f"  [API call] {endpoint} (monthly usage: {usage})")

        if usage >= 2000:
            print(f"  WARNING: Monthly usage is {usage}/2500!")

        response = requests.get(url, headers=headers, params=params, timeout=30)
        self.last_request_time = time.time()
        response.raise_for_status()
        data = response.json()

        self._log_request(endpoint)
        self._save_to_cache(cache_key, data)

        return data

    # ---- Rankings / Top Charts ----

    def get_top_apps(
        self,
        category: str = "6014",
        chart_type: str = CHART_TOP_FREE,
        date: str = None,
        country: str = "US",
        device: str = "ios",
        limit: Optional[int] = None,
        use_cache: bool = True,
        resolve_details: bool = True
    ) -> Dict:
        """
        Get top apps from a chart.

        Args:
            category: Category ID (e.g., '6014' for Games on iOS, 'GAME' for Android)
            chart_type: 'topfreeapplications', 'toppaidapplications', 'topgrossingapplications'
            date: Date string 'YYYY-MM-DD' (defaults to today)
            country: Country code
            device: 'ios' or 'android'
            limit: Limit results (applied after fetch)
            use_cache: Use cache
            resolve_details: If True, also fetches app names/details (costs 1 extra API call)

        Returns:
            Dict with 'ranking' (list of app IDs) and optionally 'apps' (list of app details)
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "category": category,
            "chart_type": chart_type,
            "date": date,
            "country": country,
        }

        endpoint = f"{device}/ranking"
        data = self._make_request(endpoint, params, use_cache)

        app_ids = data.get("ranking", [])
        if limit:
            app_ids = app_ids[:limit]

        result = {
            "category": data.get("category"),
            "chart_type": data.get("chart_type"),
            "country": data.get("country"),
            "date": data.get("date"),
            "ranking": app_ids,
        }

        if resolve_details and app_ids:
            apps = self.get_app_details(app_ids[:limit or 100], device=device, use_cache=use_cache)
            result["apps"] = apps

        return result

    # ---- App Details ----

    def get_app_details(
        self,
        app_ids: List,
        device: str = "ios",
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get details for multiple apps.

        Args:
            app_ids: List of app IDs (iTunes IDs for iOS, package names for Android)
            device: 'ios' or 'android'
            use_cache: Use cache

        Returns:
            List of app detail dicts
        """
        ids_str = ",".join(str(x) for x in app_ids)
        params = {"app_ids": ids_str}
        endpoint = f"{device}/apps"

        data = self._make_request(endpoint, params, use_cache)
        return data.get("apps", [])

    # ---- Sales / Revenue / Download Estimates ----

    def get_sales_estimates(
        self,
        app_ids: List = None,
        publisher_ids: List = None,
        device: str = "ios",
        date_granularity: str = "monthly",
        start_date: str = None,
        end_date: str = None,
        country: str = None,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get download and revenue estimates.

        Args:
            app_ids: List of app IDs
            publisher_ids: List of publisher IDs (alternative to app_ids)
            device: 'ios' or 'android'
            date_granularity: 'daily', 'weekly', 'monthly'
            start_date: 'YYYY-MM-DD'
            end_date: 'YYYY-MM-DD'
            country: Optional country filter (omit for all countries)
            use_cache: Use cache

        Returns:
            List of estimate records. Keys:
            - aid: app ID, cc: country, d: date
            - iOS: iu (units/downloads), ir (revenue in cents)
            - Android: u (units/downloads), r (revenue in cents)
        """
        if not app_ids and not publisher_ids:
            raise ValueError("Either app_ids or publisher_ids required")

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        params = {
            "date_granularity": date_granularity,
            "start_date": start_date,
            "end_date": end_date,
        }

        if app_ids:
            params["app_ids"] = ",".join(str(x) for x in app_ids)
        if publisher_ids:
            params["publisher_ids"] = ",".join(str(x) for x in publisher_ids)
        if country:
            params["country"] = country

        endpoint = f"{device}/sales_report_estimates"
        return self._make_request(endpoint, params, use_cache)

    # ---- Unified / Cross-platform ----

    def get_unified_app(
        self,
        app_ids: List,
        app_id_type: str = "itunes",
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Look up unified (cross-platform) app info.

        Args:
            app_ids: List of app IDs
            app_id_type: 'itunes', 'android', 'unified', 'cohorts'
            use_cache: Use cache

        Returns:
            List of unified app records with cross-platform mappings
        """
        params = {
            "app_ids": ",".join(str(x) for x in app_ids),
            "app_id_type": app_id_type,
        }
        endpoint = "unified/apps"
        data = self._make_request(endpoint, params, use_cache)
        return data.get("apps", [])

    # ---- Cache management ----

    def clear_old_cache(self, days: int = 30):
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        for cache_file in self.CACHE_DIR.glob("*.json"):
            modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if modified_time < cutoff:
                cache_file.unlink()
                removed += 1
        print(f"Removed {removed} old cache files")
        return removed


def main():
    """Quick test of the client"""
    client = SensorTowerClient(cache_ttl_hours=168)
    print(f"Current month usage: {client.get_monthly_usage()} requests\n")

    print("Fetching top free games (US)...")
    result = client.get_top_apps(
        category="6014",
        chart_type=CHART_TOP_FREE,
        country="US",
        limit=10,
        resolve_details=True
    )

    print(f"\nTop 10 free games (US):")
    for i, app in enumerate(result.get("apps", []), 1):
        print(f"  {i}. {app['name']} by {app['publisher_name']}")

    print(f"\nTotal monthly usage: {client.get_monthly_usage()} requests")


if __name__ == "__main__":
    main()
