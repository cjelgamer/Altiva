#!/usr/bin/env python3
"""
Test del reloj peruano y verificación de horas
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.components.peru_clock import (
    peru_clock_component,
    get_peru_datetime,
    get_peru_midnight,
    get_utc_equivalent,
    format_peru_time,
    is_new_day_in_peru,
)


def test_peru_clock():
    """Test all Peru clock functions"""

    print("🕐 Testing Peru Clock Component")
    print("=" * 50)

    # Test current Peru time
    print("1️⃣ Current Peru Time:")
    peru_time = get_peru_datetime()
    print(f"   Peru datetime: {peru_time}")
    print(f"   Formatted: {format_peru_time(peru_time)}")

    # Test midnight calculation
    print("\n2️⃣ Peru Midnight:")
    peru_midnight = get_peru_midnight()
    print(f"   Peru midnight: {peru_midnight}")

    # Test UTC conversion
    print("\n3️⃣ UTC Conversion:")
    utc_equivalent = get_utc_equivalent(peru_midnight)
    print(f"   Peru midnight: {peru_midnight}")
    print(f"   UTC equivalent: {utc_equivalent}")
    print(f"   Time difference: {utc_equivalent - peru_midnight}")

    # Test new day detection
    print("\n4️⃣ New Day Detection:")
    from datetime import datetime, timedelta
    from pytz import timezone

    peru_tz = timezone("America/Lima")

    # Test with yesterday's timestamp
    yesterday = peru_midnight - timedelta(hours=1)
    print(f"   Yesterday timestamp: {yesterday}")
    print(f"   Is new day? {is_new_day_in_peru(yesterday)}")

    # Test with today's timestamp
    today = peru_midnight + timedelta(hours=1)
    print(f"   Today timestamp: {today}")
    print(f"   Is new day? {is_new_day_in_peru(today)}")

    # Test timezones
    print("\n5️⃣ Timezone Verification:")
    print(f"   Peru timezone: {peru_time.tzinfo}")
    print(f"   UTC timezone: {utc_equivalent.tzinfo}")

    # Manual verification
    print("\n🔍 Manual Verification:")
    import pytz

    utc_now = datetime.now(pytz.UTC)
    peru_now_manual = utc_now.astimezone(pytz.timezone("America/Lima"))

    print(f"   UTC now: {utc_now}")
    print(f"   Peru now (manual): {peru_now_manual}")
    print(f"   Peru now (function): {peru_time}")
    print(f"   Difference: {peru_time - peru_now_manual}")

    if abs((peru_time - peru_now_manual).total_seconds()) < 60:
        print("   ✅ Time calculations are correct!")
    else:
        print("   ❌ Time calculations may have issues")

    print(f"\n📋 Expected Behavior:")
    print(f"   - Day resets at 00:00:00 Peru time (GMT-5)")
    print(f"   - UTC equivalent is 05:00:00 next day")
    print(f"   - This ensures users see Peru time in the interface")

    print(f"\n🎯 Component Display:")
    print(f"   The clock will show in top-left corner with:")
    print(f"   - Peru time (HH:MM:SS)")
    print(f"   - Day of week in Spanish")
    print(f"   - Date in DD/MM/YYYY format")
    print(f"   - Blue background with Peru flag emoji")


if __name__ == "__main__":
    test_peru_clock()
