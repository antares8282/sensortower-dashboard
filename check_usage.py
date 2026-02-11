"""
API Usage Monitor
Quick script to check your current API usage
"""
import json
from pathlib import Path
from datetime import datetime


def main():
    usage_file = Path("data/api_usage_log.json")

    if not usage_file.exists():
        print("No API usage data found yet.")
        print("Run quickstart.py or make some API calls first.")
        return

    with open(usage_file, 'r') as f:
        usage_log = json.load(f)

    current_month = datetime.now().strftime("%Y-%m")
    current_usage = usage_log["monthly_counts"].get(current_month, 0)

    # Limits
    soft_limit = 2000
    hard_limit = 3000

    print("=" * 60)
    print("SensorTower API Usage Monitor")
    print("=" * 60)
    print(f"\nCurrent Month: {current_month}")
    print(f"Requests Made: {current_usage}")
    print(f"Soft Limit:    {soft_limit}")
    print(f"Hard Limit:    {hard_limit}")
    print(f"\nRemaining:     {hard_limit - current_usage}")
    print(f"Usage:         {(current_usage/soft_limit)*100:.1f}% of soft limit")

    # Status indicator
    if current_usage >= hard_limit:
        status = "🔴 CRITICAL - At/Over Hard Limit!"
    elif current_usage >= soft_limit:
        status = "🟡 WARNING - Over Soft Limit"
    elif current_usage >= soft_limit * 0.8:
        status = "🟠 CAUTION - Approaching Limit"
    else:
        status = "🟢 GOOD - Within Safe Range"

    print(f"\nStatus: {status}")

    # Recent requests
    recent = usage_log["requests"][-10:]
    if recent:
        print("\n" + "=" * 60)
        print("Recent Requests (last 10):")
        print("=" * 60)
        for req in recent:
            timestamp = datetime.fromisoformat(req["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            endpoint = req["endpoint"]
            print(f"{timestamp} | {endpoint}")

    # Monthly breakdown
    print("\n" + "=" * 60)
    print("Monthly Usage History:")
    print("=" * 60)
    for month, count in sorted(usage_log["monthly_counts"].items()):
        indicator = "←" if month == current_month else ""
        print(f"{month}: {count:4d} requests {indicator}")

    print("=" * 60)


if __name__ == "__main__":
    main()
